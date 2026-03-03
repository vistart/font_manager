#!/usr/bin/env python3
"""
字体渲染工具：使用指定字体将字符导出为图片。

依赖安装：
    pip install Pillow

用法：
    # 每个字符单独导出为一张图片
    python font_to_image.py -f 字体.ttf -t "你好世界" -o output_dir/ --mode single

    # 所有字符渲染到一张图片上
    python font_to_image.py -f 字体.ttf -t "Hello你好" -o output.png --mode combined

    # 自定义样式
    python font_to_image.py -f 字体.ttf -t "ABC" -o out/ --mode single \
        --size 128 --color "#FF0000" --bg "#FFFFFF" --padding 20
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def render_single_chars(
    font_path: str,
    characters: str,
    output_dir: str,
    font_size: int = 128,
    color: str = "#000000",
    bg_color: str | None = None,
    padding: int = 16,
    image_format: str = "png",
) -> list[str]:
    """
    将每个字符分别渲染为单独的图片文件。

    参数:
        font_path:    字体文件路径
        characters:   要渲染的字符串
        output_dir:   输出目录
        font_size:    字体大小（像素）
        color:        字体颜色（十六进制）
        bg_color:     背景色（None 表示透明）
        padding:      内边距（像素）
        image_format: 输出格式 png / jpg / bmp

    返回:
        生成的文件路径列表
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    font = ImageFont.truetype(font_path, font_size)
    saved_files = []

    for i, char in enumerate(characters):
        # 测量字符边界
        bbox = font.getbbox(char)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        img_w = text_w + padding * 2
        img_h = text_h + padding * 2

        # 创建画布（透明或指定背景色）
        if bg_color:
            img = Image.new("RGB", (img_w, img_h), bg_color)
        else:
            img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))

        draw = ImageDraw.Draw(img)
        # 绘制文字，偏移量补偿 bbox 的 origin
        x = padding - bbox[0]
        y = padding - bbox[1]
        draw.text((x, y), char, font=font, fill=color)

        # 文件名：使用 Unicode 码点命名，避免特殊字符问题
        codepoint = f"U+{ord(char):04X}"
        filename = f"{i:03d}_{codepoint}.{image_format}"
        filepath = out / filename
        img.save(filepath)
        saved_files.append(str(filepath))
        print(f"  [{codepoint}] '{char}' → {filename}  ({img_w}×{img_h})")

    return saved_files


def render_combined(
    font_path: str,
    characters: str,
    output_path: str,
    font_size: int = 128,
    color: str = "#000000",
    bg_color: str = "#FFFFFF",
    padding: int = 16,
    columns: int = 0,
    cell_gap: int = 8,
    show_label: bool = True,
) -> str:
    """
    将所有字符渲染到一张图片上（网格布局）。

    参数:
        font_path:   字体文件路径
        characters:  要渲染的字符串
        output_path: 输出文件路径
        font_size:   字体大小（像素）
        color:       字体颜色
        bg_color:    背景色
        padding:     整体内边距
        columns:     每行列数（0=自动）
        cell_gap:    单元格间距
        show_label:  是否在字符下方显示 Unicode 码点标签

    返回:
        输出文件路径
    """
    font = ImageFont.truetype(font_path, font_size)

    # 计算单元格尺寸（取所有字符中最大的边界）
    max_w, max_h = 0, 0
    for char in characters:
        bbox = font.getbbox(char)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        max_w = max(max_w, w)
        max_h = max(max_h, h)

    label_height = 0
    label_font = None
    if show_label:
        label_size = max(12, font_size // 6)
        try:
            label_font = ImageFont.truetype(font_path, label_size)
        except Exception:
            label_font = ImageFont.load_default()
        label_height = label_size + 4

    cell_w = max_w + cell_gap * 2
    cell_h = max_h + cell_gap * 2 + label_height

    # 确定网格布局
    n = len(characters)
    if columns <= 0:
        import math
        columns = max(1, min(n, int(math.ceil(math.sqrt(n)))))
    rows = max(1, (n + columns - 1) // columns)

    img_w = columns * cell_w + padding * 2
    img_h = rows * cell_h + padding * 2

    img = Image.new("RGB", (img_w, img_h), bg_color)
    draw = ImageDraw.Draw(img)

    for idx, char in enumerate(characters):
        row, col = divmod(idx, columns)
        cx = padding + col * cell_w
        cy = padding + row * cell_h

        # 绘制单元格边框（浅灰色）
        draw.rectangle(
            [cx, cy, cx + cell_w - 1, cy + cell_h - label_height - 1],
            outline="#E0E0E0",
        )

        # 居中绘制字符
        bbox = font.getbbox(char)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = cx + (cell_w - tw) // 2 - bbox[0]
        ty = cy + (cell_h - label_height - th) // 2 - bbox[1]
        draw.text((tx, ty), char, font=font, fill=color)

        # 绘制标签
        if show_label and label_font:
            label = f"U+{ord(char):04X}"
            lbbox = label_font.getbbox(label)
            lw = lbbox[2] - lbbox[0]
            lx = cx + (cell_w - lw) // 2 - lbbox[0]
            ly = cy + cell_h - label_height
            draw.text((lx, ly), label, font=label_font, fill="#888888")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    print(f"  合并图片已保存 → {output_path}  ({img_w}×{img_h})")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="使用指定字体将字符渲染为图片")
    parser.add_argument("-f", "--font", required=True, help="字体文件路径")
    parser.add_argument("-t", "--text", required=True, help="要渲染的字符")
    parser.add_argument("-o", "--output", required=True, help="输出路径（目录或文件）")
    parser.add_argument(
        "--mode",
        choices=["single", "combined"],
        default="single",
        help="single=每字一图，combined=合并到一张图（默认 single）",
    )
    parser.add_argument("--size", type=int, default=128, help="字体大小，默认 128")
    parser.add_argument("--color", default="#000000", help="字体颜色，默认黑色")
    parser.add_argument("--bg", default=None, help="背景色（single 模式默认透明，combined 默认白色）")
    parser.add_argument("--padding", type=int, default=16, help="内边距，默认 16")
    parser.add_argument("--columns", type=int, default=0, help="combined 模式每行列数，0=自动")
    parser.add_argument("--format", default="png", help="图片格式，默认 png")
    parser.add_argument("--no-label", action="store_true", help="combined 模式不显示码点标签")
    args = parser.parse_args()

    if not Path(args.font).exists():
        print(f"错误：字体文件不存在 → {args.font}", file=sys.stderr)
        sys.exit(1)

    print(f"字体：{args.font}")
    print(f"字符：{args.text}")
    print(f"模式：{args.mode}")
    print()

    if args.mode == "single":
        bg = args.bg  # None → 透明
        files = render_single_chars(
            font_path=args.font,
            characters=args.text,
            output_dir=args.output,
            font_size=args.size,
            color=args.color,
            bg_color=bg,
            padding=args.padding,
            image_format=args.format,
        )
        print(f"\n共生成 {len(files)} 张图片")

    elif args.mode == "combined":
        bg = args.bg or "#FFFFFF"
        render_combined(
            font_path=args.font,
            characters=args.text,
            output_path=args.output,
            font_size=args.size,
            color=args.color,
            bg_color=bg,
            padding=args.padding,
            columns=args.columns,
            show_label=not args.no_label,
        )


if __name__ == "__main__":
    main()
