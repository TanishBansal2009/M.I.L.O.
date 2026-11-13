import atexit

from config.settings import SHOW_FACE
from core.engine import run
from interfaces import text_io
from interfaces.face import hide_face, show_face

if __name__ == "__main__":
    face_process = show_face() if SHOW_FACE else None
    atexit.register(hide_face, face_process)

    run(text_io)