# import time
# from threading import Lock
# from module.translator import update_translator_text

# # 각각 사용할 곳에서 호출하면 스레드가 생성됨
# # 타임아웃이 되면 업데이트
# # 그냥 이 스레드에 계속해서 문자열을 누적시키고 타임아웃은 따로 체크 
# def create_sentence_checker(timeout=2.0, interval=0.1):
#     last_text = None
#     last_update_time = 0
#     lock = Lock()
#     accumulated_text = []  # 누적된 텍스트 저장

#     def _checker_thread():
#         acc_interval = 0
#         while True:
#             time.sleep(interval)
#             acc_interval += interval   # 현재시간 체크하는 것 보다 정확하지 않지만 그냥쓰셈

#             if (acc_interval >= timeout):
#                 with lock:
#                     update_translator_text("".join(accumulated_text))
#                     accumulated_text.clear()
#                 acc_interval = 0

#     def is_custom_completion(current_sentence):
#         """
#         사용자 정의 조건을 확인
#         :param current_sentence: 현재 누적된 문장
#         :return: 조건이 충족되면 True, 아니면 False
#         """
#         return False

#     def is_sentence_complete(new_text=None):
#         """
#         문장이 완성되었는지 확인
#         :param new_text: 새로 입력된 텍스트 (None이면 업데이트 없음)
#         :return: 완성된 문장 또는 None
#         """
#         nonlocal last_text, last_update_time
#         current_time = time.time()

#         with lock:
#             # 새로운 텍스트 업데이트 처리
#             # "", None 는 무시
#             if new_text and (new_text != last_text):
#                 last_text = new_text
#                 last_update_time = current_time
#                 accumulated_text.append(new_text)

#             # 현재 문장
#             current_sentence = "".join(accumulated_text)

#             # 각 조건을 순차적으로 확인
#             if is_timeout_complete(current_time) or is_punctuation_complete(current_sentence) or is_custom_completion(current_sentence):
#                 accumulated_text.clear()
#                 return current_sentence

#         return None  # 아직 문장이 완성되지 않음

#     return is_sentence_complete
