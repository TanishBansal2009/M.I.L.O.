import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

JAVA_SOURCE = PROJECT_ROOT / "interfaces" / "face_java" / "Face.java"
JAVA_CLASS = PROJECT_ROOT / "interfaces" / "face_java" / "Face.class"

JAVA_CLASS_NAME = "interfaces.face_java.Face"



def class_is_up_to_date():
    return JAVA_CLASS.exists() and JAVA_CLASS.stat().st_mtime >= JAVA_SOURCE.stat().st_mtime



def compile_face():
    if class_is_up_to_date():
        return True

    javac = shutil.which("javac")

    if javac is None:
        if JAVA_CLASS.exists():
            return True
        print("[face] Java compiler (javac) was not found.")
        return False

    print("[face] Compiling Java face...")

    result = subprocess.run(
        [javac, "-d", str(PROJECT_ROOT), str(JAVA_SOURCE)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("[face] Compilation failed:")
        print(result.stderr)
        return False

    if not JAVA_CLASS.exists():
        print("[face] Compilation completed, but Face.class is missing.")
        return False

    print("[face] Compilation successful.")
    return True



def show_face():
    java = shutil.which("java")

    if java is None:
        print("[face] Java runtime was not found.")
        return None

    if not compile_face():
        return None

    # a separate process group, so Ctrl+C in the terminal doesn't also close the face
    if sys.platform == "win32":
        separate = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    else:
        separate = {"start_new_session": True}

    return subprocess.Popen(
        [java, "-cp", str(PROJECT_ROOT), JAVA_CLASS_NAME],
        **separate
    )



def hide_face(process) -> None:
    if process is None or process.poll() is not None:
        return

    process.terminate()

    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()

    print("[face] Milo's face closed.")