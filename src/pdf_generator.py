# src/pdf_generator.py
# Purpose: Create PDF client deliverables from Markdown-style report files

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os


def markdown_to_pdf(input_file, output_file):
    """Convert a simple markdown report into a PDF file."""

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()
    story = []

    with open(input_file, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        if not line:
            story.append(Spacer(1, 12))
            continue

        if line.startswith("# "):
            story.append(Paragraph(line.replace("# ", ""), styles["Title"]))
        elif line.startswith("## "):
            story.append(Paragraph(line.replace("## ", ""), styles["Heading2"]))
        elif line.startswith("### "):
            story.append(Paragraph(line.replace("### ", ""), styles["Heading3"]))
        else:
            clean_line = line.replace("**", "")
            story.append(Paragraph(clean_line, styles["BodyText"]))

        story.append(Spacer(1, 8))

    doc.build(story)

    print(f"[+] PDF created: {output_file}")


if __name__ == "__main__":
    markdown_to_pdf(
        "reports/executive_summary.md",
        "reports/executive_summary.pdf"
    )

    markdown_to_pdf(
        "reports/audit_report.md",
        "reports/audit_report.pdf"
    )