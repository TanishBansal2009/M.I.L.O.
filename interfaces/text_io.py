import os
import time


def milo_speak(text: str) -> None:
    print(f"Milo : {text}")


def milo_speak_stream(chat, prompt: str) -> str:
    print("Milo : ", end="", flush=True)
    chunks = []
    start = time.perf_counter()
    first_chunk_time = None

    for chunk in chat.send_message_stream(prompt):
        if chunk.text:
            if first_chunk_time is None:
                first_chunk_time = time.perf_counter() - start
            print(chunk.text, end="", flush=True)
            chunks.append(chunk.text)

    print()
    total_time = time.perf_counter() - start

    if os.getenv("MILO_DEBUG_TIMING") == "1" and first_chunk_time is not None:
        print(f"[debug] time to first chunk: {first_chunk_time:.2f}s, total: {total_time:.2f}s")

    return "".join(chunks)


def get_user_input(user_name: str) -> str:
    return input(f"{user_name} : ").strip()

def ask_yes_no(question: str) -> bool:
    try:
        answer = input(f"Milo : {question} (y/n) ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return answer in ("y", "yes", "yeah", "yep", "sure", "ok", "okay")