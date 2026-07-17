"""Optional: mux raw_english.srt into the source video as a soft-subtitle track.

Not part of the default pipeline (src/pipeline.py) — currently subtitles are
uploaded to YouTube directly as .srt files, so this step is unused. Requires
ffmpeg to be installed and on PATH.
"""
import argparse
import subprocess

from src import config


def mux_subtitles(ep: int):
    ep_dir = config.episode_dir(ep)
    video_path = config.find_source(ep_dir)
    srt_path = ep_dir / "raw_english.srt"
    output_path = ep_dir / f"Mojo_Spy_Ep{ep:02d}_EN.mp4"

    command = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(srt_path),
        "-c", "copy",
        "-c:s", "mov_text",
        str(output_path),
    ]

    print("🚀 正在通过 Python 后台调用 ffmpeg 进行无损合并...")
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("🎉 瞬间合体成功！")
        print(f"✨ 英文重制版视频已完美生成至: {output_path}")
    except FileNotFoundError:
        print("❌ 错误：系统中找不到 ffmpeg 可执行程序。请先安装 ffmpeg 并加入 PATH。")
    except subprocess.CalledProcessError as e:
        print(f"❌ 合并失败，错误信息:\n{e.stderr}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mux raw_english.srt into the episode's source video (needs ffmpeg).")
    parser.add_argument("--ep", type=int, required=True, help="Episode number, e.g. 2")
    args = parser.parse_args()
    mux_subtitles(args.ep)
