import atexit
import os

from google import genai
from google.genai import types

from config.settings import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_LOOKUP_MODEL, USER_NAME, MILO_SYSTEM_INSTRUCTION, SHOW_FACE
from interfaces.face import show_face, hide_face
from interfaces.text_io import milo_speak, milo_speak_stream, get_user_input, ask_yes_no
from skills.open_website import try_handle_open_site
from skills.search import try_handle_search
from skills.time_date import try_handle_time_date

EXIT_WORDS = {"exit", "quit", "bye", "goodbye"}


def run_skill(name: str, skill, user_input: str) -> str | None:
    try:
        return skill(user_input)
    except KeyboardInterrupt:
        return "Okay, never mind!"
    except Exception as e:
        if os.getenv("MILO_DEBUG") == "1":
            print(f"[debug] skill '{name}' crashed: {type(e).__name__}: {e}")
        return None


def try_skills(skills: list, user_input: str) -> str | None:
    for name, skill in skills:
        reply = run_skill(name, skill, user_input)
        if reply is not None:
            return reply
    return None


def remember_skill_action(notes: list, user_input: str, reply: str) -> None:
    notes.append(f'The user said "{user_input}" and you handled it yourself, replying "{reply}".')
    del notes[:-3]


def add_skill_context(user_input: str, notes: list) -> str:
    if not notes:
        return user_input
    background = " ".join(notes)
    return f"[Background, only mention if relevant: {background}]\n\n{user_input}"


def run():
    client = genai.Client(api_key=GEMINI_API_KEY)

    chat = client.chats.create(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(system_instruction=MILO_SYSTEM_INSTRUCTION),
    )

    if SHOW_FACE:
        face_process = show_face()
        atexit.register(hide_face, face_process)

    skills = [
        ("time_date", lambda text: try_handle_time_date(text)),
        ("search", lambda text: try_handle_search(text)),
        ("open_website", lambda text: try_handle_open_site(text, client, GEMINI_LOOKUP_MODEL, ask_yes_no)),
    ]

    skill_notes = []

    try:
        milo_speak_stream(
            chat,
            f"Greet the user named {USER_NAME} in a friendly, playful way, "
            f"introducing yourself briefly as Milo.",
        )
    except Exception as e:
        milo_speak(f"Hey {USER_NAME}, I'm Milo! (had trouble reaching my brain just now: {e})")

    while True:
        try:
            user_input = get_user_input(USER_NAME)
        except (EOFError, KeyboardInterrupt):
            milo_speak("Alright, catch you later!")
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_WORDS:
            milo_speak("See you soon! Take care.")
            break

        skill_reply = try_skills(skills, user_input)
        if skill_reply is not None:
            milo_speak(skill_reply)
            remember_skill_action(skill_notes, user_input, skill_reply)
            continue

        try:
            milo_speak_stream(chat, add_skill_context(user_input, skill_notes))
            skill_notes.clear()
        except KeyboardInterrupt:
            print()
            milo_speak("Okay, I'll stop talking!")
        except Exception as e:
            milo_speak(f"Hmm, I ran into an issue talking to my brain: {e}")