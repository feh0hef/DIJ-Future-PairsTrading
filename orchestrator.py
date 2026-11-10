import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PIPELINE = ("main.py", "interactions.py", "pairs.py")


def main() -> int:
    for script_name in PIPELINE:
        script_path = BASE_DIR / script_name
        if not script_path.is_file():
            print(f"File not found: {script_path}", file=sys.stderr)
            return 1

        print(f"\n==> {script_name}", flush=True)
        result = subprocess.run([sys.executable, str(script_path)], cwd=BASE_DIR)
        if result.returncode != 0:
            print(
                f"\nPipeline stopped: {script_name} exited with code {result.returncode}.",
                file=sys.stderr,
            )
            return result.returncode

    print("\nPipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
