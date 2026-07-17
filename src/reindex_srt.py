import argparse
import re

from src import config


def reindex_srt_perfect(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 这一步利用正则表达式，直接把所有孤立的、或者叠在一起的数字（包括小数、整数、多余序号）全部清洗干净
    # 只要它处于一行的开头，并且只含有数字和点，我们就把它彻底抹去，只留下干净的时间轴和台词
    cleaned_content = re.sub(r"^\s*\d+(\.\d+)?\s*$", "", content, flags=re.MULTILINE)

    # 2. 按行拆分，开始重新编号
    lines = cleaned_content.split("\n")
    new_lines = []
    current_index = 1

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 只要抓到时间轴特征 -->
        if "-->" in line:
            # 自动在时间轴上方插入崭新、干净的自增整数序号
            new_lines.append(f"{current_index}")
            new_lines.append(line)
            current_index += 1
        else:
            # 如果是空行或者台词，且不是空行堆叠，就正常保留
            if line or (new_lines and new_lines[-1] != ""):
                new_lines.append(line)
        i += 1

    # 3. 重新拼合写入
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print(f"✨ 强迫症终极版！已自动干掉所有冗余的小数序号，并重新完美递增至 {current_index - 1}！")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reindex an episode's raw_chinese.srt sequence numbers.")
    parser.add_argument("--ep", type=int, required=True, help="Episode number, e.g. 2")
    args = parser.parse_args()

    ep_dir = config.episode_dir(args.ep)
    reindex_srt_perfect(ep_dir / "raw_chinese.srt")
