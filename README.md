# x-transcribe

Local transcription pipeline for social videos, especially when files are too large for hosted AI uploads or when platforms (e.g., Twitter/X) have no captions.

For YouTube, you may not need local transcription if you already have an MCP server that can fetch transcripts directly.

## Requirements

- Python 3.10+
- ffmpeg (via Homebrew)
- `faster-whisper` Python package

## Install

```bash
python3 -m pip install --user -U faster-whisper
```

## Usage

Transcribe a video (extracts audio first):

```bash
python3 x_transcribe.py /path/to/video.mp4 --out-dir /path/to/output
```

Transcribe from a URL (downloads first):

```bash
python3 x_transcribe.py --url "https://x.com/..." --out-dir /path/to/output
```

Transcribe an audio file directly:

```bash
python3 x_transcribe.py /path/to/audio.wav
```

### Options

- `--model` (default: `large-v3`)
- `--compute-type` (default: `int8`)
- `--beam-size` (default: `5`)
- `--no-vad` (disable VAD filtering)
- `--keep-wav` (keep extracted WAV next to outputs)
- `--url` (download video from URL first)
- `--keep-download` (keep downloaded video)

## Outputs

Creates:

- `<basename>.txt`
- `<basename>.srt`

## Watcher (optional)

Continuously watch a folder for new videos and auto-transcribe them.

Defaults:
- Inbox: `~/Downloads/social-video-transcriber/inbox`
- Outputs: `~/Downloads/social-video-transcriber/outputs`
- Processed: `~/Downloads/social-video-transcriber/processed`

```bash
python3 watch_folder.py
```

You can override paths:

```bash
python3 watch_folder.py \
  --watch-dir ~/Downloads/social-video-transcriber/inbox \
  --out-dir ~/Downloads/social-video-transcriber/outputs \
  --processed-dir ~/Downloads/social-video-transcriber/processed
```
