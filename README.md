# font_manager

**脚本 1 — `font_subset.py`（字体子集化）**

依赖：`pip install fonttools brotli zopfli`

```bash
# 从字体中只保留"你好世界"这几个字
python font_subset.py -i SourceHanSans.ttf -o mini.ttf -t "你好世界"

# 从文件读取字符列表，输出为 woff2
python font_subset.py -i input.otf -o output.woff2 -f chars.txt
```

**脚本 2 — `font_to_image.py`（字符导出图片）**

依赖：`pip install Pillow`

```bash
# 每个字符单独一张透明背景 PNG
python font_to_image.py -f mini.ttf -t "你好世界" -o output_dir/ --mode single

# 所有字符合并到一张网格图（带 Unicode 码点标签）
python font_to_image.py -f mini.ttf -t "Hello你好" -o grid.png --mode combined

# 自定义：红色文字、白底、字号 256
python font_to_image.py -f mini.ttf -t "ABC" -o out/ --mode single \
    --size 256 --color "#FF0000" --bg "#FFFFFF"
```

两个脚本可以串联使用：先用脚本 1 提取需要的字符生成小字体，再用脚本 2 将其渲染为图片。
