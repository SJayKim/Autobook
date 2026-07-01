# -*- coding: utf-8 -*-
"""AI 엔지니어 영어 면접 말하기 — PDF 빌더.
기본 build_pdf.py 양식 + 표/헤더/blockquote/리스트/이모지 렌더링 확장."""
import json
import re
from pathlib import Path
from fpdf import FPDF

BOOK_DIR = Path('C:/Users/cyon1/OneDrive/Desktop/Autobook/Books/AI 엔지니어 영어 면접 말하기')
PAGES_DIR = BOOK_DIR / 'wikidocs' / 'pages'
OUT = BOOK_DIR / 'AI 엔지니어 영어 면접 말하기.pdf'

with open(BOOK_DIR / 'curriculum.json', encoding='utf-8') as f:
    cur = json.load(f)

TITLE = 'AI 엔지니어 영어 면접 말하기'
SUBTITLE = '내 프로젝트로 만드는 실전 영어 답변'
KEYWORDS = '자기소개 · 8개 프로젝트 정답지 · 꼬리질문 · 표현·발음'
YEAR = '2026'
SERIES = 'A U T O B O O K   S E R I E S'

EMOJI = re.compile('[\U0001F000-\U0001FAFF\U0001F1E6-\U0001F1FF\U00002B00-\U00002BFF️‍]')


def clean_inline(text):
    text = text.replace('🟢', '●').replace('🟡', '●').replace('🔴', '●').replace('🔵', '●')
    text = EMOJI.sub('', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)            # `code` -> code
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # [t](url) -> t
    text = re.sub(r'  +', ' ', text)
    return text


def has_hangul(s):
    return any('가' <= c <= '힣' for c in s)


class Book(FPDF):
    def __init__(self):
        super().__init__(format='A4')
        self.add_font('M', '', 'C:/Windows/Fonts/malgun.ttf')
        self.add_font('M', 'B', 'C:/Windows/Fonts/malgunbd.ttf')
        self.add_font('Mono', '', 'C:/Windows/Fonts/consola.ttf')
        self.set_margins(18, 25, 18)
        self.set_auto_page_break(True, margin=22)
        self.body_started = False
        self.first_body_page = None

    def footer(self):
        if self.body_started and self.first_body_page is not None:
            body_no = self.page_no() - self.first_body_page + 1
            if body_no >= 1:
                self.set_y(-12)
                self.set_font('M', '', 9)
                self.set_text_color(0, 0, 0)
                self.cell(0, 6, str(body_no), align='C')

    def add_body_page(self):
        self.add_page()
        if not self.body_started:
            self.body_started = True
            self.first_body_page = self.page_no()


pdf = Book()
USABLE = pdf.w - pdf.l_margin - pdf.r_margin


def fit_size(text, max_w, start, floor, style='B'):
    size = start
    pdf.set_font('M', style, size)
    while pdf.get_string_width(text) > max_w and size > floor:
        size -= 1
        pdf.set_font('M', style, size)
    return size


# ============== Cover ==============
pdf.add_page()
pdf.set_y(92)
pdf.set_font('M', '', 11)
pdf.set_text_color(90, 90, 90)
pdf.cell(0, 10, SERIES, align='C')
pdf.set_text_color(0, 0, 0)
pdf.set_y(108)
tsize = fit_size(TITLE, USABLE - 4, 40, 22)
pdf.set_font('M', 'B', tsize)
pdf.cell(0, 18, TITLE, align='C')
pdf.set_y(140)
pdf.set_font('M', '', 14)
pdf.cell(0, 8, SUBTITLE, align='C')
pdf.set_y(150)
ksize = fit_size(KEYWORDS, USABLE - 10, 12, 9, style='')
pdf.set_font('M', '', ksize)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 8, KEYWORDS, align='C')
pdf.set_text_color(0, 0, 0)
pdf.set_y(174)
pdf.set_font('M', '', 10)
pdf.cell(0, 8, YEAR, align='C')

# ============== TOC ==============
pdf.add_page()
pdf.set_y(25)
pdf.set_font('M', 'B', 24)
pdf.cell(0, 12, '목차', align='C')
pdf.ln(20)
pdf.set_x(18)
pdf.set_font('M', 'B', 11.5)
pdf.cell(0, 6.5, '0. 들어가며', new_x='LMARGIN', new_y='NEXT')
pdf.ln(2)
for phase in cur['phases']:
    pdf.set_x(18)
    pdf.set_font('M', 'B', 11.5)
    pdf.cell(0, 7, f"{phase['id']} {phase['title']}", new_x='LMARGIN', new_y='NEXT')
    for section in phase['sections']:
        pdf.set_x(23)
        pdf.set_font('M', 'B', 10.2)
        pdf.cell(0, 6, f"{section['id']} {section['title']}", new_x='LMARGIN', new_y='NEXT')
        for topic in section['topics']:
            pdf.set_x(28)
            pdf.set_font('M', '', 9.7)
            pdf.multi_cell(0, 5.5, f"{topic['id']} {topic['title']}", new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)


# ============== Markdown body renderer ==============
def render_inline(text, size=10.3, lh=5.6):
    """write one line with inline **bold**; assumes cursor at desired x."""
    parts = re.split(r'(\*\*[^*]+\*\*)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            pdf.set_font('M', 'B', size)
            pdf.write(lh, clean_inline(part[2:-2]))
        else:
            pdf.set_font('M', '', size)
            pdf.write(lh, clean_inline(part))
    pdf.ln(lh)


def render_heading(s):
    level = len(s) - len(s.lstrip('#'))
    title = clean_inline(s.lstrip('#').replace('**', '').strip())
    pdf.ln(2.5)
    if level <= 2:
        size, gap = 12.5, 7.0
    elif level == 3:
        size, gap = 11.0, 6.2
    else:
        size, gap = 10.5, 5.8
    pdf.set_font('M', 'B', size)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, gap, title, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(1)


def render_hr():
    pdf.ln(1.5)
    y = pdf.get_y()
    pdf.set_draw_color(205, 209, 216)
    pdf.set_line_width(0.3)
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.set_line_width(0.2)
    pdf.set_draw_color(0, 0, 0)
    pdf.ln(2.5)


def render_blockquote(block):
    orig = pdf.l_margin
    left = orig + 5
    content = [re.sub(r'^>\s?', '', ln) for ln in block]
    pdf.set_left_margin(left)
    for cl in content:
        cs = cl.strip()
        if not cs:
            pdf.ln(2)
            continue
        y0 = pdf.get_y()
        m = re.match(r'^[-*]\s+(.*)$', cs)
        if m:
            pdf.set_x(left + 3)
            pdf.set_font('M', '', 9.9)
            pdf.write(5.2, '· ')
            render_inline(m.group(1), size=9.9, lh=5.2)
        else:
            pdf.set_x(left)
            render_inline(cs, size=10.0, lh=5.3)
        y1 = pdf.get_y()
        if y1 > y0:
            pdf.set_draw_color(120, 140, 175)
            pdf.set_line_width(0.9)
            pdf.line(orig + 2, y0 + 0.5, orig + 2, y1 - 0.8)
            pdf.set_line_width(0.2)
            pdf.set_draw_color(0, 0, 0)
    pdf.set_left_margin(orig)
    pdf.set_x(orig)
    pdf.ln(2.2)


def render_list_item(raw):
    m = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', raw)
    orig = pdf.l_margin
    lead = len(m.group(1))
    depth = 0 if lead < 2 else 1
    x = orig + 2 + depth * 5
    bullet = '· ' if m.group(2) in ('-', '*') else (m.group(2) + ' ')
    pdf.set_left_margin(x + 4)
    pdf.set_x(x)
    pdf.set_font('M', '', 10.2)
    pdf.write(5.5, bullet)
    render_inline(m.group(3), size=10.2, lh=5.5)
    pdf.set_left_margin(orig)
    pdf.set_x(orig)


def render_code(block):
    pdf.ln(1)
    for cl in block:
        cl_safe = cl.replace('\t', '    ')
        pdf.set_x(20)
        if has_hangul(cl_safe):
            pdf.set_font('M', '', 9)
            pdf.cell(0, 4.6, cl_safe, new_x='LMARGIN', new_y='NEXT')
        else:
            pdf.set_font('Mono', '', 8.3)
            pdf.cell(0, 4.2, cl_safe, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)


def render_table(block):
    rows = []
    for ln in block:
        cells = [c.strip() for c in ln.strip().strip('|').split('|')]
        rows.append(cells)
    has_header = False
    if len(rows) >= 2 and rows[1] and all(re.match(r'^:?-{2,}:?$', c) for c in rows[1] if c != ''):
        rows.pop(1)
        has_header = True
    ncol = max(len(r) for r in rows)
    if ncol == 2:
        ws = [USABLE * 0.40, USABLE * 0.60]
    elif ncol == 3:
        ws = [USABLE * 0.30, USABLE * 0.35, USABLE * 0.35]
    elif ncol == 4:
        ws = [USABLE * 0.22, USABLE * 0.26, USABLE * 0.26, USABLE * 0.26]
    else:
        ws = [USABLE / ncol] * ncol
    line_h, pad = 4.8, 1.3
    pdf.ln(1)
    pdf.set_auto_page_break(False)
    for ri, row in enumerate(rows):
        cells = [clean_inline(c.replace('**', '')) for c in row] + [''] * (ncol - len(row))
        is_head = has_header and ri == 0
        style = 'B' if is_head else ''
        pdf.set_font('M', style, 8.8)
        maxl = 1
        for ci, c in enumerate(cells):
            lns = pdf.multi_cell(ws[ci] - 2 * pad, line_h, c if c else ' ',
                                 dry_run=True, output="LINES", wrapmode="CHAR")
            maxl = max(maxl, len(lns))
        rh = maxl * line_h + 2 * pad
        if pdf.get_y() + rh > pdf.h - 22:
            pdf.add_page()
        x0 = pdf.l_margin
        y0 = pdf.get_y()
        for ci, c in enumerate(cells):
            if is_head:
                pdf.set_fill_color(234, 238, 244)
                pdf.set_draw_color(200, 205, 212)
                pdf.rect(x0, y0, ws[ci], rh, style='FD')
            else:
                pdf.set_draw_color(212, 216, 222)
                pdf.rect(x0, y0, ws[ci], rh)
            pdf.set_xy(x0 + pad, y0 + pad)
            pdf.set_font('M', style, 8.8)
            pdf.multi_cell(ws[ci] - 2 * pad, line_h, c, border=0, align='L',
                           new_x='RIGHT', new_y='TOP', max_line_height=line_h, wrapmode="CHAR")
            x0 += ws[ci]
        pdf.set_xy(pdf.l_margin, y0 + rh)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_auto_page_break(True, margin=22)
    pdf.ln(2.5)


def write_md_body(md_text):
    lines = md_text.split('\n')
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].lstrip().startswith('# '):
        lines.pop(0)
    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        s = raw.strip()
        if s.startswith('```'):
            i += 1
            block = []
            while i < n and not lines[i].strip().startswith('```'):
                block.append(lines[i])
                i += 1
            i += 1
            render_code(block)
            continue
        if s.startswith('|'):
            block = []
            while i < n and lines[i].strip().startswith('|'):
                block.append(lines[i].strip())
                i += 1
            render_table(block)
            continue
        if s.startswith('>'):
            block = []
            while i < n and lines[i].strip().startswith('>'):
                block.append(lines[i].strip())
                i += 1
            render_blockquote(block)
            continue
        if not s:
            pdf.ln(2.3)
            i += 1
            continue
        if s.startswith('#'):
            render_heading(s)
            i += 1
            continue
        if len(s) >= 3 and set(s) <= set('-'):
            render_hr()
            i += 1
            continue
        if re.match(r'^(\s*)([-*]|\d+\.)\s+', raw):
            render_list_item(raw)
            i += 1
            continue
        pdf.set_x(pdf.l_margin)
        render_inline(s)
        i += 1


def topic_md_path(topic_id):
    pp, ss, tt = topic_id.split('.')
    pattern = f"{int(pp):02d}-{int(ss):02d}-{int(tt):02d}-*.md"
    matches = list(PAGES_DIR.glob(pattern))
    return matches[0] if matches else None


# ============== 들어가며 ==============
pdf.add_body_page()
pdf.set_y(20)
pdf.set_font('M', 'B', 24)
pdf.cell(0, 12, '0. 들어가며', new_x='LMARGIN', new_y='NEXT')
pdf.ln(8)
intro = (PAGES_DIR / '00-들어가며.md').read_text(encoding='utf-8')
write_md_body(intro)

# ============== Phases ==============
for phase in cur['phases']:
    pdf.add_body_page()
    pdf.set_y(33)
    pdf.set_font('M', 'B', 24)
    pdf.multi_cell(0, 12, f"{phase['id']} {phase['title']}", new_x='LMARGIN', new_y='NEXT')
    pdf.ln(6)
    pdf.set_font('M', '', 10.3)
    pdf.set_x(pdf.l_margin)
    render_inline(phase.get('exit_capability', ''))
    pdf.ln(2)
    pdf.set_font('M', '', 10.3)
    pdf.cell(0, 6, '이 Phase는 다음 섹션으로 구성됩니다.', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)
    for section in phase['sections']:
        pdf.set_x(24)
        pdf.set_font('M', 'B', 10.3)
        pdf.cell(0, 6, f"{section['id']} {section['title']}", new_x='LMARGIN', new_y='NEXT')
        for topic in section['topics']:
            pdf.set_x(30)
            pdf.set_font('M', '', 10.3)
            pdf.multi_cell(0, 5.5, f"{topic['id']} {topic['title']}", new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    for section in phase['sections']:
        pdf.set_font('M', 'B', 14.5)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 10, f"{section['id']} {section['title']}", new_x='LMARGIN', new_y='NEXT')
        pdf.ln(1)
        pdf.set_font('M', '', 10.3)
        pdf.cell(0, 6, '이 섹션의 토픽과 학습 목표는 다음과 같습니다.', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(1)
        for topic in section['topics']:
            obj = topic['learning_objectives'][0] if topic['learning_objectives'] else ''
            pdf.set_left_margin(24)
            pdf.set_x(24)
            pdf.set_font('M', 'B', 10.3)
            pdf.write(5.8, f"{topic['id']} {topic['title']}")
            pdf.set_font('M', '', 10.3)
            pdf.write(5.8, f" — {obj}")
            pdf.ln(7)
            pdf.set_left_margin(18)
        pdf.ln(4)

        for topic in section['topics']:
            md_path = topic_md_path(topic['id'])
            if not md_path:
                print(f"[WARN] no md for {topic['id']}")
                continue
            pdf.ln(2)
            pdf.set_font('M', 'B', 13)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 8, f"{topic['id']} {topic['title']}", new_x='LMARGIN', new_y='NEXT')
            pdf.ln(1)
            text = md_path.read_text(encoding='utf-8')
            write_md_body(text)
            pdf.ln(3)

OUT.parent.mkdir(parents=True, exist_ok=True)
pdf.output(str(OUT))
print(f'Saved: {OUT} ({OUT.stat().st_size:,} bytes)')
