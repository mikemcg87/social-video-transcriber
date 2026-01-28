#!/usr/bin/env python3
import argparse
import os
import time
from pathlib import Path
import subprocess


VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".m4a", ".mp3", ".wav", ".aac", ".flac"}


def file_stable(path: Path, checks: int = 3, interval: float = 1.5) -> bool:
    prev = -1
    for _ in range(checks):
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            return False
        if size == prev:
            return True
        prev = size
        time.sleep(interval)
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch a folder and auto-transcribe new files.")
    parser.add_argument(
        "--watch-dir",
        default="~/Downloads/social-video-transcriber/inbox",
        help="Folder to watch for new videos.",
    )
    parser.add_argument(
        "--out-dir",
        default="~/Downloads/social-video-transcriber/outputs",
        help="Folder for transcript outputs.",
    )
    parser.add_argument(
        "--processed-dir",
        default="~/Downloads/social-video-transcriber/processed",
        help="Folder to move processed inputs.",
    )
    parser.add_argument(
        "--poll",
        type=float,
        default=3.0,
        help="Polling interval in seconds.",
    )
    args = parser.parse_args()

    watch_dir = Path(args.watch_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    processed_dir = Path(args.processed_dir).expanduser().resolve()

    watch_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    print(f"Watching: {watch_dir}")
    print(f"Outputs:  {out_dir}")
    print(f"Processed:{processed_dir}")

    while True:
        for item in watch_dir.iterdir():
            if not item.is_file():
                continue
            if item.suffix.lower() not in VIDEO_EXTS:
                continue
            if not file_stable(item):
                continue

            cmd = [
                "python3",
                str(Path(__file__).parent / "x_transcribe.py"),
                str(item),
                "--out-dir",
                str(out_dir),
            ]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                # Leave file in place for retry on next poll.
                continue

            dest = processed_dir / item.name
            try:
                item.rename(dest)
            except OSError:
                pass

        time.sleep(args.poll)


if __name__ == "__main__":
    main()
