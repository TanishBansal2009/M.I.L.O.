
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

JAVA_SOURCE = PROJECT_ROOT / "interfaces" / "face_java" / "Face.java"
JAVA_CLASS = PROJECT_ROOT / "interfaces" / "face_java" / "Face.class"

JAVA_CLASS_NAME = "interfaces.face_java.Face"



def compile_face():
    javac = shutil.which("javac")

    if javac is None:
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

    print("[face] Launching Milo...")

    return subprocess.Popen(
        [java, "-cp", str(PROJECT_ROOT), JAVA_CLASS_NAME]
    )


def hide_face(process) -> None:
    if process is not None and process.poll() is None:
        process.terminate()
        process.wait(timeout=3)
        print("[face] Milo's face closed.")
