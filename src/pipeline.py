import argparse

STEP_FUNCS = {}


def _lazy_steps():
    # Imported lazily so `--steps transcribe` alone doesn't require the
    # DeepSeek API key to be set, etc.
    if not STEP_FUNCS:
        from src.transcribe import transcribe_episode
        from src.translate_srt import translate_srt
        from src.reindex_srt import reindex_srt_perfect
        from src.mux_subtitles import mux_subtitles
        from src import config

        def _transcribe(ep, language):
            transcribe_episode(ep, language=language)

        def _translate(ep, language):
            ep_dir = config.episode_dir(ep)
            # Reindex right before translating, not right after transcribing:
            # decimal indices (16.1, 16.2, ...) only show up once lines have
            # been manually inserted during proofreading, so reindexing
            # earlier has nothing to clean up yet.
            reindex_srt_perfect(ep_dir / "raw_chinese.srt")
            translate_srt(ep_dir / "raw_chinese.srt", ep_dir / "raw_english.srt")

        def _reindex(ep, language):
            ep_dir = config.episode_dir(ep)
            reindex_srt_perfect(ep_dir / "raw_chinese.srt")

        def _mux(ep, language):
            mux_subtitles(ep)

        STEP_FUNCS.update(
            transcribe=_transcribe,
            translate=_translate,
            reindex=_reindex,
            mux=_mux,
        )
    return STEP_FUNCS


DEFAULT_STEPS = ["transcribe"]
# 'translate' (which reindexes raw_chinese.srt right before translating) is
# run manually after reviewing/fixing raw_chinese.srt by hand, so it's
# opt-in (--steps translate) rather than part of the default run.


def run_pipeline(ep: int, steps=None, language: str = "zh"):
    steps = steps or DEFAULT_STEPS
    step_funcs = _lazy_steps()
    for step in steps:
        if step not in step_funcs:
            raise ValueError(f"Unknown step '{step}'. Valid steps: {list(step_funcs)}")
        print(f"\n{'=' * 60}\n▶ Ep{ep:02d}: {step}\n{'=' * 60}")
        step_funcs[step](ep, language)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Mojo Spy subtitle pipeline for one episode.")
    parser.add_argument("--ep", type=int, required=True, help="Episode number, e.g. 2")
    parser.add_argument(
        "--steps",
        default=",".join(DEFAULT_STEPS),
        help=f"Comma-separated steps to run (default: {','.join(DEFAULT_STEPS)}). "
        f"'translate' is opt-in (reindexes then translates, run after manually "
        f"reviewing raw_chinese.srt); 'reindex' alone and 'mux' (needs ffmpeg) "
        f"are also opt-in.",
    )
    parser.add_argument("--language", default="zh", help="Source language code (default: zh)")
    args = parser.parse_args()

    run_pipeline(args.ep, steps=args.steps.split(","), language=args.language)
