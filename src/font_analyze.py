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
    ("组合变音标记", 0x0300, 0x036F),
    ("希腊和科普特", 0x0370, 0x03FF),
    ("希腊扩展", 0x1F00, 0x1FFF),
    ("西里尔字母", 0x0400, 0x04FF),
    ("西里尔字母补充", 0x0500, 0x052F),
    ("亚美尼亚", 0x0530, 0x058F),
    ("希伯来", 0x0590, 0x05FF),
    ("阿拉伯", 0x0600, 0x06FF),
    ("阿拉伯补充", 0x0750, 0x077F),
    ("阿拉伯扩展-A", 0x08A0, 0x08FF),
    ("阿拉伯扩展-B", 0x0870, 0x089F),
    ("叙利亚", 0x0700, 0x074F),
    ("塔纳", 0x1200, 0x137F),
    ("天城文", 0x0900, 0x097F),
    ("孟加拉", 0x0980, 0x09FF),
    ("古鲁穆奇", 0x0A00, 0x0A7F),
    ("古吉拉特", 0x0A80, 0x0AFF),
    ("奥里亚", 0x0B00, 0x0B7F),
    ("泰米尔", 0x0B80, 0x0BFF),
    ("泰卢固", 0x0C00, 0x0C7F),
    ("卡纳达", 0x0C80, 0x0CFF),
    ("马拉雅拉姆", 0x0D00, 0x0D7F),
    ("僧伽罗", 0x0D80, 0x0DFF),
    ("泰文", 0x0E00, 0x0E7F),
    ("老挝", 0x0E80, 0x0EFF),
    ("藏文", 0x0F00, 0x0FFF),
    ("缅甸", 0x1000, 0x109F),
    ("格鲁吉亚", 0x10A0, 0x10FF),
    ("格鲁吉亚补充", 0x2D00, 0x2D2F),
    ("朝鲜文字母", 0x1100, 0x11FF),
    ("谚文音节", 0xAC00, 0xD7AF),
    ("谚文字母扩展-A", 0xA960, 0xA97F),
    ("谚文字母扩展-B", 0xD7B0, 0xD7FF),
    ("平假名", 0x3040, 0x309F),
    ("片假名", 0x30A0, 0x30FF),
    ("片假名扩展", 0x31F0, 0x31FF),
    ("中日韩统一表意文字", 0x4E00, 0x9FFF),
    ("中日韩统一表意文字扩展A", 0x3400, 0x4DBF),
    ("中日韩统一表意文字扩展B", 0x20000, 0x2A6DF),
    ("中日韩统一表意文字扩展C", 0x2A700, 0x2B73F),
    ("中日韩统一表意文字扩展D", 0x2B740, 0x2B81F),
    ("中日韩统一表意文字扩展E", 0x2B820, 0x2CEAF),
    ("中日韩统一表意文字扩展F", 0x2CEB0, 0x2EBEF),
    ("中日韩统一表意文字扩展G", 0x30000, 0x3134F),
    ("中日韩统一表意文字扩展H", 0x31350, 0x323AF),
    ("中日韩统一表意文字扩展I", 0x2EBF0, 0x2EE5F),
    ("中日韩兼容表意文字", 0xF900, 0xFAFF),
    ("中日韩兼容表意文字补充", 0x2F800, 0x2FA1F),
    ("康熙部首", 0x2F00, 0x2FDF),
    ("中日韩部首补充", 0x2E80, 0x2EFF),
    ("半角和全角形式", 0xFF00, 0xFFEF),
    ("注音符号", 0x3100, 0x312F),
    ("注音符号扩展", 0x31A0, 0x31BF),
    ("傣文", 0x1950, 0x197F),
    ("新傣文", 0x1980, 0x19DF),
    ("高棉", 0x1780, 0x17FF),
    ("高棉符号", 0x19E0, 0x19FF),
    ("埃塞俄比亚", 0x1200, 0x137F),
    ("埃塞俄比亚补充", 0x1380, 0x139F),
    ("埃塞俄比亚扩展", 0x2D80, 0x2DDF),
    ("埃塞俄比亚扩展-A", 0xAB00, 0xAB2F),
    ("切罗基", 0x13A0, 0x13FF),
    ("加拿大原住民音节", 0x1400, 0x167F),
    ("加拿大原住民音节扩展", 0x18B0, 0x18FF),
    ("欧格", 0x1680, 0x169F),
    ("拉扬", 0x1720, 0x173F),
    ("他加禄", 0x1700, 0x171F),
    ("哈努诺", 0x1720, 0x173F),
    ("布希德", 0x1740, 0x175F),
    ("塔格巴努瓦", 0x1760, 0x177F),
    ("蒙古", 0x1800, 0x18AF),
    ("蒙古补充", 0x11660, 0x1167F),
    ("维吾尔", 0x0700, 0x074F),
    ("西夏", 0x17000, 0x18AFF),
    ("西夏部首", 0x18800, 0x18AFF),
    ("契丹小字", 0x18B00, 0x18CFF),
    ("女真", 0x18D00, 0x18D7F),
    ("傈僳", 0xA000, 0xA4CF),
    ("彝", 0xA000, 0xA4CF),
    ("彝文部首", 0xA490, 0xA4CF),
    ("纳西东巴", 0x1E800, 0x1E8FF),
    ("纳西哥巴", 0x1E900, 0x1E9FF),
    ("婆罗米", 0x11000, 0x1107F),
    ("古印度文字", 0x11080, 0x110CF),
    ("古卡拉尼", 0x110D0, 0x110FF),
    ("凯塔", 0x11080, 0x110CF),
    ("凯塔扩展", 0x11100, 0x1114F),
    ("孔雀", 0x11580, 0x115FF),
    ("悉昙", 0x11580, 0x115FF),
    ("莫迪", 0x11600, 0x1165F),
    ("莫迪补充", 0x11680, 0x116CF),
    ("夏拉达", 0x11180, 0x111DF),
    ("锡克", 0x11680, 0x116CF),
    ("霍吉", 0x11150, 0x1117F),
    ("塔克里", 0x11680, 0x116CF),
    ("兰纳", 0x1A20, 0x1AAF),
    ("占", 0xAA00, 0xAA5F),
    ("巴厘", 0x1B00, 0x1B7F),
    ("爪哇", 0xA980, 0xA9DF),
    ("巽他", 0x1B80, 0x1BBF),
    ("巽他补充", 0x1CC0, 0x1CCF),
    ("巴塔克", 0x1BC0, 0x1BFF),
    ("隆塔拉", 0x1DC0, 0x1DFF),
    ("比心", 0x1BC0, 0x1BFF),
    ("菲律宾", 0x1700, 0x17FF),
    ("亚拉姆", 0x10840, 0x1085F),
    ("曼达安", 0x0840, 0x085F),
    ("叙利亚补充", 0x0860, 0x086F),
    ("回鹘", 0x0700, 0x074F),
    ("阿拉伯数学字母符号", 0x1EE00, 0x1EEFF),
    ("拉丁扩展-C", 0x2C60, 0x2C7F),
    ("拉丁扩展-D", 0xA720, 0xA7FF),
    ("拉丁扩展-E", 0xAB30, 0xAB6F),
    ("拉丁扩展-F", 0x10780, 0x107BF),
    ("拉丁扩展-G", 0x1DF00, 0x1DFFF),
    ("科普特", 0x2C80, 0x2CFF),
    ("科普特闰日", 0x102E0, 0x102FF),
    ("格拉哥里", 0x2C00, 0x2C5F),
    ("格拉哥里补充", 0x1E000, 0x1E02F),
    ("哥特", 0x10330, 0x1034F),
    ("古波斯楔形文字", 0x103A0, 0x103DF),
    ("乌加里特", 0x10380, 0x1039F),
    ("古南阿拉伯", 0x10A60, 0x10A7F),
    ("古北阿拉伯", 0x10A80, 0x10A9F),
    ("线形B", 0x10000, 0x100FF),
    ("线性B表意文字", 0x10080, 0x100FF),
    ("线形B音节文字", 0x10000, 0x1007F),
    ("爱琴数字", 0x10100, 0x1013F),
    ("古希腊数字", 0x10140, 0x1018F),
    ("古意大利", 0x10300, 0x1032F),
    ("塞浦路斯音节文字", 0x10800, 0x1083F),
    ("吕底亚", 0x10920, 0x1093F),
    ("卡里亚", 0x102A0, 0x102DF),
    ("吕基亚", 0x10280, 0x1029F),
    ("腓尼基", 0x10900, 0x1091F),
    ("利西亚", 0x10280, 0x1029F),
    ("古匈牙利", 0x10C80, 0x10CFF),
    ("古突厥", 0x10C00, 0x10C4F),
    ("卢米数字", 0x10E60, 0x10E7F),
    ("巴姆穆", 0xA6A0, 0xA6FF),
    ("巴姆穆补充", 0x16800, 0x16A3F),
    ("门德基卡库", 0x1E800, 0x1E8FF),
    ("瓦伊", 0xA500, 0xA63F),
    ("姆鲁", 0x18B00, 0x18CFF),
    ("诺斯特拉提克", 0x1E800, 0x1E8FF),
    ("巴萨瓦", 0x16AD0, 0x16AFF),
    ("帕豪吉苗文", 0x16B00, 0x16B5F),
    ("苗文", 0x16B00, 0x16B5F),
    ("梅德法斯林", 0x16E40, 0x16E9F),
    ("马萨伊", 0x1E800, 0x1E8FF),
    ("阿德拉姆", 0x1E900, 0x1E9FF),
    ("奥斯曼亚", 0x10480, 0x104AF),
    ("提非纳", 0x2D30, 0x2D7F),
    ("提非纳扩展", 0x2D60, 0x2D7F),
    ("恩西巴科", 0x1E800, 0x1E8FF),
    ("万恰", 0x16100, 0x1617F),
    ("札那巴札尔", 0x1800, 0x18AF),
    ("索拉僧平", 0x11180, 0x111DF),
    ("索姆拉延", 0x1A20, 0x1AAF),
    ("一般标点", 0x2000, 0x206F),
    ("补充标点", 0x2E00, 0x2E7F),
    ("上标和下标", 0x2070, 0x209F),
    ("货币符号", 0x20A0, 0x20CF),
    ("组合变音标记补充", 0x1DC0, 0x1DFF),
    ("组合半音标记符号", 0xFE20, 0xFE2F),
    ("字母式符号", 0x2100, 0x214F),
    ("数字形式", 0x2150, 0x218F),
    ("箭头", 0x2190, 0x21FF),
    ("补充箭头-A", 0x27F0, 0x27FF),
    ("补充箭头-B", 0x2900, 0x297F),
    ("补充箭头-C", 0x1F800, 0x1F8AF),
    ("杂项符号和箭头", 0x2B00, 0x2BFF),
    ("数学运算符", 0x2200, 0x22FF),
    ("补充数学运算符", 0x2A00, 0x2AFF),
    ("杂项数学符号-A", 0x27C0, 0x27EF),
    ("杂项数学符号-B", 0x2980, 0x29FF),
    ("几何图形", 0x25A0, 0x25FF),
    ("几何图形扩展", 0x1F780, 0x1F7AF),
    ("框绘字符", 0x2500, 0x257F),
    ("制表符", 0x2500, 0x257F),
    ("方块元素", 0x2580, 0x259F),
    ("杂项符号", 0x2600, 0x26FF),
    ("杂项符号和象形文字", 0x1F300, 0x1F5FF),
    ("表情符号", 0x1F600, 0x1F64F),
    ("交通和地图符号", 0x1F680, 0x1F6FF),
    ("补充符号和象形文字", 0x1F900, 0x1F9FF),
    ("符号和象形文字扩展-A", 0x1FA00, 0x1FA6F),
    ("符号和象形文字扩展-B", 0x1FA70, 0x1FAFF),
    ("麻将牌", 0x1F000, 0x1F02F),
    ("多米诺骨牌", 0x1F030, 0x1F09F),
    ("扑克牌", 0x1F0A0, 0x1F0FF),
    ("西洋棋符号", 0x1FA00, 0x1FA6F),
    ("音符", 0x1D000, 0x1D0FF),
    ("古希腊乐符", 0x1D200, 0x1D24F),
    ("拜占庭乐符", 0x1D000, 0x1D0FF),
    ("音乐符号补充", 0x1D100, 0x1D1FF),
    ("古希腊音乐记号补充", 0x1D200, 0x1D24F),
    ("萨顿书写符号", 0x1D800, 0x1DAAF),
    ("盲文图案", 0x2800, 0x28FF),
    ("控制图片", 0x2400, 0x243F),
    ("光学字符识别", 0x2440, 0x245F),
    ("封闭字母数字数字", 0x2460, 0x24FF),
    ("封闭表意文字补充", 0x1F100, 0x1F1FF),
    ("封闭字母数字补充", 0x1F100, 0x1F1FF),
    ("圈中日韩统一表意文字", 0x3220, 0x32FF),
    ("带圈中日韩字符和月份", 0x3200, 0x32FF),
    ("封闭字母数字", 0x2460, 0x24FF),
    ("带圈中日韩字符和月份补充", 0x1F200, 0x1F2FF),
    ("区域指示符号", 0x1F1E6, 0x1F1FF),
    ("代数算子", 0x27C0, 0x27EF),
    ("带圈CJK字符", 0x3200, 0x32FF),
    ("带圈字符", 0x2460, 0x24FF),
    ("装饰符号", 0x2700, 0x27BF),
    ("装饰象形文字", 0x1F650, 0x1F67F),
    ("丁贝符", 0x2700, 0x27BF),
    ("占卜符号", 0x16AC0, 0x16AEF),
    ("炼金术符号", 0x1F700, 0x1F77F),
    ("古代符号", 0x10190, 0x101CF),
    ("特殊", 0xFFF0, 0xFFFF),
    ("私用区", 0xE000, 0xF8FF),
    ("私用区补充-A", 0xF0000, 0xFFFFD),
    ("私用区补充-B", 0x100000, 0x10FFFD),
    ("变体选择符", 0xFE00, 0xFE0F),
    ("变体选择符补充", 0xE0100, 0xE01EF),
    ("标签", 0xE0000, 0xE007F),
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

    blocks_with_chars = [b for b in stats["blocks"].keys() if b != "其他"]
    print(f"区块数量：{len(blocks_with_chars)}")
    print()

    if show_language:
        print("── 语言支持 ────────────────────────")
        blocks = stats["blocks"]

        cjk_blocks = ["中日韩统一表意文字", "中日韩统一表意文字扩展A", "中日韩统一表意文字扩展B",
                      "中日韩统一表意文字扩展C", "中日韩统一表意文字扩展D", "中日韩统一表意文字扩展E",
                      "中日韩统一表意文字扩展F", "中日韩统一表意文字扩展G", "中日韩统一表意文字扩展H",
                      "中日韩统一表意文字扩展I", "中日韩兼容表意文字", "中日韩兼容表意文字补充"]
        cjk_count = sum(len(blocks.get(b, [])) for b in cjk_blocks)

        hiragana = len(blocks.get("平假名", []))
        katakana = len(blocks.get("片假名", []))

        latin = len(blocks.get("基本拉丁", []))
        latin_ext = sum(len(blocks.get(b, [])) for b in ["拉丁-1补充", "拉丁扩展-A", "拉丁扩展-B",
                                                          "拉丁扩展-C", "拉丁扩展-D", "拉丁扩展-E",
                                                          "拉丁扩展-F", "拉丁扩展-G"])

        hangul = len(blocks.get("谚文音节", []))
        hangul_jamo = len(blocks.get("朝鲜文字母", []))

        arabic = sum(len(blocks.get(b, [])) for b in ["阿拉伯", "阿拉伯补充", "阿拉伯扩展-A", "阿拉伯扩展-B"])
        hebrew = len(blocks.get("希伯来", []))
        thai = len(blocks.get("泰文", []))
        lao = len(blocks.get("老挝", []))
        tibetan = len(blocks.get("藏文", []))
        myanmar = len(blocks.get("缅甸", []))
        georgian = len(blocks.get("格鲁吉亚", [])) + len(blocks.get("格鲁吉亚补充", []))
        armenian = len(blocks.get("亚美尼亚", []))
        ethiopic = sum(len(blocks.get(b, [])) for b in ["埃塞俄比亚", "埃塞俄比亚补充", "埃塞俄比亚扩展", "埃塞俄比亚扩展-A"])

        devanagari = len(blocks.get("天城文", []))
        bengali = len(blocks.get("孟加拉", []))
        gurmukhi = len(blocks.get("古鲁穆奇", []))
        gujarati = len(blocks.get("古吉拉特", []))
        oriya = len(blocks.get("奥里亚", []))
        tamil = len(blocks.get("泰米尔", []))
        telugu = len(blocks.get("泰卢固", []))
        kannada = len(blocks.get("卡纳达", []))
        malayalam = len(blocks.get("马拉雅拉姆", []))
        sinhala = len(blocks.get("僧伽罗", []))

        cyrillic = len(blocks.get("西里尔字母", [])) + len(blocks.get("西里尔字母补充", []))
        greek = len(blocks.get("希腊和科普特", [])) + len(blocks.get("希腊扩展", []))

        khmer = len(blocks.get("高棉", []))
        khmer_symbols = len(blocks.get("高棉符号", []))

        mongolian = len(blocks.get("蒙古", []))

        if latin > 0:
            print(f"拉丁字母：{latin + latin_ext} 字符")
        if cjk_count > 0:
            print(f"中日韩文字：{cjk_count} 字符")
        if hiragana + katakana > 0:
            print(f"日文假名：{hiragana + katakana} 字符（平假名 {hiragana}，片假名 {katakana}）")
        if hangul + hangul_jamo > 0:
            print(f"韩文：{hangul + hangul_jamo} 字符（谚文音节 {hangul}，字母 {hangul_jamo}）")
        if arabic > 0:
            print(f"阿拉伯文：{arabic} 字符")
        if hebrew > 0:
            print(f"希伯来文：{hebrew} 字符")
        if thai > 0:
            print(f"泰文：{thai} 字符")
        if lao > 0:
            print(f"老挝文：{lao} 字符")
        if tibetan > 0:
            print(f"藏文：{tibetan} 字符")
        if myanmar > 0:
            print(f"缅甸文：{myanmar} 字符")
        if georgian > 0:
            print(f"格鲁吉亚文：{georgian} 字符")
        if armenian > 0:
            print(f"亚美尼亚文：{armenian} 字符")
        if ethiopic > 0:
            print(f"埃塞俄比亚文：{ethiopic} 字符")
        if devanagari > 0:
            print(f"天城文（印地语）：{devanagari} 字符")
        if bengali > 0:
            print(f"孟加拉文：{bengali} 字符")
        if gurmukhi > 0:
            print(f"古鲁穆奇文（旁遮普语）：{gurmukhi} 字符")
        if gujarati > 0:
            print(f"古吉拉特文：{gujarati} 字符")
        if oriya > 0:
            print(f"奥里亚文：{oriya} 字符")
        if tamil > 0:
            print(f"泰米尔文：{tamil} 字符")
        if telugu > 0:
            print(f"泰卢固文：{telugu} 字符")
        if kannada > 0:
            print(f"卡纳达文：{kannada} 字符")
        if malayalam > 0:
            print(f"马拉雅拉姆文：{malayalam} 字符")
        if sinhala > 0:
            print(f"僧伽罗文：{sinhala} 字符")
        if cyrillic > 0:
            print(f"西里尔字母（俄语等）：{cyrillic} 字符")
        if greek > 0:
            print(f"希腊字母：{greek} 字符")
        if khmer + khmer_symbols > 0:
            print(f"高棉文（柬埔寨）：{khmer + khmer_symbols} 字符")
        if mongolian > 0:
            print(f"蒙古文：{mongolian} 字符")

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
