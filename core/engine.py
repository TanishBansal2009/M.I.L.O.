import os

from google import genai
from google.genai import types

from config.settings import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_LOOKUP_MODEL, USER_NAME, MILO_SYSTEM_INSTRUCTION
from skills.memory import Memory, try_handle_memory
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
    """Skills answer without the chat model, so the chat never sees those
    messages. We keep a short note and attach it to the next chat message."""
    notes.append(f'The user said "{user_input}" and you handled it yourself, replying "{reply}".')
    del notes[:-3]


def add_skill_context(user_input: str, notes: list) -> str:
    if not notes:
        return user_input
    background = " ".join(notes)
    return f"[Background, only mention if relevant: {background}]\n\n{user_input}"


class Milo:
    def __init__(self, ui):
        self.ui = ui
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.memory = Memory()
        self.memory_version = self.memory.version
        self.chat = self.client.chats.create(model=GEMINI_MODEL, config=self.chat_config())
        self.skill_notes = []
        self.skills = [
            ("time_date", lambda text: try_handle_time_date(text)),
            ("memory", lambda text: try_handle_memory(text, self.memory, ui.ask_yes_no)),
            ("search", lambda text: try_handle_search(text)),
            ("open_website", lambda text: try_handle_open_site(text, self.client, GEMINI_LOOKUP_MODEL, ui.ask_yes_no)),
        ]

    def chat_config(self):
        instruction = MILO_SYSTEM_INSTRUCTION + self.memory.as_prompt()
        return types.GenerateContentConfig(system_instruction=instruction)

    def refresh_chat_if_memory_changed(self) -> None:
        if self.memory.version == self.memory_version:
            return
        self.memory_version = self.memory.version
        try:
            self.chat = self.client.chats.create(
                model=GEMINI_MODEL,
                config=self.chat_config(),
                history=self.chat.get_history(curated=True),
            )
        except Exception as e:
            if os.getenv("MILO_DEBUG") == "1":
                print(f"[debug] could not refresh the chat after a memory change: {type(e).__name__}: {e}")

    def stream_reply(self, prompt: str):
        for chunk in self.chat.send_message_stream(prompt):
            if chunk.text:
                yield chunk.text

    def greet(self) -> None:
        prompt = (
            f"Greet the user named {USER_NAME} in a friendly, playful way, "
            f"introducing yourself briefly as Milo."
        )
        try:
            self.ui.milo_speak_stream(self.stream_reply(prompt))
        except Exception as e:
            self.ui.milo_speak(f"Hey {USER_NAME}, I'm Milo! (had trouble reaching my brain just now: {e})")

    def handle(self, user_input: str) -> None:
        skill_reply = try_skills(self.skills, user_input)
        if skill_reply is not None:
            self.ui.milo_speak(skill_reply)
            remember_skill_action(self.skill_notes, user_input, skill_reply)
            self.refresh_chat_if_memory_changed()
            return

        try:
            prompt = add_skill_context(user_input, self.skill_notes)
            self.ui.milo_speak_stream(self.stream_reply(prompt))
            self.skill_notes.clear()
        except KeyboardInterrupt:
            self.ui.milo_speak("Okay, I'll stop talking!")
        except Exception as e:
            self.ui.milo_speak(f"Hmm, I ran into an issue talking to my brain: {e}")


def run(ui) -> None:
    milo = Milo(ui)
    milo.greet()

    while True:
        try:
            user_input = ui.get_user_input(USER_NAME)
        except (EOFError, KeyboardInterrupt):
            ui.milo_speak("Alright, catch you later!")
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_WORDS:
            ui.milo_speak("See you soon! Take care.")
            break

        milo.handle(user_input)