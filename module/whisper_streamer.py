import threading
import subprocess
import time
import numpy as np
import io
import os
import sys
from module.sentence_completion import SentenceBuffer
import soundfile

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from module.debugger import update_debugger_text
from module.translator import update_translator_text

from whisper.whisper_online import *
import argparse
import logging
import socket
import whisper.line_packet as line_packet

# Global configuration
INTERFACE_NAME = "CABLE Output(VB-Audio Virtual Cable)"
SAMPLING_RATE = 16000
TMP_HOST = "localhost"
TMP_PORT = 43007

logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser()

# options from whisper_online
add_shared_args(parser)

# 커스텀 옵션
custom_args = ['--model', 'large-v3', '--lan', 'zh', '--min-chunk-size', '2']
args = parser.parse_args(custom_args)

set_logging(args, logger, other="")

# Whisper model initialization
size = args.model
language = args.lan
asr, online = asr_factory(args)
min_chunk = args.min_chunk_size
print(size, language, min_chunk)


class Connection:
    '''it wraps conn object'''
    PACKET_SIZE = 32000*5*60 # 5 minutes # was: 65536

    def __init__(self, conn):
        self.conn = conn
        self.last_line = ""

        self.conn.setblocking(True)

    def send(self, line):
        '''it doesn't send the same line twice, because it was problematic in online-text-flow-events'''
        if line == self.last_line:
            return
        line_packet.send_one_line(self.conn, line)
        self.last_line = line

    def receive_lines(self):
        in_line = line_packet.receive_lines(self.conn)
        return in_line

    def non_blocking_receive_audio(self):
        try:
            r = self.conn.recv(self.PACKET_SIZE)
            return r
        except ConnectionResetError:
            return None

class ServerProcessorThread(threading.Thread):
    """Server processor for handling audio chunks and Whisper processing."""

    def __init__(self, online_asr_proc, min_chunk):
        super().__init__()
        self.online_asr_proc = online_asr_proc
        self.min_chunk = min_chunk
        self.running = True
        self.last_end = None
        self.is_first = True
        self.conn = None
        self.addr = None
        self.sentence_buffer = SentenceBuffer()

    def run(self):
        """Start the server and process incoming audio data."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((TMP_HOST, TMP_PORT))
            server_socket.listen(1)
            logger.info(f"Listening on {TMP_HOST}:{TMP_PORT}")

            self.conn, self.addr = server_socket.accept()
            logger.info(f"Connected to client at {self.addr}")

            self.connection = Connection(self.conn)
            self.online_asr_proc.init()

            while self.running:
                a = self.receive_audio_chunk()
                if a is None:
                    break
                self.online_asr_proc.insert_audio_chunk(a)
                o = online.process_iter()
                self.send_result(o)

            logger.info(f"Connection with {self.addr} closed")

    def receive_audio_chunk(self):
        # receive all audio that is available by this time
        # blocks operation if less than self.min_chunk seconds is available
        # unblocks if connection is closed or a chunk is available
        out = []
        minlimit = self.min_chunk*SAMPLING_RATE
        while sum(len(x) for x in out) < minlimit:
            raw_bytes = self.connection.non_blocking_receive_audio()
            if not raw_bytes:
                break
#            print("received audio:",len(raw_bytes), "bytes", raw_bytes[:10])
            sf = soundfile.SoundFile(io.BytesIO(raw_bytes), channels=1,endian="LITTLE",samplerate=SAMPLING_RATE, subtype="PCM_16",format="RAW")
            audio, _ = librosa.load(sf,sr=SAMPLING_RATE,dtype=np.float32)
            out.append(audio)
        if not out:
            return None
        conc = np.concatenate(out)
        if self.is_first and len(conc) < minlimit:
            return None
        self.is_first = False
        return np.concatenate(out)

    def format_output_transcript(self,o):
        # output format in stdout is like:
        # 0 1720 Takhle to je
        # - the first two words are:
        #    - beg and end timestamp of the text segment, as estimated by Whisper model. The timestamps are not accurate, but they're useful anyway
        # - the next words: segment transcript

        # This function differs from whisper_online.output_transcript in the following:
        # succeeding [beg,end] intervals are not overlapping because ELITR protocol (implemented in online-text-flow events) requires it.
        # Therefore, beg, is max of previous end and current beg outputed by Whisper.
        # Usually it differs negligibly, by appx 20 ms.

        if o[0] is not None:
            beg, end = o[0]*1000,o[1]*1000
            if self.last_end is not None:
                beg = max(beg, self.last_end)

            self.last_end = end
            print("%1.0f %1.0f %s" % (beg,end,o[2]),flush=True,file=sys.stderr)
            # return "%1.0f %1.0f %s" % (beg,end,o[2])
            return o[2]
        else:
            logger.debug("No text in this segment")
            return None

    def send_result(self, o):
        msg = self.format_output_transcript(o)
        if msg is not None:
            update_debugger_text(msg)
            # update_sentence_checker(msg)
            comp_msg = self.sentence_buffer.is_sentence_complete(msg)
            if comp_msg:
                update_translator_text(comp_msg)



class FFMpegClientThread(threading.Thread):
    """FFmpeg client to send audio data over TCP."""

    def __init__(self):
        super().__init__()
        self.running = True
        self.process = None

    def run(self):
        """Run FFmpeg process to send audio data."""
        ffmpeg_command = [
            "ffmpeg",
            "-f", "dshow",
            "-i", f"audio={INTERFACE_NAME}",
            "-ar", str(SAMPLING_RATE),
            "-ac", "1",
            "-f", "s16le",
            f"tcp://{TMP_HOST}:{TMP_PORT}",
        ]
        self.process = subprocess.Popen(
            ffmpeg_command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def stop(self):
        """Stop FFmpeg process."""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()


def whisper_start():
    """Start the server and FFmpeg client."""
    print(args)
    server_thread = ServerProcessorThread(online, args.min_chunk_size)
    server_thread.daemon = True
    client_thread = FFMpegClientThread()
    client_thread.daemon = True

    server_thread.start()
    client_thread.start()

    return server_thread, client_thread


def whisper_stop(server_thread, client_thread):
    """Stop the server and FFmpeg client."""
    server_thread.running = False
    client_thread.stop()
    server_thread.join()
    client_thread.join()
    logger.info("Whisper processing stopped.")

