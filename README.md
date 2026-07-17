# Mojo Spy — Subtitle Pipeline

A local pipeline that transcribes and translates the Chinese donghua **魔角侦探 (Mojo Spy)**
into English subtitles, using GPU-accelerated Whisper for transcription and DeepSeek
for translation.

Source video/audio files are not included in this repo (copyrighted third-party
content) — only the code and a couple of sample `.srt` outputs.

## Pipeline

```
source.<ext>  --[transcribe: faster-whisper, GPU]-->  raw_chinese.srt
              --[translate: DeepSeek]-->               raw_english.srt
              --[reindex: cleanup]-->                  raw_english.srt (final)
```

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
python -m src.pipeline --ep 2
```

This runs transcribe → translate → reindex and leaves `raw_chinese.srt` /
`raw_english.srt` in `Eps/ep02/`. Run a single step instead with `--steps transcribe`,
or run any step's module directly, e.g. `python -m src.transcribe --ep 2`.

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
  translate_srt.py        DeepSeek -> raw_english.srt
  reindex_srt.py          renumber SRT after cleanup
  mux_subtitles.py         optional: burn srt into video (needs ffmpeg)
  pipeline.py              orchestrator
models/                   Whisper model cache (gitignored)
```

## Roadmap

- [ ] Full season transcribed/translated (currently: Ep1, Ep2 in progress)
- [ ] Demo clip / before-after sample for the portfolio writeup
- [ ] Per-season glossary config instead of the inline character table
