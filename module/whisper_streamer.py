import threading
import queue
import subprocess
import time
import numpy as np
import io
import os
import soundfile as sf

from whisper.whisper_online import *
import argparse
import logging

# Global configuration
INTERFACE_NAME = "CABLE Output(VB-Audio Virtual Cable)"
SAMPLING_RATE = 16000
MIN_CHUNK_SIZE = 1  # in seconds

logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser()

# options from whisper_online
add_shared_args(parser)

# 커스텀 옵션
custom_args = ['--model', 'large-v3', '--lan', 'zh']
args = parser.parse_args(custom_args)

set_logging(args,logger,other="")

# setting whisper object by args 
size = args.model
language = args.lan
asr, online = asr_factory(args)
min_chunk = args.min_chunk_size
print(size, language, min_chunk)


class ServerProcessorThread(threading.Thread):
    def __init__(self, data_queue, online_asr_proc, min_chunk):
        super().__init__()
        self.data_queue = data_queue
        self.online_asr_proc = online_asr_proc
        self.min_chunk = min_chunk
        self.running = True
        self.last_end = None
        self.is_first = True

    def receive_audio_chunk(self):
        """Receive audio data from the queue."""
        out = []
        min_limit = self.min_chunk * SAMPLING_RATE
        while sum(len(x) for x in out) < min_limit:
            try:
                raw_bytes = self.data_queue.get(timeout=1)
                if raw_bytes is None:  # Signal to stop processing
                    return None
                audio = sf.SoundFile(io.BytesIO(raw_bytes), channels=1, samplerate=SAMPLING_RATE, subtype="PCM_16", format="RAW")
                audio_data = np.array(audio.read(dtype="float32"))
                out.append(audio_data)
            except queue.Empty:
                continue
        if not out:
            return None
        combined_audio = np.concatenate(out)
        if self.is_first and len(combined_audio) < min_limit:
            return None
        self.is_first = False
        return combined_audio

    def format_output_transcript(self, result):
        """Format Whisper output."""
        if result[0] is not None:
            beg, end = result[0] * 1000, result[1] * 1000
            if self.last_end is not None:
                beg = max(beg, self.last_end)
            self.last_end = end
            transcript = f"{beg:.0f} {end:.0f} {result[2]}"
            print(transcript)
            return transcript
        return None

    def run(self):
        """Run the server processor thread."""
        self.online_asr_proc.init()
        while self.running:
            audio_chunk = self.receive_audio_chunk()
            if audio_chunk is None:
                break
            self.online_asr_proc.insert_audio_chunk(audio_chunk)
            result = self.online_asr_proc.process_iter()
            formatted_result = self.format_output_transcript(result)
            if formatted_result:
                print(f"Server: Processed result: {formatted_result}")

    def stop(self):
        """Stop the server processor thread."""
        self.running = False
        self.data_queue.put(None)  # Send stop signal


class FFMpegClientThread(threading.Thread):
    def __init__(self, data_queue, ffmpeg_command):
        super().__init__()
        self.data_queue = data_queue
        self.running = True
        self.ffmpeg_command = ffmpeg_command

    def run(self):
        """Run the client thread to read audio data from ffmpeg."""
        process = subprocess.Popen(
            self.ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=10**6,
        )

        try:
            while self.running:
                # 16kHz, 16-bit PCM에서 약 0.5초 분량 사이즈 조절해보면서 테스트하면 좋을듯
                raw_bytes = process.stdout.read(32000) 
                if not raw_bytes:
                    break
                self.data_queue.put(raw_bytes)
        except Exception as e:
            print(f"Error reading from ffmpeg: {e}")
        finally:
            process.terminate()
            process.wait()

    def stop(self):
        """Stop the client thread."""
        self.running = False


# Global variables for threads
client_thread = None
server_thread = None
data_queue = queue.Queue()


def whisper_start():
    """Start the Whisper client and server threads."""
    global client_thread, server_thread

    # ffmpeg command to read audio from CABLE Output
    ffmpeg_command = [
        "ffmpeg",
        "-f", "dshow",
        "-i", "audio=" + str(INTERFACE_NAME),
        "-ar", str(SAMPLING_RATE),
        "-ac", "1",
        "-f", "s16le",
        "pipe:1",
    ]

    server_thread = ServerProcessorThread(data_queue, online, args.min_chunk_size)
    client_thread = FFMpegClientThread(data_queue, ffmpeg_command)

    server_thread.start()
    client_thread.start()
    print("Whisper processing started.")


def whisper_stop():
    """Stop the Whisper client and server threads."""
    global client_thread, server_thread

    if client_thread and server_thread:
        print("Stopping Whisper processing...")
        client_thread.stop()
        server_thread.stop()

        client_thread.join()
        server_thread.join()
        print("Whisper processing stopped.")
    else:
        print("Whisper is not running.")


if __name__ == "__main__":
    try:
        whisper_start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        whisper_stop()
