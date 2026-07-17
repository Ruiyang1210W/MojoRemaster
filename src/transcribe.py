import argparse
from pathlib import Path

from src import config

config.setup_cuda_dlls()

from faster_whisper import WhisperModel


def transcribe_episode(ep: int, language: str = "zh") -> Path:
    ep_dir = config.episode_dir(ep)
    audio_path = config.find_source(ep_dir)
    srt_path = ep_dir / "raw_chinese.srt"

    print(f"🚀 正在加载 Whisper 顶级 large-v3 模型...")
    print("💡 提示：首次运行会自动下载模型到 models/，请耐心等待...")

    try:
        model = WhisperModel(
            "large-v3",
            device="cuda",
            compute_type="float16",
            download_root=str(config.MODELS_DIR),
        )
    except Exception as e:
        print(f"\n❌ 初始化 CUDA 显卡加速失败，错误信息: {e}")
        print("💡 正在自动切换为【CPU + float32 兼容模式】启动模型（速度会稍慢一些）...")
        model = WhisperModel(
            "large-v3",
            device="cpu",
            compute_type="float32",
            download_root=str(config.MODELS_DIR),
        )

    print(f"🎙️ 正在进行高质量语音识别（已限定语言 '{language}'，自动过滤复读幻觉）...")

    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        condition_on_previous_text=False,
    )

    print(f"ℹ️ 检测到语言: {info.language} (置信度: {info.language_probability:.2f})")
    print("--- 识别结果 ---")

    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, segment in enumerate(segments, start=1):
            def format_time(seconds):
                hrs = int(seconds // 3600)
                mins = int((seconds % 3600) // 60)
                secs = int(seconds % 60)
                msecs = int((seconds - int(seconds)) * 1000)
                return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"

            start_t = format_time(segment.start)
            end_t = format_time(segment.end)
            text = segment.text.strip()

            print(f"[{start_t} --> {end_t}] {text}")
            f.write(f"{idx}\n{start_t} --> {end_t}\n{text}\n\n")

    print(f"\n🎉 完美！高质量字幕已成功生成到: {srt_path}")
    return srt_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an episode's source audio to SRT.")
    parser.add_argument("--ep", type=int, required=True, help="Episode number, e.g. 2")
    parser.add_argument("--language", default="zh", help="Source language code (default: zh)")
    args = parser.parse_args()
    transcribe_episode(args.ep, language=args.language)
