"""범용 교재 PDF 빌더 — Autobook Series 양식.

사용법:
    python build_pdf.py "책이름" [--subtitle "부제"] [--keywords "키워드"] [--out "경로"]

기본 동작:
    - 02_Books/{책이름}/curriculum.json 로드
    - 02_Books/{책이름}/wikidocs/pages/ 의 토픽 .md 렌더링
    - 출력: {repo_root}/{책이름}.pdf
"""
import argparse
import json
import re
import sys
from pathlib import Path

from fpdf import FPDF

REPO_ROOT = Path(__file__).resolve().parents[3]


def parse_args():
    p = argparse.ArgumentParser(description='교재 PDF 빌더')
    p.add_argument('book', help='02_Books/ 하위의 책 디렉토리 이름')
    p.add_argument('--subtitle', default='', help='표지 부제 (없으면 빈 줄)')
    p.add_argument('--keywords', default='', help='표지 키워드 줄')
    p.add_argument('--year', default='2026', help='표지 연도')
    p.add_argument('--series', default='A U T O B O O K  S E R I E S', help='시리즈명')
    p.add_argument('--out', default='', help='출력 PDF 경로 (기본: 레포 루트/{책이름}.pdf)')
    p.add_argument('--title-size', type=float, default=40.0, help='표지 제목 폰트 크기')
    return p.parse_args()


def has_hangul(s):
    return any('\uAC00' <= c <= '\uD7A3' for c in s)


def build(args):
    book_dir = REPO_ROOT / '02_Books' / args.book
    pages_dir = book_dir / 'wikidocs' / 'pages'
    curriculum_path = book_dir / 'curriculum.json'

    if not curriculum_path.exists():
        print(f'[ERR] curriculum.json not found: {curriculum_path}', file=sys.stderr)
        sys.exit(1)
    if not pages_dir.exists():
        print(f'[ERR] pages dir not found: {pages_dir}', file=sys.stderr)
        sys.exit(1)

    with open(curriculum_path, encoding='utf-8') as f:
        cur = json.load(f)

    title = cur.get('title') or args.book
    out_path = Path(args.out) if args.out else (REPO_ROOT / f'{args.book}.pdf')

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
    def fit_title_lines(text, max_size, min_size=18.0, max_width_mm=None):
        """제목이 표지 폭을 넘지 않도록 폰트 크기를 줄이고, 필요하면 두 줄로 쪼갠다."""
        if max_width_mm is None:
            max_width_mm = pdf.w - pdf.l_margin - pdf.r_margin
        # 1) 한 줄로 들어갈 수 있는 최대 폰트 크기 탐색
        size = max_size
        while size >= min_size:
            pdf.set_font('M', 'B', size)
            if pdf.get_string_width(text) <= max_width_mm:
                return [text], size
            size -= 1
        # 2) 한 줄로 안 되면 분할 후보 (':' 우선, 그다음 공백)
        candidates = []
        if ':' in text:
            head, tail = text.split(':', 1)
            candidates.append((head.strip(), tail.strip()))
        if ' ' in text:
            words = text.split(' ')
            mid = len(words) // 2
            candidates.append((' '.join(words[:mid]), ' '.join(words[mid:])))
        # 후보 중 두 줄 모두 max_size에 가장 잘 맞는 폰트 크기를 채택
        best = None
        for line1, line2 in candidates:
            if not line1 or not line2:
                continue
            s = max_size
            while s >= min_size:
                pdf.set_font('M', 'B', s)
                w1 = pdf.get_string_width(line1)
                w2 = pdf.get_string_width(line2)
                if w1 <= max_width_mm and w2 <= max_width_mm:
                    if best is None or s > best[2]:
                        best = ([line1, line2], s, s)
                    break
                s -= 1
        if best:
            return best[0], best[1]
        # 3) 그래도 안 되면 min_size 한 줄 (잘림 감수)
        return [text], min_size

    pdf.add_page()
    pdf.set_y(95)
    pdf.set_font('M', '', 11)
    pdf.cell(0, 10, args.series, align='C')
    title_lines, title_size = fit_title_lines(title, args.title_size)
    line_h = title_size * 0.5
    title_block_h = line_h * len(title_lines)
    pdf.set_y(120 - title_block_h / 2)
    pdf.set_font('M', 'B', title_size)
    for line in title_lines:
        pdf.cell(0, line_h, line, align='C', new_x='LMARGIN', new_y='NEXT')
    if args.subtitle:
        pdf.set_y(138)
        pdf.set_font('M', '', 14)
        pdf.cell(0, 8, args.subtitle, align='C')
    if args.keywords:
        pdf.set_y(146 if args.subtitle else 138)
        pdf.set_font('M', '', 11)
        pdf.cell(0, 8, args.keywords, align='C')
    pdf.set_y(170)
    pdf.set_font('M', '', 10)
    pdf.cell(0, 8, args.year, align='C')

    # ============== TOC ==============
    pdf.add_page()
    pdf.set_y(25)
    pdf.set_font('M', 'B', 24)
    pdf.cell(0, 12, '목차', align='C')
    pdf.ln(20)
    intro_md = pages_dir / '00-들어가며.md'
    if intro_md.exists():
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

    # ============== Body helpers ==============
    def write_paragraph(text, font_face='M', font_style='', font_size=10.3, line_height=5.5):
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
                cleaned = re.sub(r'`([^`]+)`', r'\1', part)
                pdf.write(line_height, cleaned)
        pdf.ln(line_height)

    def write_md_body(md_text):
        lines = md_text.split('\n')
        while lines and not lines[0].strip():
            lines.pop(0)
        if lines and lines[0].lstrip().startswith('# '):
            lines.pop(0)
        in_code = False
        code_buf = []

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
            write_paragraph(raw, line_height=5.6)
        flush_code()

    def topic_md_path(topic_id):
        parts = topic_id.split('.')
        if len(parts) != 3:
            return None
        pp, ss, tt = parts
        pattern = f"{int(pp):02d}-{int(ss):02d}-{int(tt):02d}-*.md"
        matches = list(pages_dir.glob(pattern))
        return matches[0] if matches else None

    # ============== 들어가며 ==============
    if intro_md.exists():
        pdf.add_body_page()
        pdf.set_y(20)
        pdf.set_font('M', 'B', 24)
        pdf.cell(0, 12, '0. 들어가며', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(8)
        write_md_body(intro_md.read_text(encoding='utf-8'))

    # ============== Phase 본문 ==============
    missing = []
    for phase in cur['phases']:
        pdf.add_body_page()
        pdf.set_y(33)
        pdf.set_font('M', 'B', 24)
        pdf.cell(0, 12, f"{phase['id']} {phase['title']}", new_x='LMARGIN', new_y='NEXT')
        pdf.ln(6)
        if phase.get('exit_capability'):
            write_paragraph(phase['exit_capability'], line_height=5.6)
        pdf.ln(2)
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

        for section in phase['sections']:
            pdf.set_font('M', 'B', 14.5)
            pdf.cell(0, 10, f"{section['id']} {section['title']}", new_x='LMARGIN', new_y='NEXT')
            pdf.ln(1)
            pdf.set_font('M', '', 10.3)
            pdf.cell(0, 6, '이 섹션의 토픽과 학습 목표는 다음과 같습니다.', new_x='LMARGIN', new_y='NEXT')
            pdf.ln(1)
            for topic in section['topics']:
                obj_list = topic.get('learning_objectives') or []
                obj = obj_list[0] if obj_list else ''
                pdf.set_x(24)
                pdf.set_font('M', 'B', 10.3)
                pdf.write(5.8, f"{topic['id']} {topic['title']}")
                if obj:
                    pdf.set_font('M', '', 10.3)
                    pdf.write(5.8, f" — {obj}")
                pdf.ln(7)
            pdf.ln(4)

            for topic in section['topics']:
                md_path = topic_md_path(topic['id'])
                if not md_path:
                    missing.append(topic['id'])
                    print(f"[WARN] no md for {topic['id']}", file=sys.stderr)
                    continue
                pdf.set_font('M', 'B', 12)
                pdf.cell(0, 8, f"{topic['id']} {topic['title']}", new_x='LMARGIN', new_y='NEXT')
                pdf.ln(1)
                write_md_body(md_path.read_text(encoding='utf-8'))
                pdf.ln(3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
    size = out_path.stat().st_size
    print(f'Saved: {out_path} ({size:,} bytes)')
    if missing:
        print(f'[INFO] missing topic md: {len(missing)} ({", ".join(missing[:10])}{"..." if len(missing) > 10 else ""})')


if __name__ == '__main__':
    build(parse_args())
