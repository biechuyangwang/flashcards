# -*- coding: utf-8 -*-
"""build_vocab_db.py — 生成生词卡片 APP 词库 vocab_db.js（GitHub Pages 版路径）
从两套本地课程教案抽取生词：
  E:/claude/汉字汉语普及/教学材料/01—09_*.md  （对外汉语：Word|Pinyin|POS|English）
  E:/claude/英语普及/教学材料/01—09_*.md      （英语课程：Word|POS|中文）
输出：本目录 vocab_db.js（index.html 直接引用）
完整注释版见 生词卡片APP/build_vocab_db.py。
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path("E:/claude/英语普及/生词卡片APP")))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "bvd", "E:/claude/英语普及/生词卡片APP/build_vocab_db.py")
# 直接复用主项目的抽取逻辑：把其输出落到本目录
src = Path("E:/claude/英语普及/生词卡片APP/build_vocab_db.py").read_text(encoding="utf-8")
exec(compile(src.replace(
    'OUT = Path(__file__).resolve().parent / "app" / "vocab_db.js"',
    'OUT = Path(__file__).resolve().parent / "vocab_db.js"'), "bvd", "exec"))
