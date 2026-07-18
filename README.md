# MojoSpy — Subtitle Pipeline

A local pipeline that transcribes and translates the Chinese donghua **魔角侦探 (Mojo Spy)**
into English subtitles, using GPU-accelerated Whisper for transcription and DeepSeek
for translation.

Source video/audio files are not included in this repo (copyrighted third-party
content) — only the code and a couple of sample `.srt` outputs.

## Demo

Watch on YouTube (full series, updating as episodes are finished): https://www.youtube.com/playlist?list=PLb238vBzdlPQ

## Pipeline

```
source.<ext>  --[transcribe: faster-whisper, GPU]-->      raw_chinese.srt
              --[MANUAL: native-speaker review/fix]-->     raw_chinese.srt (corrected)
              --[translate: reindex, then DeepSeek]-->      raw_english.srt
```

Transcription is never perfect, so `raw_chinese.srt` is meant to be opened and
corrected by hand before translating — `translate` is intentionally left out of
the default pipeline run for that reason (see Usage below). Manual edits during
review are free to use decimal indices (`16.1`, `16.2`, ...) to insert missed
lines; `translate` reindexes `raw_chinese.srt` back to a clean 1, 2, 3, ...
sequence immediately before sending it to DeepSeek, so that's the only point
reindexing needs to happen.

The English `.srt` is uploaded directly to YouTube as a soft-subtitle track — no
video muxing needed. An optional `mux_subtitles` step exists for burning subtitles
into a copy of the video, but it requires `ffmpeg` and isn't part of the default run.

## Setup

1. Python 3.12, `python -m venv .venv`, then `.venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your `DEEPSEEK_API_KEY`
4. GPU transcription needs CUDA 12's cuBLAS/cuDNN. The pip packages above provide
   them; `src/config.py::setup_cuda_dlls()` registers them with Windows automatically.
   If you have a system-wide CUDA Toolkit installed that isn't v12.x, ignore it —
   it isn't used.

## Usage

Drop an episode's video/audio into `Eps/epNN/source.<ext>` (any container works —
`.mp4`, `.m4a`, etc.), then run:

```
python -m src.pipeline --ep N
```

This runs transcribe and leaves `raw_chinese.srt` in `Eps/ep02/`. Open it and fix
any misheard lines by hand (decimal indices like `16.1` are fine for inserting
missed lines), then translate once you're happy with it:

```
python -m src.translate_srt --ep N
```

This reindexes `raw_chinese.srt` and translates it into `raw_english.srt` in one
go. Run any step's module directly if needed, e.g. `python -m src.reindex_srt --ep 2`.

## Layout

```
Eps/
  ep01/
    source.mp4          (gitignored)
    raw_chinese.srt
    raw_english.srt
  ep02/
    ...
src/
  config.py              paths, CUDA DLL setup
  transcribe.py           faster-whisper -> raw_chinese.srt
  translate_srt.py        reindex + DeepSeek -> raw_english.srt
  reindex_srt.py          renumber SRT (also runnable standalone)
  mux_subtitles.py         optional: burn srt into video (needs ffmpeg)
  pipeline.py              orchestrator
models/                   Whisper model cache (gitignored)
```

## Roadmap

- [x] Ep1 published to YouTube (see Demo above)
- [ ] Full season transcribed/translated
- [ ] Per-season glossary config instead of the inline character table
