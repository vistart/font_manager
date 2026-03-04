#!/usr/bin/env python3
"""
字体分析工具：分析字体文件包含的字符和语言支持。

依赖安装：
pip install fonttools

用法：
# 查看字体包含的所有字符
python font_analyze.py -i 字体.ttf

# 查看字体支持的语言
python font_analyze.py -i 字体.ttf --language

# 导出字符列表到文件
python font_analyze.py -i 字体.ttf -o chars.txt
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from fontTools.ttLib import TTFont

UNICODE_BLOCKS = [
    ("基本拉丁", 0x0000, 0x007F),
    ("拉丁-1补充", 0x0080, 0x00FF),
    ("拉丁扩展-A", 0x0100, 0x017F),
    ("拉丁扩展-B", 0x0180, 0x024F),
    ("IPA扩展", 0x0250, 0x02AF),
    ("间距修饰字母", 0x02B0, 0x02FF),
    ("希腊和科普特", 0x0370, 0x03FF),
    ("西里尔字母", 0x0400, 0x04FF),
    ("一般标点", 0x2000, 0x206F),
    ("上标和下标", 0x2070, 0x209F),
    ("货币符号", 0x20A0, 0x20CF),
    ("箭头", 0x2190, 0x21FF),
    ("数学运算符", 0x2200, 0x22FF),
    ("几何图形", 0x25A0, 0x25FF),
    ("中日韩统一表意文字", 0x4E00, 0x9FFF),
    ("中日韩统一表意文字扩展A", 0x3400, 0x4DBF),
    ("中日韩统一表意文字扩展B", 0x20000, 0x2A6DF),
    ("中日韩兼容表意文字", 0xF900, 0xFAFF),
    ("半角和全角形式", 0xFF00, 0xFFEF),
    ("平假名", 0x3040, 0x309F),
    ("片假名", 0x30A0, 0x30FF),
    ("谚文音节", 0xAC00, 0xD7AF),
    ("阿拉伯", 0x0600, 0x06FF),
    ("希伯来", 0x0590, 0x05FF),
    ("泰文", 0x0E00, 0x0E7F),
    ("天城文", 0x0900, 0x097F),
]


def get_unicode_block(codepoint: int) -> str:
    """获取字符所属的 Unicode 区块名称。"""
    for name, start, end in UNICODE_BLOCKS:
        if start <= codepoint <= end:
            return name
    return "其他"


def analyze_font(font_path: str) -> dict:
    """
    分析字体文件。

    参数:
        font_path: 字体文件路径

    返回:
        包含分析结果的字典
    """
    font = TTFont(font_path)

    cmap = font.getBestCmap()

    codepoints = sorted(cmap.keys())

    blocks = defaultdict(list)
    for cp in codepoints:
        block_name = get_unicode_block(cp)
        blocks[block_name].append(cp)

    font.close()

    return {
        "glyph_count": len(codepoints),
        "codepoints": codepoints,
        "blocks": dict(blocks),
        "cmap": cmap,
    }


def format_char(cp: int) -> str:
    """格式化字符显示。"""
    try:
        char = chr(cp)
        if cp < 32 or cp in (0x7F,):
            return f"U+{cp:04X}"
        return f"U+{cp:04X} '{char}'"
    except ValueError:
        return f"U+{cp:04X}"


def print_analysis(stats: dict, show_language: bool = False):
    """打印分析结果。"""
    print(f"字符总数：{stats['glyph_count']}")
    print()

    if show_language:
        print("── 语言支持 ────────────────────────")
        blocks = stats["blocks"]

        cjk_blocks = ["中日韩统一表意文字", "中日韩统一表意文字扩展A", "中日韩统一表意文字扩展B", "中日韩兼容表意文字"]
        cjk_count = sum(len(blocks.get(b, [])) for b in cjk_blocks)

        hiragana = len(blocks.get("平假名", []))
        katakana = len(blocks.get("片假名", []))

        latin = len(blocks.get("基本拉丁", []))
        latin_ext = len(blocks.get("拉丁-1补充", [])) + len(blocks.get("拉丁扩展-A", []))

        hangul = len(blocks.get("谚文音节", []))
        arabic = len(blocks.get("阿拉伯", []))
        hebrew = len(blocks.get("希伯来", []))
        thai = len(blocks.get("泰文", []))
        devanagari = len(blocks.get("天城文", []))

        if latin > 0:
            print(f"拉丁字母：{latin + latin_ext} 字符")
        if cjk_count > 0:
            print(f"中日韩文字：{cjk_count} 字符")
        if hiragana + katakana > 0:
            print(f"日文假名：{hiragana + katakana} 字符（平假名 {hiragana}，片假名 {katakana}）")
        if hangul > 0:
            print(f"韩文谚文：{hangul} 字符")
        if arabic > 0:
            print(f"阿拉伯文：{arabic} 字符")
        if hebrew > 0:
            print(f"希伯来文：{hebrew} 字符")
        if thai > 0:
            print(f"泰文：{thai} 字符")
        if devanagari > 0:
            print(f"天城文：{devanagari} 字符")

        print()

    print("── Unicode 区块分布 ────────────────")
    for block_name in [b[0] for b in UNICODE_BLOCKS]:
        if block_name in stats["blocks"]:
            count = len(stats["blocks"][block_name])
            bar = "█" * min(50, count // 50)
            print(f"{block_name:20} {count:6} {bar}")
    print()


def print_characters(stats: dict, limit: int = 100):
    """打印字符列表。"""
    codepoints = stats["codepoints"]

    if len(codepoints) <= limit:
        print("── 全部字符 ────────────────────────")
        for cp in codepoints:
            print(f"  {format_char(cp)}")
    else:
        print(f"── 前 {limit} 个字符 ────────────────────────")
        for cp in codepoints[:limit]:
            print(f"  {format_char(cp)}")
        print(f"  ... 还有 {len(codepoints) - limit} 个字符")


def export_characters(stats: dict, output_path: str):
    """导出字符列表到文件。"""
    chars = "".join(chr(cp) for cp in stats["codepoints"] if cp >= 32)
    Path(output_path).write_text(chars, encoding="utf-8")
    print(f"字符列表已导出 → {output_path} ({len(chars)} 个可打印字符)")


def main():
    parser = argparse.ArgumentParser(description="分析字体文件包含的字符")
    parser.add_argument("-i", "--input", required=True, help="字体文件路径")
    parser.add_argument("-o", "--output", help="导出字符列表到文件")
    parser.add_argument("--language", action="store_true", help="显示语言支持分析")
    parser.add_argument("--list", action="store_true", help="显示字符列表")
    parser.add_argument("--limit", type=int, default=100, help="显示字符列表的限制数量")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"错误：字体文件不存在 → {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"字体：{args.input}")
    print()

    stats = analyze_font(args.input)

    print_analysis(stats, show_language=args.language)

    if args.list:
        print_characters(stats, limit=args.limit)

    if args.output:
        export_characters(stats, args.output)


if __name__ == "__main__":
    main()
