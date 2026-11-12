import webbrowser
from pathlib import Path

FACE_FILE = Path(__file__).with_name("face.html")

def show_face() -> bool:
    if not FACE_FILE.exists():
        return False
    return bool(webbrowser.open(FACE_FILE.as_uri()))