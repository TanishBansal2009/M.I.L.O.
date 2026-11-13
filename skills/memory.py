import json
import os
from datetime import date
from pathlib import Path

from skills.common import POLITE_PREFIXES

MEMORY_FILE = Path(__file__).resolve().parent.parent / "data" / "memory.json"
MAX_FACTS = 50
MAX_FACT_CHARS = 200

REMEMBER_TRIGGERS = (
    "remember that ", "remember ", "note that ",
    "dont forget that ", "don't forget that ", "keep in mind that ",
)
FORGET_TRIGGERS = ("forget that ", "forget about ", "forget ")

LIST_PHRASES = (
    "what do you remember", "what do you remember about me", "what do you know about me",
    "show my memories", "show memories", "show memory", "show your memory",
    "list my memories", "what is in your memory", "whats in your memory",
)
CLEAR_PHRASES = (
    "forget everything", "forget all", "forget all memories",
    "forget everything you know about me", "clear your memory", "clear memory",
    "wipe your memory", "delete all memories", "delete my memories",
)

NOT_A_FACT_WORDS = ("when", "how", "what", "why", "who", "where", "which", "if", "you", "me", "it", "this")
FILLER_WORDS = ("my", "the", "a", "an", "of", "is", "are", "to", "that", "about", "i", "me", "and", "on", "in", "it")
NOT_A_FORGET_WORDS = ("it", "this", "them", "me", "you", "i", "we", "what", "how", "why", "when", "who", "where")


class Memory:
    def __init__(self, path: Path = MEMORY_FILE):
        self.path = path
        self.version = 0
        self.facts = self.load()

    def load(self) -> list:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, OSError):
            try:
                self.path.replace(self.path.with_suffix(".corrupt.json"))
            except OSError:
                pass
            return []

        facts = []
        for item in data if isinstance(data, list) else []:
            if isinstance(item, dict) and isinstance(item.get("fact"), str):
                facts.append({"fact": item["fact"], "saved": str(item.get("saved", ""))})
        return facts[:MAX_FACTS]

    def save(self) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temp = self.path.with_suffix(".tmp")
            temp.write_text(json.dumps(self.facts, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(temp, self.path)
            return True
        except OSError:
            return False

    def add(self, fact: str) -> str:
        if any(f["fact"].lower() == fact.lower() for f in self.facts):
            return "I already remember that."
        if len(self.facts) >= MAX_FACTS:
            return f"My memory is full ({MAX_FACTS} things). Ask me to forget something first."

        self.facts.append({"fact": fact, "saved": date.today().isoformat()})
        self.version += 1

        if not self.save():
            return f"I'll remember that for now, but I couldn't save it to disk: {fact}"
        return f"Got it, I'll remember that: {fact}"

    def find(self, query: str) -> list:
        words = [w for w in query.lower().split() if w not in FILLER_WORDS]
        if not words:
            return []
        return [i for i, f in enumerate(self.facts) if all(w in f["fact"].lower() for w in words)]

    def remove(self, index: int) -> str:
        fact = self.facts.pop(index)["fact"]
        self.version += 1
        self.save()
        return f"Done, I forgot: {fact}"

    def clear(self) -> str:
        self.facts = []
        self.version += 1
        self.save()
        return "Done, my memory is empty."

    def describe(self) -> str:
        if not self.facts:
            return "I don't have anything saved yet. Try 'remember that ...'."
        lines = [f"  {i}. {f['fact']}" for i, f in enumerate(self.facts, 1)]
        return "Here's what I remember:\n" + "\n".join(lines)

    def as_prompt(self) -> str:
        if not self.facts:
            return ""
        lines = []
        for f in self.facts:
            saved = f" (saved on {f['saved']})" if f["saved"] else ""
            lines.append(f"- {f['fact']}{saved}")
        today = date.today().strftime("%A, %d %B %Y")
        return (
            f"\n\nToday is {today}. The user asked you to remember these things. "
            "Use them naturally when they are relevant, and do not list them unless asked:\n"
            + "\n".join(lines)
        )


def read_command(user_input: str) -> tuple[str, str]:
    """Returns the text (original capital letters kept) and a lowercase copy,
    both without polite starts like 'please' and without ? ! . at the end."""
    text = " ".join(user_input.replace("\u2019", "'").strip().split()).rstrip(" ?!.")
    lowered = text.lower()

    changed = True
    while changed:
        changed = False
        for prefix in POLITE_PREFIXES:
            if lowered.startswith(prefix):
                text = text[len(prefix):].strip()
                lowered = lowered[len(prefix):].strip()
                changed = True

    return text, lowered


def remember(fact: str, memory: Memory) -> str | None:
    words = fact.split()

    if len(words) < 2 or "?" in fact or words[0].lower() in NOT_A_FACT_WORDS:
        return None

    if words[0].lower() == "to":
        fact = "I need " + fact

    if len(fact) > MAX_FACT_CHARS:
        return "That's a bit long for me to remember. Can you say it in a shorter way?"

    return memory.add(fact)


def forget(query: str, memory: Memory) -> str | None:
    words = query.split()

    if not words or len(words) > 10 or words[0] in NOT_A_FORGET_WORDS:
        return None

    if all(w in FILLER_WORDS for w in words):
        return "Tell me a bit more about what to forget."

    matches = memory.find(query)

    if not matches:
        return "I don't have anything saved like that."

    if len(matches) > 1:
        shown = "\n".join(f"  - {memory.facts[i]['fact']}" for i in matches)
        return f"That matches {len(matches)} things, so tell me which one:\n{shown}"

    return memory.remove(matches[0])


def clear_everything(memory: Memory, ask_yes_no) -> str:
    if not memory.facts:
        return "I don't have anything saved yet."

    count = len(memory.facts)
    what = "the 1 thing" if count == 1 else f"all {count} things"
    if not ask_yes_no(f"Forget {what} I remember?"):
        return "Okay, I'll keep everything."

    return memory.clear()


def try_handle_memory(user_input: str, memory: Memory, ask_yes_no) -> str | None:
    text, lowered = read_command(user_input)
    plain = lowered.replace("'", "")

    if plain in LIST_PHRASES:
        return memory.describe()

    if plain in CLEAR_PHRASES:
        return clear_everything(memory, ask_yes_no)

    for trigger in FORGET_TRIGGERS:
        if lowered.startswith(trigger):
            return forget(lowered[len(trigger):].strip(), memory)

    for trigger in REMEMBER_TRIGGERS:
        if lowered.startswith(trigger):
            return remember(text[len(trigger):].strip(), memory)

    return None