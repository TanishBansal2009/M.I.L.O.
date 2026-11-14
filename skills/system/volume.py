import ctypes
import platform
import time

from skills.common import simple_text

KEY_MUTE = 0xAD
KEY_DOWN = 0xAE
KEY_UP = 0xAF
KEY_RELEASE = 0x0002
KEY_PAUSE = 0.02

STEPS = {"small": 2, "normal": 5, "big": 10}
MAX_WORDS = 7

UP_WORDS = {"up", "louder", "increase", "raise", "higher", "boost"}
DOWN_WORDS = {"down", "quieter", "softer", "decrease", "lower", "reduce"}
MUTE_WORDS = {"mute", "unmute"}
SUBJECT_WORDS = {"volume", "sound", "audio", "music", "speakers"}
COMPARATIVE_WORDS = {"louder", "quieter", "softer"}
SMALL_WORDS = {"bit", "little", "slightly", "touch", "notch"}
BIG_WORDS = {"lot", "much", "way"}
OTHER_WORDS = {"turn", "make", "bring", "toggle", "the", "a", "it", "some", "just"}

KNOWN_WORDS = (
    UP_WORDS | DOWN_WORDS | MUTE_WORDS | SUBJECT_WORDS | SMALL_WORDS | BIG_WORDS | OTHER_WORDS
)


def parse_request(user_input: str) -> tuple[str, int] | None:
    words = [w.strip(",") for w in simple_text(user_input).split()]
    if not words or len(words) > MAX_WORDS or any(w not in KNOWN_WORDS for w in words):
        return None

    found = set(words)

    if found & MUTE_WORDS:
        return None if found & (UP_WORDS | DOWN_WORDS) else ("mute", 1)

    wants_up = bool(found & UP_WORDS)
    wants_down = bool(found & DOWN_WORDS)
    if wants_up == wants_down:
        return None

    says_what = found & (SUBJECT_WORDS | COMPARATIVE_WORDS) or ("it" in found and found & {"turn", "make", "bring"})
    if not says_what:
        return None

    if found & SMALL_WORDS:
        size = "small"
    elif found & BIG_WORDS:
        size = "big"
    else:
        size = "normal"

    return ("up" if wants_up else "down"), STEPS[size]


def press_key(key_code: int) -> None:
    user32 = ctypes.windll.user32
    user32.keybd_event(key_code, 0, 0, 0)
    user32.keybd_event(key_code, 0, KEY_RELEASE, 0)


def try_handle_volume(user_input: str) -> str | None:
    request = parse_request(user_input)
    if request is None:
        return None

    if platform.system() != "Windows":
        return "I can only control the volume on Windows for now."

    action, presses = request
    key = {"up": KEY_UP, "down": KEY_DOWN, "mute": KEY_MUTE}[action]

    try:
        for _ in range(presses):
            press_key(key)
            time.sleep(KEY_PAUSE)
    except (OSError, AttributeError):
        return "I couldn't change the volume on this computer."

    if action == "mute":
        return "Okay, I flipped the mute switch."

    amount = " a little" if presses == STEPS["small"] else " a lot" if presses == STEPS["big"] else ""
    return f"Turned the volume {action}{amount}."