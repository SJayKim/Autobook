"""에이전트 평가와 관측 PDF 빌더 — 하네스 엔지니어링 PDF와 동일 양식."""
import json
import re
from pathlib import Path
from fpdf import FPDF

BOOK_DIR = Path('C:/Users/cyon1/OneDrive/Desktop/Autobook/02_Books/에이전트 평가와 관측')
PAGES_DIR = BOOK_DIR / 'wikidocs' / 'pages'
OUT = Path('C:/Users/cyon1/OneDrive/Desktop/Autobook/에이전트 평가와 관측.pdf')

with open(BOOK_DIR / 'curriculum.json', encoding='utf-8') as f:
    cur = json.load(f)

TITLE = '에이전트 평가와 관측'
SUBTITLE = '비결정적 시스템을 프로덕션에 올리는 법'
KEYWORDS = '평가 · 관측 · 거버넌스 · 케이스 · 도입 로드맵'
YEAR = '2026'
SERIES = 'A U T O B O O K  S E R I E S'

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

# ============== Cover ==============
pdf.add_page()
pdf.set_y(95)
pdf.set_font('M', '', 11)
pdf.cell(0, 10, SERIES, align='C')
pdf.set_y(110)
pdf.set_font('M', 'B', 40)
pdf.cell(0, 18, TITLE, align='C')
pdf.set_y(138)
pdf.set_font('M', '', 14)
pdf.cell(0, 8, SUBTITLE, align='C')
pdf.set_y(146)
pdf.cell(0, 8, KEYWORDS, align='C')
pdf.set_y(170)
pdf.set_font('M', '', 10)
pdf.cell(0, 8, YEAR, align='C')

# ============== TOC ==============
def render_toc(start_new=True):
    if start_new:
        pdf.add_page()
    pdf.set_y(25)
    pdf.set_font('M', 'B', 24)
    pdf.cell(0, 12, '목차', align='C')
    pdf.ln(20)
    # 들어가며
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
                pdf.cell(0, 5.5, f"{topic['id']} {topic['title']}", new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

render_toc()

# ============== Body ==============
def write_paragraph(text, font_face='M', font_style='', font_size=10.3, line_height=5.5):
    """write a paragraph with **bold** segments inline."""
    pdf.set_font(font_face, font_style, font_size)
    parts = re.split(r'(\*\*[^*\n]+\*\*)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            pdf.set_font(font_face, 'B', font_size)
            pdf.write(line_height, part[2:-2])
        else:
            pdf.set_font(font_face, font_style, font_size)
            # remove inline `code` ticks for simplicity (keep text)
            cleaned = re.sub(r'`([^`]+)`', r'\1', part)
            pdf.write(line_height, cleaned)
    pdf.ln(line_height)


def write_md_body(md_text):
    """render markdown body: drop first '# ...' heading, then process lines."""
    lines = md_text.split('\n')
    # drop leading blanks then first '# ' heading line
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].lstrip().startswith('# '):
        lines.pop(0)
    # process
    in_code = False
    code_buf = []

    def has_hangul(s):
        return any('\uAC00' <= c <= '\uD7A3' for c in s)

    def flush_code():
        if not code_buf:
            return
        for cl in code_buf:
            cl_safe = cl.replace('\t', '    ')
            pdf.set_x(20)
            if has_hangul(cl_safe):
                pdf.set_font('M', '', 9)
                pdf.cell(0, 4.6, cl_safe, new_x='LMARGIN', new_y='NEXT')
            else:
                pdf.set_font('Mono', '', 8.5)
                pdf.cell(0, 4.2, cl_safe, new_x='LMARGIN', new_y='NEXT')
        code_buf.clear()
        pdf.set_font('M', '', 10.3)
        pdf.ln(2)

    for raw in lines:
        if raw.strip().startswith('```'):
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
                pdf.ln(1)
            continue
        if in_code:
            code_buf.append(raw)
            continue
        if not raw.strip():
            pdf.ln(2.5)
            continue
        # heading inside body? (we already dropped the top-level title)
        write_paragraph(raw, line_height=5.6)
    flush_code()


def topic_md_path(topic_id):
    pp, ss, tt = topic_id.split('.')
    pattern = f"{int(pp):02d}-{int(ss):02d}-{int(tt):02d}-*.md"
    matches = list(PAGES_DIR.glob(pattern))
    return matches[0] if matches else None

# 들어가며
pdf.add_body_page()
pdf.set_y(20)
pdf.set_font('M', 'B', 24)
pdf.cell(0, 12, '0. 들어가며', new_x='LMARGIN', new_y='NEXT')
pdf.ln(8)
intro = (PAGES_DIR / '00-들어가며.md').read_text(encoding='utf-8')
write_md_body(intro)

# 각 Phase
for phase in cur['phases']:
    pdf.add_body_page()
    # Phase heading
    pdf.set_y(33)
    pdf.set_font('M', 'B', 24)
    pdf.cell(0, 12, f"{phase['id']} {phase['title']}", new_x='LMARGIN', new_y='NEXT')
    pdf.ln(6)
    # exit_capability
    write_paragraph(phase.get('exit_capability', ''), line_height=5.6)
    pdf.ln(2)
    # section list
    pdf.set_font('M', '', 10.3)
    pdf.cell(0, 6, '이 Phase는 다음 섹션으로 구성됩니다.', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)
    for section in phase['sections']:
        pdf.set_x(24)
        pdf.set_font('M', '', 10.3)
        pdf.cell(0, 6, f"{section['id']} {section['title']}", new_x='LMARGIN', new_y='NEXT')
        for topic in section['topics']:
            pdf.set_x(30)
            pdf.cell(0, 5.5, f"{topic['id']} {topic['title']}", new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    # 각 Section
    for section in phase['sections']:
        # 섹션 헤더
        pdf.set_font('M', 'B', 14.5)
        pdf.cell(0, 10, f"{section['id']} {section['title']}", new_x='LMARGIN', new_y='NEXT')
        pdf.ln(1)
        pdf.set_font('M', '', 10.3)
        pdf.cell(0, 6, '이 섹션의 토픽과 학습 목표는 다음과 같습니다.', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(1)
        for topic in section['topics']:
            obj = topic['learning_objectives'][0] if topic['learning_objectives'] else ''
            pdf.set_x(24)
            pdf.set_font('M', 'B', 10.3)
            pdf.write(5.8, f"{topic['id']} {topic['title']}")
            pdf.set_font('M', '', 10.3)
            pdf.write(5.8, f" — {obj}")
            pdf.ln(7)
        pdf.ln(4)

        # 각 Topic 본문
        for topic in section['topics']:
            md_path = topic_md_path(topic['id'])
            if not md_path:
                print(f"[WARN] no md for {topic['id']}")
                continue
            pdf.set_font('M', 'B', 12)
            pdf.cell(0, 8, f"{topic['id']} {topic['title']}", new_x='LMARGIN', new_y='NEXT')
            pdf.ln(1)
            text = md_path.read_text(encoding='utf-8')
            write_md_body(text)
            pdf.ln(3)

OUT.parent.mkdir(parents=True, exist_ok=True)
pdf.output(str(OUT))
print(f'Saved: {OUT} ({OUT.stat().st_size:,} bytes)')
