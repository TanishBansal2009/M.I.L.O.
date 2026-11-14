import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "data" / "log.jsonl"

PRIVATE_SKILLS = ("memory",)


def log_interaction(text: str, handled_by: str, enabled: bool = True) -> None:
    if not enabled:
        return

    entry = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "text": None if handled_by in PRIVATE_SKILLS else text,
        "handled_by": handled_by,
    }

    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass