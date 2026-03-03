#!/usr/bin/env python3
"""
字体子集化工具：从字体文件中抽取指定字符，生成精简的小字体文件。

依赖安装：
    pip install fonttools brotli zopfli

用法：
    python font_subset.py -i 输入字体.ttf -o 输出字体.ttf -t "你好世界"
    python font_subset.py -i 输入字体.ttf -o 输出字体.woff2 -t "ABC123"
    python font_subset.py -i 输入字体.otf -o 输出字体.ttf -f chars.txt
"""

import argparse
import sys
from pathlib import Path

from fontTools.subset import Subsetter, Options
from fontTools.ttLib import TTFont


def load_characters(text: str | None, file_path: str | None) -> str:
    """从命令行参数或文件中加载需要保留的字符集合。"""
    chars = ""
    if text:
        chars += text
    if file_path:
        chars += Path(file_path).read_text(encoding="utf-8")
    # 去重并排序，方便查看
    return "".join(sorted(set(chars)))


def subset_font(input_path: str, output_path: str, characters: str) -> dict:
    """
    对字体进行子集化处理。

    参数:
        input_path:  源字体文件路径（.ttf / .otf / .woff2）
        output_path: 输出字体文件路径
        characters:  需要保留的字符字符串

    返回:
        包含处理统计信息的字典
    """
    font = TTFont(input_path)

    # 统计原始信息
    original_glyph_count = len(font.getGlyphOrder())
    original_size = Path(input_path).stat().st_size

    # 配置子集化选项
    options = Options()
    options.layout_features = ["*"]   # 保留所有 OpenType 特性
    options.name_IDs = ["*"]          # 保留所有名称记录
    options.notdef_outline = True     # 保留 .notdef 轮廓
    options.glyph_names = True        # 保留字形名称

    # 根据输出格式决定是否需要 woff2 压缩
    out_suffix = Path(output_path).suffix.lower()
    if out_suffix == ".woff2":
        options.flavor = "woff2"
    elif out_suffix == ".woff":
        options.flavor = "woff"
    else:
        options.flavor = None

    # 执行子集化
    subsetter = Subsetter(options=options)
    # 将字符转换为 Unicode 码点集合
    codepoints = {ord(c) for c in characters}
    subsetter.populate(unicodes=codepoints)
    subsetter.subset(font)

    # 保存
    font.save(output_path)
    font.close()

    # 统计结果
    result_font = TTFont(output_path)
    new_glyph_count = len(result_font.getGlyphOrder())
    new_size = Path(output_path).stat().st_size
    result_font.close()

    return {
        "original_glyphs": original_glyph_count,
        "subset_glyphs": new_glyph_count,
        "original_size": original_size,
        "subset_size": new_size,
        "characters": characters,
        "character_count": len(characters),
    }


def format_size(size_bytes: int) -> str:
    """将字节数格式化为可读字符串。"""
    for unit in ("B", "KB", "MB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} GB"


def main():
    parser = argparse.ArgumentParser(
        description="从字体文件中提取指定字符，生成子集字体"
    )
    parser.add_argument("-i", "--input", required=True, help="输入字体文件路径")
    parser.add_argument("-o", "--output", required=True, help="输出字体文件路径")
    parser.add_argument("-t", "--text", help="需要保留的字符（直接输入）")
    parser.add_argument("-f", "--file", help="包含需要保留字符的文本文件路径")
    args = parser.parse_args()

    if not args.text and not args.file:
        parser.error("请至少指定 -t (文本) 或 -f (文件) 其中之一")

    if not Path(args.input).exists():
        print(f"错误：输入文件不存在 → {args.input}", file=sys.stderr)
        sys.exit(1)

    characters = load_characters(args.text, args.file)
    if not characters:
        print("错误：未提供任何字符", file=sys.stderr)
        sys.exit(1)

    print(f"输入字体：{args.input}")
    print(f"提取字符：{characters[:50]}{'…' if len(characters) > 50 else ''}")
    print(f"字符数量：{len(characters)}")
    print()

    stats = subset_font(args.input, args.output, characters)

    print("── 完成 ──────────────────────────────")
    print(f"输出字体：{args.output}")
    print(f"字形数量：{stats['original_glyphs']} → {stats['subset_glyphs']}")
    print(f"文件大小：{format_size(stats['original_size'])} → {format_size(stats['subset_size'])}")
    ratio = (1 - stats["subset_size"] / stats["original_size"]) * 100
    print(f"压缩比例：减小了 {ratio:.1f}%")


if __name__ == "__main__":
    main()
