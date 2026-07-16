# -*- coding: utf-8 -*-
"""Agentic AI 보안 설계 전용 PDF 빌더 — Books/ 경로 대응 + 마크다운 표 렌더링.

stock build_pdf.py(02_Books 하드코딩, 표 미지원)의 한계를 우회한 책 전용 빌더.
표지·목차·들어가며·Phase/Section 개요·Topic 본문을 렌더링하고, 파이프 표는 fpdf2 table로 그린다.
"""
import json
import re
import sys
from pathlib import Path

from fpdf import FPDF

BOOK_DIR = Path("C:/Users/cyon1/OneDrive/Desktop/Autobook/Books/Agentic AI 보안 설계")
PAGES_DIR = BOOK_DIR / "wikidocs" / "pages"
CUR = json.load(open(BOOK_DIR / "curriculum.json", encoding="utf-8"))

TITLE = "Agentic AI 보안 설계"
SUBTITLE = "권한을 가진 신뢰할 수 없는 실행 주체를 다루는 법"
KEYWORDS = "OWASP ASI · MCP · Lethal Trifecta · N2SF · 방어 설계"
YEAR = "2026"
SERIES = "A U T O B O O K   S E R I E S"
OUT = BOOK_DIR / "Agentic AI 보안 설계.pdf"


def has_hangul(s):
    return any("가" <= c <= "힣" for c in s)


class Book(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.add_font("M", "", "C:/Windows/Fonts/malgun.ttf")
        self.add_font("M", "B", "C:/Windows/Fonts/malgunbd.ttf")
        self.add_font("Mono", "", "C:/Windows/Fonts/consola.ttf")
        self.set_margins(18, 22, 18)
        self.set_auto_page_break(True, margin=20)
        self.body_started = False
        self.first_body_page = None

    def footer(self):
        if self.body_started and self.first_body_page is not None:
            body_no = self.page_no() - self.first_body_page + 1
            if body_no >= 1:
                self.set_y(-12)
                self.set_font("M", "", 9)
                self.set_text_color(0, 0, 0)
                self.cell(0, 6, str(body_no), align="C")

    def add_body_page(self):
        self.add_page()
        if not self.body_started:
            self.body_started = True
            self.first_body_page = self.page_no()


pdf = Book()


# ============== Cover ==============
def fit_title_lines(text, max_size, min_size=17.0, max_width_mm=None):
    if max_width_mm is None:
        max_width_mm = pdf.w - pdf.l_margin - pdf.r_margin
    size = max_size
    while size >= min_size:
        pdf.set_font("M", "B", size)
        if pdf.get_string_width(text) <= max_width_mm:
            return [text], size
        size -= 1
    candidates = []
    if ":" in text:
        head, tail = text.split(":", 1)
        candidates.append((head.strip(), tail.strip()))
    if " " in text:
        words = text.split(" ")
        mid = len(words) // 2
        candidates.append((" ".join(words[:mid]), " ".join(words[mid:])))
    best = None
    for line1, line2 in candidates:
        if not line1 or not line2:
            continue
        s = max_size
        while s >= min_size:
            pdf.set_font("M", "B", s)
            if pdf.get_string_width(line1) <= max_width_mm and pdf.get_string_width(line2) <= max_width_mm:
                if best is None or s > best[1]:
                    best = ([line1, line2], s)
                break
            s -= 1
    if best:
        return best
    return [text], min_size


pdf.add_page()
pdf.set_y(92)
pdf.set_font("M", "", 11)
pdf.cell(0, 10, SERIES, align="C")
title_lines, title_size = fit_title_lines(TITLE, 34.0)
line_h = title_size * 0.52
pdf.set_y(118 - (line_h * len(title_lines)) / 2)
pdf.set_font("M", "B", title_size)
for ln in title_lines:
    pdf.cell(0, line_h, ln, align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_y(150)
pdf.set_font("M", "", 13)
pdf.cell(0, 8, SUBTITLE, align="C")
pdf.set_y(160)
pdf.set_font("M", "", 11)
pdf.cell(0, 8, KEYWORDS, align="C")
pdf.set_y(180)
pdf.set_font("M", "", 10)
pdf.cell(0, 8, YEAR, align="C")


# ============== TOC ==============
pdf.add_page()
pdf.set_y(24)
pdf.set_font("M", "B", 24)
pdf.cell(0, 12, "목차", align="C")
pdf.ln(16)
intro_md = PAGES_DIR / "00-들어가며.md"
if intro_md.exists():
    pdf.set_x(18)
    pdf.set_font("M", "B", 11.5)
    pdf.cell(0, 6.5, "0. 들어가며", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
for phase in CUR["phases"]:
    pdf.set_x(18)
    pdf.set_font("M", "B", 11.5)
    pdf.cell(0, 7, f"{phase['id']} {phase['title']}", new_x="LMARGIN", new_y="NEXT")
    for section in phase["sections"]:
        pdf.set_x(23)
        pdf.set_font("M", "B", 10.0)
        pdf.cell(0, 5.8, f"{section['id']} {section['title']}", new_x="LMARGIN", new_y="NEXT")
        for topic in section["topics"]:
            pdf.set_x(28)
            pdf.set_font("M", "", 9.4)
            pdf.cell(0, 5.2, f"{topic['id']} {topic['title']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)


# ============== Body helpers ==============
def write_paragraph(text, font_size=10.3, line_height=5.6):
    parts = re.split(r"(\*\*[^*\n]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            pdf.set_font("M", "B", font_size)
            pdf.write(line_height, part[2:-2])
        else:
            pdf.set_font("M", "", font_size)
            pdf.write(line_height, re.sub(r"`([^`]+)`", r"\1", part))
    pdf.ln(line_height)


def render_table(rows):
    # rows: list of list-of-cells (구분 행 이미 제거). 첫 행은 헤더.
    pdf.ln(1)
    pdf.set_font("M", "", 9.2)
    with pdf.table(
        first_row_as_headings=True,
        headings_style=__import__("fpdf").fonts.FontFace(emphasis="BOLD", fill_color=(238, 238, 238)),
        line_height=5.2,
        width=pdf.w - pdf.l_margin - pdf.r_margin,
        text_align="LEFT",
    ) as table:
        for r in rows:
            row = table.row()
            for cell in r:
                row.cell(cell)
    pdf.ln(2)


def flush_code(code_buf):
    if not code_buf:
        return
    pdf.ln(1)
    for cl in code_buf:
        cl_safe = cl.replace("\t", "    ")
        pdf.set_x(20)
        if has_hangul(cl_safe):
            pdf.set_font("M", "", 8.8)
            pdf.cell(0, 4.5, cl_safe, new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Mono", "", 8.4)
            pdf.cell(0, 4.2, cl_safe, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("M", "", 10.3)
    pdf.ln(2)


def is_table_row(line):
    return re.match(r"\s*\|.*\|\s*$", line) is not None


def is_sep_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return all(re.match(r"^:?-+:?$", c) for c in cells if c != "")


def write_md_body(md_text):
    lines = md_text.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].lstrip().startswith("# "):
        lines.pop(0)
    i = 0
    in_code = False
    code_buf = []
    while i < len(lines):
        raw = lines[i]
        if raw.strip().startswith("```"):
            if in_code:
                flush_code(code_buf)
                code_buf = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(raw)
            i += 1
            continue
        # 표 블록 감지
        if is_table_row(raw):
            block = []
            while i < len(lines) and is_table_row(lines[i]):
                block.append(lines[i])
                i += 1
            rows = []
            for bl in block:
                if is_sep_row(bl):
                    continue
                cells = [c.strip() for c in bl.strip().strip("|").split("|")]
                rows.append(cells)
            if rows:
                render_table(rows)
            continue
        if not raw.strip():
            pdf.ln(2.5)
            i += 1
            continue
        write_paragraph(raw)
        i += 1
    if in_code:
        flush_code(code_buf)


def topic_md_path(topic_id):
    a, b, c = topic_id.split(".")
    matches = list(PAGES_DIR.glob(f"{int(a):02d}-{int(b):02d}-{int(c):02d}-*.md"))
    return matches[0] if matches else None


# ============== 들어가며 ==============
if intro_md.exists():
    pdf.add_body_page()
    pdf.set_y(20)
    pdf.set_font("M", "B", 22)
    pdf.cell(0, 12, "0. 들어가며", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    write_md_body(intro_md.read_text(encoding="utf-8"))


# ============== Phase 본문 ==============
missing = []
for phase in CUR["phases"]:
    pdf.add_body_page()
    pdf.set_y(30)
    pdf.set_font("M", "B", 23)
    pdf.multi_cell(0, 11, f"{phase['id']}. {phase['title']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    if phase.get("exit_capability"):
        write_paragraph(phase["exit_capability"])
    pdf.ln(1)
    pdf.set_font("M", "", 10.3)
    pdf.cell(0, 6, "이 Phase는 다음 섹션으로 구성됩니다.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    for section in phase["sections"]:
        pdf.set_x(24)
        pdf.set_font("M", "", 10.3)
        pdf.cell(0, 5.6, f"{section['id']} {section['title']}", new_x="LMARGIN", new_y="NEXT")
        for topic in section["topics"]:
            pdf.set_x(30)
            pdf.set_font("M", "", 9.6)
            pdf.cell(0, 5.2, f"{topic['id']} {topic['title']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    for section in phase["sections"]:
        pdf.set_font("M", "B", 14.5)
        pdf.multi_cell(0, 9, f"{section['id']} {section['title']}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        pdf.set_font("M", "", 10.3)
        pdf.cell(0, 6, "이 섹션의 토픽과 학습 목표는 다음과 같습니다.", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        for topic in section["topics"]:
            objs = topic.get("learning_objectives") or []
            obj = objs[0] if objs else ""
            pdf.set_x(24)
            pdf.set_font("M", "B", 10.2)
            pdf.write(5.7, f"{topic['id']} {topic['title']}")
            if obj:
                pdf.set_font("M", "", 10.2)
                pdf.write(5.7, f" — {obj}")
            pdf.ln(6.6)
        pdf.ln(3)

        for topic in section["topics"]:
            md_path = topic_md_path(topic["id"])
            if not md_path:
                missing.append(topic["id"])
                continue
            pdf.set_font("M", "B", 12)
            pdf.multi_cell(0, 7.5, f"{topic['id']} {topic['title']}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
            write_md_body(md_path.read_text(encoding="utf-8"))
            pdf.ln(3)

OUT.parent.mkdir(parents=True, exist_ok=True)
pdf.output(str(OUT))
print(f"Saved: {OUT} ({OUT.stat().st_size:,} bytes)")
if missing:
    print(f"[INFO] missing topic md: {len(missing)} ({', '.join(missing)})")
else:
    print("[INFO] all 65 topics rendered")
