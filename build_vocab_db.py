# -*- coding: utf-8 -*-
"""
build_vocab_db.py — 从两套课程教案抽取生词，生成生词卡片 APP 预置词库 vocab_db.js
来源：
  E:/claude/汉字汉语普及/教学材料/01—09_*.md  （对外汉语：Word|Pinyin|POS|English 四列）
  E:/claude/英语普及/教学材料/01—09_*.md      （英语课程：Word|POS|中文 三列）
输出：app/vocab_db.js  →  const VOCAB_DB = {meta, courses:{cn:{1..9:[...]}, en:{...}}}
条目：{w, py|pos, pos|cn, en|cn2, lesson:"L1-03"}
用法：python build_vocab_db.py
"""
import re
import sys
from pathlib import Path

CN_ROOT = Path("E:/claude/汉字汉语普及/教学材料")
EN_ROOT = Path("E:/claude/英语普及/教学材料")
YUE_ROOT = Path("E:/claude/粤语普及/教学材料")
YUE_ROOT = Path("E:/claude/粤语普及/教学材料")
OUT = Path(__file__).resolve().parent / "app" / "vocab_db.js"

PH = re.compile(r"【(?:IMG|AUD)-[^】]+】")


def tables(body):
    t, cur = [], []
    for ln in body.splitlines():
        if ln.strip().startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c or "---") for c in cells):
                continue
            cur.append(cells)
        elif cur:
            t.append(cur); cur = []
    if cur:
        t.append(cur)
    return t


def cn_split(text, n):
    parts = [x.strip(" ★") for x in re.split(r"\s*/\s*", text)]
    return parts if len(parts) == n else None


def parse_cn_lesson(lv, no, block):
    """对外汉语教案生词表：| 词 | 拼音 | 词性 | 英译 |"""
    head = re.split(r"(?m)^###", block)[0]
    secs = re.split(r"(?m)^###\s*([^#\n]+?)\s*\*{0,2}\s*$", block)
    items = []
    for i in range(1, len(secs), 2):
        name = secs[i].split("（")[0].strip()
        if not name.startswith(("生词表", "核心词汇")):
            continue
        for t in tables(secs[i + 1]):
            if not t or "词" not in t[0][0]:
                continue
            ncol = len(t[0])  # 4列=词|拼音|词性|英译（初等）；3列=词|拼音|英译（中等核心词汇）
            for cells in t[1:]:
                if len(cells) < 3:
                    continue
                if any(("不进词表" in c) or c == "—" for c in cells[:2]):
                    continue
                cells = list(cells) + ["", ""]
                if ncol >= 4:
                    w_, p_, pos_, en_ = cells[0], cells[1], cells[2], cells[3]
                else:
                    w_, p_, pos_, en_ = cells[0], cells[1], "", cells[2]
                w_, p_ = w_.replace("**", ""), p_.replace("**", "")
                ws = [x.strip(" ★") for x in re.split(r"\s*/\s*", w_)]
                ps = [x.strip() for x in re.split(r"\s*/\s*", p_)]
                ens = [x.strip() for x in re.split(r"\s*/\s*", en_.replace("**", ""))]
                if len(ws) == 1:
                    items.append({"w": ws[0], "py": p_.strip(), "pos": pos_.strip(),
                                  "en": en_.replace("**", "").strip(), "lesson": f"L{lv}-{no:02d}"})
                elif len(ws) == len(ps):
                    ens2 = ens if len(ens) == len(ws) else [en_.strip()] + [""] * (len(ws) - 1)
                    for a, b, c in zip(ws, ps, ens2):
                        items.append({"w": a, "py": b, "pos": pos_.strip(), "en": c,
                                      "lesson": f"L{lv}-{no:02d}"})
                elif len(w_.replace("★", "").strip()) == len(p_.split()) and len(w_) > 8:
                    chars = w_.replace("★", "").strip()
                    ens2 = ens if len(ens) == len(chars) else [en_.strip()] + [""] * (len(chars) - 1)
                    m = {"〇": "0", "一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
                         "六": "6", "七": "7", "八": "8", "九": "9", "十": "10", "百": "100",
                         "红": "red", "黄": "yellow", "蓝": "blue", "绿": "green", "黑": "black", "白": "white"}
                    for ch, pyn, enx in zip(chars, p_.split(), ens2):
                        items.append({"w": ch, "py": pyn, "pos": pos_.strip(),
                                      "en": m.get(ch, enx), "lesson": f"L{lv}-{no:02d}"})
    return items


def parse_en_lesson(lv, no, block):
    """英语教案生词表：| Word | 词性 | 中文 |"""
    secs = re.split(r"(?m)^###\s*([^#\n]+?)\s*\*{0,2}\s*$", block)
    items = []
    for i in range(1, len(secs), 2):
        name = secs[i].split("（")[0].strip()
        if not name.startswith(("生词表", "核心词汇")):
            continue
        for t in tables(secs[i + 1]):
            if not t or t[0][0] != "词":
                continue
            for cells in t[1:]:
                if len(cells) < 3:
                    continue
                w_, pos_, cn_ = cells[0], cells[1], cells[2]
                ws = [x.strip(" ★") for x in re.split(r"\s*/\s*", w_.replace("**", ""))]
                cns = [x.strip() for x in re.split(r"\s*/\s*", cn_)]
                if len(ws) == 1:
                    items.append({"w": ws[0], "pos": pos_.strip(), "cn": cn_.strip(),
                                  "lesson": f"L{lv}-{no:02d}"})
                elif len(ws) == len(cns):
                    for a, c in zip(ws, cns):
                        items.append({"w": a, "pos": pos_.strip(), "cn": c, "lesson": f"L{lv}-{no:02d}"})
                else:
                    items.append({"w": " / ".join(ws), "pos": pos_.strip(), "cn": cn_.strip(),
                                  "lesson": f"L{lv}-{no:02d}"})
    return items




def parse_yue_lesson(lv, no, block):
    """粤语教案生词表：| 词 | 粤拼 | 词性 | 普通话 |（4列）或 | 词 | 粤拼 | 普通话 |（3列）"""
    secs = re.split(r"(?m)^###\s*([^#\n]+?)\s*\*{0,2}\s*$", block)
    items = []
    for i in range(1, len(secs), 2):
        name = secs[i].split("（")[0].strip()
        if not name.startswith(("生词表", "核心词汇")):
            continue
        for t in tables(secs[i + 1]):
            if not t or t[0][0] != "词":
                continue
            ncol = len(t[0])
            for cells in t[1:]:
                if len(cells) < 3:
                    continue
                cells = list(cells) + ["", ""]
                if ncol >= 4:
                    w_, py_, pos_, cn_ = cells[0], cells[1], cells[2], cells[3]
                else:
                    w_, py_, pos_, cn_ = cells[0], cells[1], "", cells[2]
                ws = [x.strip(" ★") for x in re.split(r"\s*/\s*", w_.replace("**", ""))]
                pys = [x.strip() for x in re.split(r"\s*/\s*", py_)]
                cns = [x.strip() for x in re.split(r"\s*/\s*", cn_)]
                base = {"pos": pos_.strip(), "lesson": f"L{lv}-{no:02d}"}
                if len(ws) == 1:
                    items.append({"w": ws[0], "py": py_.strip(), "cn": cn_.strip(), **base})
                elif len(ws) == len(pys) == len(cns):
                    for a, b, c in zip(ws, pys, cns):
                        items.append({"w": a, "py": b, "cn": c, **base})
                elif len(ws) == len(pys):
                    cns2 = cns if len(cns) == len(ws) else [cn_.strip()] + [""] * (len(ws) - 1)
                    for a, b, c in zip(ws, pys, cns2):
                        items.append({"w": a, "py": b, "cn": c, **base})
                else:
                    items.append({"w": " / ".join(ws), "py": py_.strip(), "cn": cn_.strip(), **base})
    return items


def lesson_blocks(root):
    for lv in range(1, 10):
        f = next(root.glob(f"{lv:02d}_*.md"), None)
        if not f:
            continue
        text = f.read_text(encoding="utf-8")
        for b in re.split(r"(?m)^## (?=第 \d+ 课|专题 \d+)", text)[1:]:
            hm = re.match(r"(第 (\d+) 课|专题 (\d+))", b)
            if hm:
                yield lv, int(hm.group(2) or hm.group(3)), b


def main():
    db = {"meta": {"generated": "2026-09-13",
                   "sources": ["汉字汉语普及/教学材料（对外汉语 115 课）", "英语普及/教学材料（英语 115 课）", "粤语普及/教学材料（粤语 115 课）"]},
          "courses": {"cn": {}, "en": {}, "yue": {}}}
    stat = {"cn": 0, "en": 0, "yue": 0}
    for lv, no, b in lesson_blocks(CN_ROOT):
        items = parse_cn_lesson(lv, no, b)
        db["courses"]["cn"].setdefault(str(lv), []).extend(items)
        stat["cn"] += len(items)
    for lv, no, b in lesson_blocks(EN_ROOT):
        items = parse_en_lesson(lv, no, b)
        db["courses"]["en"].setdefault(str(lv), []).extend(items)
        stat["en"] += len(items)
    for lv, no, b in lesson_blocks(YUE_ROOT):
        items = parse_yue_lesson(lv, no, b)
        db["courses"].setdefault("yue", {}).setdefault(str(lv), []).extend(items)
        stat["yue"] = stat.get("yue", 0) + len(items)
    for lv, no, b in lesson_blocks(YUE_ROOT):
        items = parse_yue_lesson(lv, no, b)
        db["courses"].setdefault("yue", {}).setdefault(str(lv), []).extend(items)
        stat["yue"] = stat.get("yue", 0) + len(items)
    # 去重（同级别内同词同课保留一条；同词异课保留多处出现以供"按课学习"）
    for c in db["courses"]:
        for lv in db["courses"][c]:
            seen, out = set(), []
            for it in db["courses"][c][lv]:
                k = (it["w"].lower(), it["lesson"])
                if k in seen:
                    continue
                seen.add(k)
                out.append(it)
            db["courses"][c][lv] = out
            stat[c] -= len(db["courses"][c][lv]) and 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    js = "const VOCAB_DB = " + __import__("json").dumps(db, ensure_ascii=False, separators=(",", ":")) + ";"
    OUT.write_text(js, encoding="utf-8")
    print(f"OK cn={stat['cn']} en={stat['en']} total={stat['cn']+stat['en']} -> {OUT.name} ({OUT.stat().st_size//1024}KB)")
    for c in ("cn", "en", "yue"):
        for lv in sorted(db["courses"].get(c, {}), key=int):
            print(f"  {c} L{lv}: {len(db['courses'][c][lv])}")


if __name__ == "__main__":
    main()
