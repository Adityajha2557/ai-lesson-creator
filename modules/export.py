import re
from pathlib import Path
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parents[1] / "outputs"
OUT.mkdir(exist_ok=True)

def slug(text):
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", text).strip("_")[:60] or "lesson"

def export_docx(title, lesson, research, research_qc, instructional_qc):
    doc = Document()
    doc.add_heading(title, 0)
    for line in lesson.splitlines():
        if line.startswith("# "): doc.add_heading(line[2:], 1)
        elif line.startswith("## "): doc.add_heading(line[3:], 2)
        elif line.startswith("### "): doc.add_heading(line[4:], 3)
        elif line.strip(): doc.add_paragraph(line.replace("**", "").replace("`", ""))
    doc.add_heading("Research references", 1)
    for item in research:
        if item.get("url"):
            doc.add_paragraph(f'{item.get("source_type")}: {item.get("title")} — {item.get("url")}')
    doc.add_heading("QC Layer 1 — Research and factual accuracy", 1)
    doc.add_paragraph(research_qc or "Not run.")
    doc.add_heading("QC Layer 2 — Instructional quality", 1)
    doc.add_paragraph(instructional_qc or "Not run.")
    path = OUT / f"{slug(title)}.docx"
    doc.save(path)
    return path

def export_pdf(title, lesson, research, research_qc, instructional_qc):
    path = OUT / f"{slug(title)}.pdf"
    styles = getSampleStyleSheet()
    story = [Paragraph(escape(title), styles["Title"]), Spacer(1, 12)]
    for line in lesson.splitlines():
        line = line.strip()
        if not line:
            story.append(Spacer(1, 5))
        elif line.startswith("# "):
            story.append(Paragraph(escape(line[2:]), styles["Heading1"]))
        elif line.startswith("## "):
            story.append(Paragraph(escape(line[3:]), styles["Heading2"]))
        elif line.startswith("### "):
            story.append(Paragraph(escape(line[4:]), styles["Heading3"]))
        else:
            story.append(Paragraph(escape(line.replace("**", "").replace("`", "")), styles["BodyText"]))
            story.append(Spacer(1, 4))
    story.append(Paragraph("Research references", styles["Heading1"]))
    for item in research:
        if item.get("url"):
            story.append(Paragraph(escape(f'{item.get("source_type")}: {item.get("title")} — {item.get("url")}'), styles["BodyText"]))
    for heading, content in [
        ("QC Layer 1 — Research and factual accuracy", research_qc),
        ("QC Layer 2 — Instructional quality", instructional_qc)
    ]:
        story.append(Paragraph(heading, styles["Heading1"]))
        for line in (content or "Not run.").splitlines():
            if line.strip():
                story.append(Paragraph(escape(line), styles["BodyText"]))
    SimpleDocTemplate(str(path), pagesize=A4).build(story)
    return path
