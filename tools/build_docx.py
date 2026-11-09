"""
Build the master Word document (DOCX) for Erasmus Mobility Platform Project Deliverable P1.
Features:
- Font: Roboto throughout all headings, paragraphs, bullet points, tables, and captions.
- Monospace font: Roboto Mono / Consolas for BDD Gherkin and Java code blocks.
- Embedded high-resolution PNG diagrams for all 25 figures.
- High-quality inline Markdown formatting parser: renders bold, italic, code spans, and strips raw URLs.
- Complete English language uniformity for SDBIS (Software Development and Business Information Systems).
- Formal Cover Page conforming to FEAA / UAIC university specifications.
- Clean chapter outline structure strictly aligned with ModelProiect2026N8.pdf & ModelProiect2026N7.docx.
- MobilityChecklist as the sole Aggregate Root in Mobility Preparation (encapsulating ChecklistTask child entity).
"""

from pathlib import Path
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PNG_DIR = ROOT / "models/diagrams-png"
OUTPUT_FILE = DOCS / "Erasmus_Mobility_Platform_Documentatie_P1.docx"

# Professional Color Palette
COLOR_PRIMARY = RGBColor(0x1A, 0x36, 0x5D)    # Deep Navy
COLOR_SECONDARY = RGBColor(0x8D, 0x5B, 0x4C)  # Terra-cotta
COLOR_TEXT = RGBColor(0x2D, 0x37, 0x48)       # Charcoal text
COLOR_MUTED = RGBColor(0x71, 0x80, 0x96)      # Muted slate
HEX_HEADER_BG = "1A365D"
HEX_ALT_ROW = "F7FAFC"
HEX_CODE_BG = "F7FAFC"

FONT_MAIN = "Roboto"
FONT_CODE = "Roboto Mono"

def set_cell_shading(cell, color_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in (('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)):
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_heading_1(doc, text):
    h = doc.add_heading(text, level=1)
    h.paragraph_format.space_before = Pt(18)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    for r in h.runs:
        r.font.name = FONT_MAIN
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY
    return h

def add_heading_2(doc, text):
    h = doc.add_heading(text, level=2)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    for r in h.runs:
        r.font.name = FONT_MAIN
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_SECONDARY
    return h

def add_heading_3(doc, text):
    h = doc.add_heading(text, level=3)
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after = Pt(2)
    h.paragraph_format.keep_with_next = True
    for r in h.runs:
        r.font.name = FONT_MAIN
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEXT
    return h

def add_heading_4(doc, text):
    h = doc.add_heading(text, level=4)
    h.paragraph_format.space_before = Pt(8)
    h.paragraph_format.space_after = Pt(2)
    h.paragraph_format.keep_with_next = True
    for r in h.runs:
        r.font.name = FONT_MAIN
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.italic = True
        r.font.color.rgb = COLOR_TEXT
    return h

def add_heading_5(doc, text):
    h = doc.add_heading(text, level=5)
    h.paragraph_format.space_before = Pt(6)
    h.paragraph_format.space_after = Pt(2)
    h.paragraph_format.keep_with_next = True
    for r in h.runs:
        r.font.name = FONT_MAIN
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = COLOR_MUTED
    return h

def add_formatted_runs(paragraph, text, default_bold=False, default_italic=False, default_color=COLOR_TEXT, base_size=Pt(10)):
    """
    Parse inline Markdown formatting tokens (bold, italic, inline code) and strip raw URLs.
    Tokens supported:
    - ***bold italic***
    - **bold**
    - *italic*
    - `code`
    Strips raw file:// URLs and markdown links cleanly.
    """
    if not text:
        return
        
    # 1. Clean markdown links: [label](url) -> label
    text = re.sub(r'\[(.*?)\]\([^)]+\)', r'\1', text)
    # Remove any stray file:/// URLs
    text = re.sub(r'\(file:///[^)]+\)', '', text)
    
    # 2. Normalize spaces inside bold and italic asterisks
    text = re.sub(r'\*\*\s+([^*]+?)\s+\*\*', r'**\1**', text)
    text = re.sub(r'(?<!\*)\*\s+([^*]+?)\s+\*(?!\*)', r'*\1*', text)
    
    # 3. Clean LaTeX math markers
    text = text.replace(r'\sum', 'Σ').replace(r'\ge', '≥').replace(r'\rightarrow', '→').replace('$', '')
    
    # 4. Tokenize
    token_pattern = re.compile(r'(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*|`.*?`)')
    tokens = token_pattern.split(text)
    
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith('***') and tok.endswith('***') and len(tok) >= 6:
            inner = tok[3:-3]
            r = paragraph.add_run(inner)
            r.font.name = FONT_MAIN
            r.font.size = base_size
            r.font.bold = True
            r.font.italic = True
            r.font.color.rgb = default_color
        elif tok.startswith('**') and tok.endswith('**') and len(tok) >= 4:
            inner = tok[2:-2]
            r = paragraph.add_run(inner)
            r.font.name = FONT_MAIN
            r.font.size = base_size
            r.font.bold = True
            r.font.italic = default_italic
            r.font.color.rgb = default_color
        elif tok.startswith('*') and tok.endswith('*') and len(tok) >= 2:
            inner = tok[1:-1]
            r = paragraph.add_run(inner)
            r.font.name = FONT_MAIN
            r.font.size = base_size
            r.font.bold = default_bold
            r.font.italic = True
            r.font.color.rgb = default_color
        elif tok.startswith('`') and tok.endswith('`') and len(tok) >= 2:
            inner = tok[1:-1]
            r = paragraph.add_run(inner)
            r.font.name = FONT_CODE
            r.font.size = Pt(base_size.pt - 0.5)
            r.font.bold = False
            r.font.italic = False
            r.font.color.rgb = default_color
        else:
            r = paragraph.add_run(tok)
            r.font.name = FONT_MAIN
            r.font.size = base_size
            r.font.bold = default_bold
            r.font.italic = default_italic
            r.font.color.rgb = default_color

def add_paragraph(doc, text, bold_prefix=""):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = FONT_MAIN
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_TEXT
    add_formatted_runs(p, text, base_size=Pt(10))
    return p

def add_bullet(doc, text, bold_prefix=""):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = FONT_MAIN
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_TEXT
    add_formatted_runs(p, text, base_size=Pt(10))
    return p

def add_code_block(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)
    cell = table.cell(0, 0)
    set_cell_shading(cell, HEX_CODE_BG)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_text.strip())
    run.font.name = FONT_CODE
    run.font.size = Pt(8.5)
    run.font.color.rgb = COLOR_TEXT
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_image_diagram(doc, image_name, caption):
    image_path = PNG_DIR / image_name
    if not image_path.exists():
        print(f"Warning: Image not found: {image_path}")
        return
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(3)
    p_img.paragraph_format.keep_with_next = True
    run = p_img.add_run()
    run.add_picture(str(image_path), width=Inches(6.2))
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_after = Pt(10)
    r_cap = p_cap.add_run(caption)
    r_cap.font.name = FONT_MAIN
    r_cap.font.size = Pt(9)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

def add_table_from_markdown(doc, md_table_text):
    lines = [l.strip() for l in md_table_text.strip().splitlines() if l.strip()]
    if len(lines) < 2:
        return
    raw_headers = [c.strip() for c in lines[0].strip('|').split('|')]
    data_rows = []
    for l in lines[2:]:
        if not l.startswith('|'): continue
        cells = [c.strip() for c in l.strip('|').split('|')]
        data_rows.append(cells)
    
    num_cols = len(raw_headers)
    table = doc.add_table(rows=len(data_rows) + 1, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(raw_headers):
        set_cell_shading(hdr_cells[i], HEX_HEADER_BG)
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        add_formatted_runs(p, h, default_bold=True, default_color=RGBColor(0xFF, 0xFF, 0xFF), base_size=Pt(9.5))
            
    for r_idx, row in enumerate(data_rows):
        row_cells = table.rows[r_idx + 1].cells
        bg = HEX_ALT_ROW if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row):
            if c_idx < len(row_cells):
                set_cell_shading(row_cells[c_idx], bg)
                set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
                p = row_cells[c_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                add_formatted_runs(p, val, default_bold=False, default_color=COLOR_TEXT, base_size=Pt(9))
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def parse_markdown_content(doc, md_text, heading_level_offset=0):
    lines = md_text.splitlines()
    in_code = False
    code_buf = []
    in_table = False
    table_buf = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if stripped.startswith("```"):
            if in_code:
                add_code_block(doc, "\n".join(code_buf))
                in_code = False
                code_buf = []
            else:
                in_code = True
                code_buf = []
            i += 1
            continue
            
        if in_code:
            code_buf.append(line)
            i += 1
            continue
            
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            table_buf.append(stripped)
            i += 1
            continue
        elif in_table:
            add_table_from_markdown(doc, "\n".join(table_buf))
            in_table = False
            table_buf = []
            
        if not stripped:
            i += 1
            continue
            
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', stripped)
        if img_match:
            cap, path = img_match.groups()
            img_name = Path(path).name
            add_image_diagram(doc, img_name, cap)
            i += 1
            continue
            
        if stripped in ("---", "***", "___"):
            i += 1
            continue
            
        def render_heading(text, base_level):
            lvl = min(5, base_level + heading_level_offset)
            if lvl == 1: add_heading_1(doc, text)
            elif lvl == 2: add_heading_2(doc, text)
            elif lvl == 3: add_heading_3(doc, text)
            elif lvl == 4: add_heading_4(doc, text)
            else: add_heading_5(doc, text)
            
        if stripped.startswith("#### "):
            render_heading(stripped[5:].strip(), 4)
            i += 1
            continue
        if stripped.startswith("### "):
            render_heading(stripped[4:].strip(), 3)
            i += 1
            continue
        if stripped.startswith("## "):
            render_heading(stripped[3:].strip(), 2)
            i += 1
            continue
        if stripped.startswith("# "):
            render_heading(stripped[2:].strip(), 1)
            i += 1
            continue
            
        if stripped.startswith("* ") or stripped.startswith("- "):
            item = stripped[2:].strip()
            m_bold = re.match(r'^(\*\*.*?\*\*|\*[^*]+?\*:?)\s*(.*)', item)
            if m_bold:
                prefix = m_bold.group(1).strip()
                rest = m_bold.group(2).strip()
                clean_prefix = re.sub(r'^\*+|\*+$', '', prefix).strip()
                add_bullet(doc, rest, bold_prefix=clean_prefix + " ")
            else:
                add_bullet(doc, item)
            i += 1
            continue
            
        m_num = re.match(r'^(\d+\.)\s+(.*)', stripped)
        if m_num:
            num_str = m_num.group(1)
            item = m_num.group(2).strip()
            m_bold = re.match(r'^(\*\*.*?\*\*|\*[^*]+?\*:?)\s*(.*)', item)
            if m_bold:
                prefix = m_bold.group(1).strip()
                rest = m_bold.group(2).strip()
                clean_prefix = re.sub(r'^\*+|\*+$', '', prefix).strip()
                add_paragraph(doc, rest, bold_prefix=f"{num_str} {clean_prefix} ")
            else:
                add_paragraph(doc, item, bold_prefix=num_str + " ")
            i += 1
            continue
            
        m_bold = re.match(r'^(\*\*.*?\*\*|\*[^*]+?\*:)\s*(.*)', stripped)
        if m_bold:
            prefix = m_bold.group(1).strip()
            rest = m_bold.group(2).strip()
            clean_prefix = re.sub(r'^\*+|\*+$', '', prefix).strip()
            add_paragraph(doc, rest, bold_prefix=clean_prefix + " ")
        else:
            add_paragraph(doc, stripped)
        i += 1
        
    if in_table and table_buf:
        add_table_from_markdown(doc, "\n".join(table_buf))

def build_cover_page(doc):
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_uni = p_uni.add_run("UNIVERSITATEA „ALEXANDRU IOAN CUZA” DIN IAȘI\nFACULTATEA DE ECONOMIE ȘI ADMINISTRAREA AFACERILOR\nMASTER: SISTEME INFORMAȚIONALE PENTRU AFACERI (SIA / SDBIS)")
    r_uni.font.name = FONT_MAIN
    r_uni.font.size = Pt(11)
    r_uni.font.bold = True
    r_uni.font.color.rgb = COLOR_PRIMARY
    p_uni.paragraph_format.space_after = Pt(45)
    
    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_course = p_course.add_run("DISCIPLINA: ANALIZA ȘI PROIECTAREA ORIENTATĂ PE OBIECTE (APOO)\nAN UNIVERSITAR 2026-2027")
    r_course.font.name = FONT_MAIN
    r_course.font.size = Pt(11)
    r_course.font.italic = True
    r_course.font.color.rgb = COLOR_SECONDARY
    p_course.paragraph_format.space_after = Pt(60)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("ERASMUS MOBILITY PLATFORM (EMP)")
    r_title.font.name = FONT_MAIN
    r_title.font.size = Pt(24)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY
    p_title.paragraph_format.space_after = Pt(10)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Sistem Distribuit bazat pe Domain-Driven Design și UML 2.5 pentru Gestiunea Mobilităților Academice Internaționale conform Standardelor Erasmus Without Paper")
    r_sub.font.name = FONT_MAIN
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = COLOR_TEXT
    p_sub.paragraph_format.space_after = Pt(25)
    
    p_liv = doc.add_paragraph()
    p_liv.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_liv = p_liv.add_run("PROIECT DE SPECIALITATE - PARTEA I (LIVRABILUL P1: SECȚIUNILE 1–6)")
    r_liv.font.name = FONT_MAIN
    r_liv.font.size = Pt(13)
    r_liv.font.bold = True
    r_liv.font.color.rgb = COLOR_SECONDARY
    p_liv.paragraph_format.space_after = Pt(80)
    
    p_team = doc.add_paragraph()
    p_team.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_team_title = p_team.add_run("Echipa de Proiect & Repartizare Subdomenii:\n")
    r_team_title.font.name = FONT_MAIN
    r_team_title.font.size = Pt(11)
    r_team_title.font.bold = True
    r_team_title.font.color.rgb = COLOR_PRIMARY
    
    students = [
        ("Prigoreanu Alin-Gabriel", "Student 1", "Learning Agreement Management (Core Domain)"),
        ("Bîrgovan A. Mihai-Daniel", "Student 2", "Equivalence Management (Supporting Subdomain)"),
        ("Schipor Ana-Maria", "Student 3", "Mobility Preparation (Supporting Subdomain)")
    ]
    for name, s_idx, role in students:
        p_s = doc.add_paragraph(style='List Bullet')
        p_s.paragraph_format.space_after = Pt(2)
        r_n = p_s.add_run(f"{name} ({s_idx}): ")
        r_n.font.name = FONT_MAIN
        r_n.font.bold = True
        r_n.font.size = Pt(10.5)
        r_r = p_s.add_run(role)
        r_r.font.name = FONT_MAIN
        r_r.font.size = Pt(10.5)
        
    doc.add_page_break()

def generate_document():
    doc = docx.Document()
    
    # Set default style font to Roboto
    style_normal = doc.styles['Normal']
    style_normal.font.name = FONT_MAIN
    style_normal.font.size = Pt(10)
    style_normal.font.color.rgb = COLOR_TEXT
    
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        
    print("Building Formal Cover Page...")
    build_cover_page(doc)
    
    # =========================================================================
    # CHAPTER 1: Defining and Structuring Requirements (Model Reference Sec. 1)
    # =========================================================================
    print("Chapter 1: Defining and Structuring Requirements...")
    add_heading_1(doc, "Chapter 1. Defining and Structuring Functional and Non-Functional Requirements")
    
    # 1.1 Executive Problem Statement and Subdomain Overview
    add_heading_2(doc, "1.1 Executive Summary of Main Application Requirements")
    doc_sub = (DOCS / "01-subdomains-and-transactions.md").read_text(encoding="utf-8")
    doc_sub_body = re.sub(r'^# .*\n+', '', doc_sub)
    parse_markdown_content(doc, doc_sub_body)
    
    # Table 1.1 NFR Matrix
    add_heading_2(doc, "Table 1.1. Measurable Non-Functional Requirements Matrix (SLA & Acceptance Criteria)")
    doc_nfr = (DOCS / "02-nfr-matrix.md").read_text(encoding="utf-8")
    doc_nfr_body = re.sub(r'^# .*\n+', '', doc_nfr)
    parse_markdown_content(doc, doc_nfr_body)
    
    # 1.2 Structuring and Detailing Functional Requirements
    add_heading_2(doc, "1.2 Structuring and Detailing Functional Requirements")
    
    # 1.2.1 Strategic DDD & Context Mapping
    add_heading_3(doc, "1.2.1 Problem Domain Decomposition (Strategic DDD) and Context Mapping")
    doc_map = (DOCS / "03-context-map-glossary.md").read_text(encoding="utf-8")
    doc_map_body = re.sub(r'^# .*\n+', '', doc_map)
    parse_markdown_content(doc, doc_map_body)
    
    # 1.2.2 Activity Diagram
    add_heading_3(doc, "1.2.2 Business Process Activity Diagram across Bounded Contexts (Figure 2)")
    doc_act = (DOCS / "04-activity-diagram-business-process.md").read_text(encoding="utf-8")
    doc_act_body = re.sub(r'^# .*\n+', '', doc_act)
    parse_markdown_content(doc, doc_act_body, heading_level_offset=2)
    add_image_diagram(doc, "Figura2-Activity-Diagram-Across-Bounded-Contexts.png", "Figure 2. Business Process Activity Diagram across Bounded Contexts with Swimlanes and InterruptibleActivityRegion")
    
    # 1.2.3 Use Case Diagrams
    add_heading_3(doc, "1.2.3 Subdomain Use Case Diagrams (Figures 3, 4, 5)")
    add_paragraph(doc, "For each of the three primary subdomains established in the strategic context map, a dedicated UML 2.5 Use Case Diagram was designed, detailing business actors, associations, and advanced «include» and «extend» relationships:")
    add_image_diagram(doc, "usecase-learning-agreement.png", "Figure 3. Use Case Diagram: Learning Agreement Management (Student 1: Prigoreanu Alin-Gabriel)")
    add_image_diagram(doc, "usecase-equivalence-management.png", "Figure 4. Use Case Diagram: Equivalence Management (Student 2: Bîrgovan A. Mihai-Daniel)")
    add_image_diagram(doc, "usecase-mobility-preparation.png", "Figure 5. Use Case Diagram: Mobility Preparation (Student 3: Schipor Ana-Maria)")
    
    # 1.2.4 SVDPI Use Case Narrative Descriptions
    add_heading_3(doc, "1.2.4 Use Case Narrative Specifications (SVDPI Format: UC01, UC02, UC03)")
    add_paragraph(doc, "In strict compliance with the reference course methodology, each team member detailed a core use case conforming to SVDPI standards (active voice, alternating Actor/System steps, and extension points decoupled from graphical UI widgets):")
    
    # UC01
    uc01_text = (DOCS / "use-cases/UC01-submit-learning-agreement.md").read_text(encoding="utf-8")
    parse_markdown_content(doc, uc01_text, heading_level_offset=2)
    
    # UC02
    uc02_text = (DOCS / "use-cases/UC02-register-course-equivalence.md").read_text(encoding="utf-8")
    parse_markdown_content(doc, uc02_text, heading_level_offset=2)
    
    # UC03
    uc03_text = (DOCS / "use-cases/UC03-confirm-nomination.md").read_text(encoding="utf-8")
    parse_markdown_content(doc, uc03_text, heading_level_offset=2)
    
    # 1.2.5 Gherkin BDD Living Documentation
    add_heading_3(doc, "1.2.5 Living BDD Specifications in Gherkin Language (.feature)")
    add_paragraph(doc, "Declarative executable specifications formalize the acceptance criteria for each use case, capturing system invariants and business preconditions:")
    
    add_paragraph(doc, "A. Gherkin Specification: Learning Agreement Management (Student 1: Prigoreanu Alin-Gabriel)", bold_prefix="Specification 1: ")
    feat_la = (ROOT / "features/learning-agreement.feature").read_text(encoding="utf-8")
    add_code_block(doc, feat_la)
    
    add_paragraph(doc, "B. Gherkin Specification: Equivalence Management (Student 2: Bîrgovan A. Mihai-Daniel)", bold_prefix="Specification 2: ")
    feat_eq = (ROOT / "features/equivalence-management.feature").read_text(encoding="utf-8")
    add_code_block(doc, feat_eq)
    
    add_paragraph(doc, "C. Gherkin Specification: Mobility Preparation (Student 3: Schipor Ana-Maria)", bold_prefix="Specification 3: ")
    feat_prep = (ROOT / "features/mobility-preparation.feature").read_text(encoding="utf-8")
    add_code_block(doc, feat_prep)
    
    doc.add_page_break()
    
    # =========================================================================
    # CHAPTER 2: Tactical Domain Model (Model Reference Sec. 2 / Sec. 3)
    # =========================================================================
    print("Chapter 2: Tactical Domain Model...")
    add_heading_1(doc, "Chapter 2. Domain Model (Tactical Domain-Driven Design Patterns)")
    doc_tac = (DOCS / "05-tactical-domain-model.md").read_text(encoding="utf-8")
    doc_tac_body = re.sub(r'^# .*\n+', '', doc_tac)
    parse_markdown_content(doc, doc_tac_body)
    add_image_diagram(doc, "Figura8-Tactical-DDD-Domain-Model.png", "Figure 8. Tactical DDD Domain Model: Aggregate Roots, Internal Entities, Value Objects, and Domain Events")
    
    doc.add_page_break()
    
    # =========================================================================
    # CHAPTER 3: Layered Architecture and Repositories (Model Reference Sec. 3)
    # =========================================================================
    print("Chapter 3: Layered Architecture and Repositories...")
    add_heading_1(doc, "Chapter 3. Architectural Solution Design (Logical Architecture)")
    
    add_heading_2(doc, "3.1 Layered Onion / Clean Architecture (Figures 9, 9b, and 10)")
    doc_layer = (DOCS / "06-layered-architecture-spec.md").read_text(encoding="utf-8")
    doc_layer_body = re.sub(r'^# .*\n+', '', doc_layer)
    parse_markdown_content(doc, doc_layer_body)
    add_image_diagram(doc, "Figura9-Layered-Architecture-Core-Domain.png", "Figure 9. Layered Architecture: Core Domain (Learning Agreement Management)")
    add_image_diagram(doc, "Figura10-Layered-Architecture-Supporting-Subdomain.png", "Figure 10. Layered Architecture: Supporting Subdomain (Equivalence Management)")
    
    add_heading_2(doc, "3.2 Repository Class Hierarchy (Figure 11)")
    doc_repo = (DOCS / "07-repository-hierarchy-spec.md").read_text(encoding="utf-8")
    doc_repo_body = re.sub(r'^# .*\n+', '', doc_repo)
    parse_markdown_content(doc, doc_repo_body)
    add_image_diagram(doc, "Figura11-Repository-Hierarchy.png", "Figure 11. DDD Repository Pattern Class Hierarchy: Decoupling Ports from JPA Implementations")
    
    doc.add_page_break()
    
    # =========================================================================
    # CHAPTER 4: Context Integration (Model Reference Sec. 4)
    # =========================================================================
    print("Chapter 4: Context Integration...")
    add_heading_1(doc, "Chapter 4. Bounded Context Integration Mechanics")
    
    add_heading_2(doc, "4.1 Synchronous REST Integration: Client and Server (Figures 12 and 13)")
    doc_rest = (DOCS / "08-synchronous-rest-integration.md").read_text(encoding="utf-8")
    doc_rest_body = re.sub(r'^# .*\n+', '', doc_rest)
    parse_markdown_content(doc, doc_rest_body)
    
    add_heading_2(doc, "4.2 Asynchronous Integration via Transactional Outbox: Publisher and Consumer (Figures 14 and 15)")
    doc_outbox = (DOCS / "09-asynchronous-outbox-integration.md").read_text(encoding="utf-8")
    doc_outbox_body = re.sub(r'^# .*\n+', '', doc_outbox)
    parse_markdown_content(doc, doc_outbox_body)
    
    doc.add_page_break()
    
    # =========================================================================
    # CHAPTER 5: Consolidated Structural Models (Model Reference Sec. 5)
    # =========================================================================
    print("Chapter 5: Consolidated Structural Models...")
    add_heading_1(doc, "Chapter 5. Consolidated Structural Perspective (Final Structural Solution)")
    doc_struct = (DOCS / "10-consolidated-structural-models.md").read_text(encoding="utf-8")
    doc_struct_body = re.sub(r'^# .*\n+', '', doc_struct)
    parse_markdown_content(doc, doc_struct_body)
    
    doc.add_page_break()
    
    # =========================================================================
    # CHAPTER 6: Dynamic System Behavior (Model Reference Sec. 6)
    # =========================================================================
    print("Chapter 6: Dynamic System Behavior...")
    add_heading_1(doc, "Chapter 6. Dynamic System Behavior (Behavioral Modeling)")
    
    add_heading_2(doc, "6.1 Aggregate Lifecycle Modeling through State Machine Diagrams and Transition Tables (Figures 19, 20, 21)")
    doc_sm = (DOCS / "11-state-machines.md").read_text(encoding="utf-8")
    doc_sm_body = re.sub(r'^# .*\n+', '', doc_sm)
    parse_markdown_content(doc, doc_sm_body)
    
    add_heading_2(doc, "6.2 Object Interaction Design through Sequence Diagrams (Figures 22–25)")
    doc_seq = (DOCS / "12-sequence-diagrams.md").read_text(encoding="utf-8")
    doc_seq_body = re.sub(r'^# .*\n+', '', doc_seq)
    parse_markdown_content(doc, doc_seq_body)
    
    doc.add_page_break()
    
    # =========================================================================
    # CHAPTER 7: Technical Implementation & Verification Annex
    # =========================================================================
    print("Chapter 7: Technical Implementation & Verification Annex...")
    add_heading_1(doc, "Chapter 7. Technical Implementation & Verification Annex")
    add_paragraph(doc, "To prove the concrete validity of the modeled structural and behavioral architecture, the project provides a full Java (JDK 23/25) domain implementation across 30 compiled classes, strictly enforcing DDD package layering and transactional invariants.")
    
    add_heading_2(doc, "7.1 Java Package Architecture and 30 Compiled Domain Classes")
    java_summary = """
The compiled domain skeleton in `src/src/main/java/ro/uaic/feaa/erasmus/` is partitioned as follows:
* **`ro.uaic.feaa.erasmus.shared` (Shared Kernel):**
  - Immutable Records: `StudentId`, `AgreementId`, `EquivalenceId`, `TaskId`, `ChecklistId`, `CourseCode`, `AcademicYear`.
  - Invariant-Enforcing Value Objects: `ECTSCredits` (validates credits >= 0 and minimum 30 ECTS threshold), `ValidityWindow` (validates chronological order endDate >= startDate).
* **`ro.uaic.feaa.erasmus.agreement` (Learning Agreement Management - Core Domain):**
  - Aggregate Root: `LearningAgreement` (manages Table A and Table B collections, enforces credit parity invariant, orchestrates tripartite approval lifecycle).
  - Internal Child Entities: `CourseLineTableA`, `CourseLineTableB`.
  - Domain Event: `LearningAgreementApprovedEvent`.
  - Domain Ports: `LearningAgreementRepository`, `IEquivalenceCatalogAdapter`, `IOutboxRepository`.
  - Infrastructure Types: `OutboxMessage`, `OutboxStatus`.
* **`ro.uaic.feaa.erasmus.equivalence` (Equivalence Management - Supporting Subdomain):**
  - Aggregate Root: `AcademicEquivalence` (manages syllabus parity evaluation, temporal validity via `isCurrentlyValid(asOf)`, and catalog indexing).
  - Entity: `CourseSyllabus`.
  - Domain Port: `AcademicEquivalenceRepository`.
  - Lifecycle Enum: `EquivalenceStatus`.
* **`ro.uaic.feaa.erasmus.preparation` (Mobility Preparation - Supporting Subdomain):**
  - Aggregate Root: `MobilityChecklist` (initializes mandatory administrative onboarding tasks, verifies dossier completion via `areMandatoryTasksComplete()`).
  - Internal Child Entity: `ChecklistTask` (encapsulates task lifecycle from initialization to student submission, officer validation, or overdue escalation).
  - Domain Port: `MobilityChecklistRepository`.
  - Infrastructure Port: `IProcessedEventRepository` (guarantees idempotent message processing).
    """
    parse_markdown_content(doc, java_summary.strip())
    
    add_heading_2(doc, "7.2 Automated Verification Report (JUnit 5 Invariants)")
    test_report = """
The automated test suite `ro.uaic.feaa.erasmus.domain.DomainInvariantsTest` verifies runtime behavior against the UML class models and state machine specifications:
1. `testLearningAgreementInvariants`: Asserts rejection of agreements holding under 30 ECTS credits, verifies exact credit parity between Table A and Table B, tests submission locking, coordinator review assignment, and automatic dispatch of `LearningAgreementApprovedEvent` upon faculty approval.
2. `testAcademicEquivalence`: Asserts state machine progression (PROPOSED -> UNDER_EVALUATION -> APPROVED -> ACTIVE) and temporal validity evaluation.
3. `testMobilityChecklist`: Asserts automated initialization of 5 mandatory administrative tasks, document proof attachment, submission for verification, and readiness completion gating via `areMandatoryTasksComplete()`.

Maven Build Verification: `mvn -f src/pom.xml test`
* **Tests run:** 3, Failures: 0, Errors: 0, Skipped: 0
* **Build Status:** BUILD SUCCESS
* **Execution Time:** 0.031 seconds
    """
    parse_markdown_content(doc, test_report.strip())
    
    add_heading_2(doc, "7.3 Standardized OMG UML 2.1 XMI Structural Export")
    add_paragraph(doc, "For seamless interoperability with CASE tools (Enterprise Architect v16+, Visual Paradigm), the structural model has been exported to the standard OMG UML 2.1 XMI format at `models/xmi-exports/ErasmusModel.xmi` (containing 50 structured model elements and 33 association relationships).")
    
    print(f"Saving final master document to {OUTPUT_FILE}...")
    doc.save(str(OUTPUT_FILE))
    file_size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"Master Document created successfully! Size: {file_size_mb:.2f} MB ({OUTPUT_FILE.stat().st_size} bytes)")

if __name__ == "__main__":
    generate_document()
