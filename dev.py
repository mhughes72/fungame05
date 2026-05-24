"""
Dev launcher — starts the FastAPI backend and Vite frontend together.
Ctrl+C kills both.

Usage:
    python dev.py
"""

import os
import subprocess
import sys


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    npm  = "npm.cmd" if sys.platform == "win32" else "npm"

    procs = []
    try:
        procs.append(subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.main:app", "--reload", "--port", "8000"],
            cwd=root,
        ))
        procs.append(subprocess.Popen(
            [npm, "run", "dev"],
            cwd=os.path.join(root, "web"),
        ))

        print("Backend:  http://localhost:8000")
        print("Frontend: http://localhost:5173")
        print("Press Ctrl+C to stop both.\n")

        for p in procs:
            p.wait()

    except KeyboardInterrupt:
        print("\nShutting down...")
        for p in procs:
            p.terminate()


if __name__ == "__main__":
    main()
