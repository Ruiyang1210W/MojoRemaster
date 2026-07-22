import argparse
import os

from dotenv import load_dotenv
from openai import OpenAI

from src import config
from src.reindex_srt import reindex_srt_perfect

load_dotenv(config.PROJECT_ROOT / ".env")

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise RuntimeError(
        "DEEPSEEK_API_KEY is not set. Copy .env.example to .env and fill in your key."
    )

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

SYSTEM_PROMPT = (
    "You are an expert subtitle translator specialized in Chinese animation (Donghua).\n"
    "Translate the following Chinese subtitles into natural, punchy English.\n"
    "The Dounghua you are focused to translate is: 魔角侦探 (MojoSpy)\n"
    "This Donghua also has some comedy elements—these can be translated in a suitably humorous way.\n"
    "Rules:\n"
    "1. Keep the exact same line structure. Do not merge lines.\n"
    "2. Keep the style conversational and match the cartoon's detective theme.\n"
    "3. Strict Character/Term Translation Table:\n"
    "   - 齐乐天 -> Locky Qi\n"
    "   - 霍星 -> Hawxing\n"
    "   - 菁菁 -> Jingjing\n"
    "   - 司马刚 -> Inspector Sima\n"
    "   - 陈嘉明 -> Jimmy Chen\n"
    "   - 天使之泪 -> Angel's Tears\n"
    "   - 香蕉博物馆 -> Banana Museum\n"
    "   - 魔角侦探 -> Mojo Spy\n"
    "   - 微笑对对碰 -> Smile Match (This is a show in the Donghua that everyone watch)\n"
    "   - 雷杰 -> Lei Jie\n"
    "   - 光明之眼 -> The Illumin-Eye\n"
    "   - 眼大人 -> Lord Eye\n"
    "   - 肉抖抖-> Shaker\n"
    "   - 为了爱与梦想 -> For Love and Ideals! (The official passionate slogan of The Illumin-Eye.)\n"
    "   - 尼亚克-> Niake\n"
    "   - 小猫咪（狗名）-> Little Kitten\n"
    "   - 乌贼城-> Squid City\n"
    "   - 金枪鱼镇 -> Tuna Town\n"
    "   - 桃乐丝-> Dorothy\n"
    "   - 小MU-> Miss MU\n"
    "   - 文康-> Wen Kang\n"

    "4. Output ONLY the translated English lines. No explanations, no numbering, no prefix/suffix."
)


def translate_text(text_block):
    """把这一批台词打包喂给 DeepSeek-V3/Coder 展现最强上下文翻译"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Translate these lines. Keep the exact line breaks:\n\n{text_block}"},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def translate_srt(input_path, output_path, batch_size=25):
    """
    流式分批翻译管道
    batch_size=25 代表一次发送25句台词，既能让 DeepSeek 结合上下文顺畅翻译，
    又不会因为一次发太多导致前后行数对不上。
    """
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.strip().split("\n\n")

    translated_blocks = []
    current_batch_texts = []
    current_batch_indices = []

    print(f"🎬 [DeepSeek 翻译管道] 已开启！总计有 {len(blocks)} 条字幕待处理...")

    for idx, block in enumerate(blocks):
        lines = block.split("\n")
        if len(lines) >= 3:
            index = lines[0]
            time_axis = lines[1]
            text = " ".join(lines[2:])

            current_batch_texts.append(text)
            current_batch_indices.append((index, time_axis))

        if len(current_batch_texts) == batch_size or idx == len(blocks) - 1:
            text_to_translate = "\n".join(current_batch_texts)
            try:
                translated_text = translate_text(text_to_translate)
                translated_lines = [line.strip() for line in translated_text.split("\n") if line.strip()]

                if len(translated_lines) == len(current_batch_texts):
                    for i, t_text in enumerate(translated_lines):
                        orig_idx, orig_time = current_batch_indices[i]
                        translated_blocks.append(f"{orig_idx}\n{orig_time}\n{t_text}")
                else:
                    print(f"⚠️ [批次 {idx // batch_size + 1}] 翻译结果行数不对等，正在启动高精度单句兜底...")
                    for i, orig_text in enumerate(current_batch_texts):
                        orig_idx, orig_time = current_batch_indices[i]
                        single_t = translate_text(orig_text)
                        translated_blocks.append(f"{orig_idx}\n{orig_time}\n{single_t}")
            except Exception as e:
                print(f"❌ 翻译出错: {e}")

            current_batch_texts = []
            current_batch_indices = []
            print(f"▓ 进度: 已处理 {idx + 1}/{len(blocks)} 条...")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(translated_blocks))

    print(f"🎉 翻译大功告成！英文精校字幕已秒级生成至: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate an episode's raw_chinese.srt to English.")
    parser.add_argument("--ep", type=int, required=True, help="Episode number, e.g. 2")
    args = parser.parse_args()

    ep_dir = config.episode_dir(args.ep)
    # Reindex right before translating: decimal indices (16.1, 16.2, ...) only
    # show up after lines are manually inserted during proofreading, so this
    # is the first point where reindexing actually has something to clean up.
    reindex_srt_perfect(ep_dir / "raw_chinese.srt")
    translate_srt(ep_dir / "raw_chinese.srt", ep_dir / "raw_english.srt")
