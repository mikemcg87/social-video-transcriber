#!/usr/bin/env python3
import argparse
import os
import subprocess
from datetime import timedelta
from pathlib import Path

from faster_whisper import WhisperModel


def fmt_srt(ts: float) -> str:
    td = timedelta(seconds=ts)
    total = int(td.total_seconds())
    ms = int((td.total_seconds() - total) * 1000)
    hh = total // 3600
    mm = (total % 3600) // 60
    ss = total % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def extract_audio(input_path: Path, out_wav: Path) -> None:
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "/opt/homebrew/bin/ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(out_wav),
    ]
    subprocess.run(cmd, check=True)


def transcribe(
    audio_path: Path,
    out_txt: Path,
    out_srt: Path,
    model_name: str,
    compute_type: str,
    beam_size: int,
    vad_filter: bool,
) -> None:
    model = WhisperModel(model_name, device="auto", compute_type=compute_type)
    segments, _info = model.transcribe(
        str(audio_path),
        beam_size=beam_size,
        vad_filter=vad_filter,
    )

    with open(out_txt, "w", encoding="utf-8") as txt, open(out_srt, "w", encoding="utf-8") as srt:
        for i, segment in enumerate(segments, start=1):
            text = segment.text.strip()
            if text:
                txt.write(text + "\n")
            srt.write(
                f"{i}\n{fmt_srt(segment.start)} --> {fmt_srt(segment.end)}\n{text}\n\n"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Local transcription for short videos.")
    parser.add_argument("input", help="Path to video or audio file.")
    parser.add_argument("--out-dir", default=".", help="Output directory (default: current).")
    parser.add_argument("--model", default="large-v3", help="Whisper model size.")
    parser.add_argument("--compute-type", default="int8", help="Compute type for faster-whisper.")
    parser.add_argument("--beam-size", type=int, default=5, help="Beam size.")
    parser.add_argument("--no-vad", action="store_true", help="Disable VAD filtering.")
    parser.add_argument("--keep-wav", action="store_true", help="Keep extracted WAV.")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    base_name = input_path.stem
    out_txt = out_dir / f"{base_name}.txt"
    out_srt = out_dir / f"{base_name}.srt"

    is_audio = input_path.suffix.lower() in {".wav", ".mp3", ".m4a", ".aac", ".flac"}
    if is_audio:
        audio_path = input_path
    else:
        audio_path = out_dir / f"{base_name}.wav"
        extract_audio(input_path, audio_path)

    transcribe(
        audio_path=audio_path,
        out_txt=out_txt,
        out_srt=out_srt,
        model_name=args.model,
        compute_type=args.compute_type,
        beam_size=args.beam_size,
        vad_filter=not args.no_vad,
    )

    if (not is_audio) and (not args.keep_wav):
        try:
            os.remove(audio_path)
        except OSError:
            pass

    print(f"Wrote: {out_txt}")
    print(f"Wrote: {out_srt}")


if __name__ == "__main__":
    main()
