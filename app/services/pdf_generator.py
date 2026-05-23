import os
import re
from fpdf import FPDF

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _safe(text: str) -> str:
    """
    Encode to latin-1, replacing any character that can't be encoded.
    fpdf 1.7.2 only supports latin-1 internally.
    """
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _clean(text: str) -> str:
    """Remove markdown bold/italic markers and strip leading # characters."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    text = text.lstrip("#").strip()
    return _safe(text)


def generate_pdf(source_filename: str, notes_text: str, mode: str) -> str:
    """Build a PDF from notes text and return the output file path."""

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _safe("AI Generated Notes"), ln=True, align="C")
    pdf.ln(2)

    # Sub-title
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, _safe(f"Source: {source_filename}  |  Mode: {mode.capitalize()}"), ln=True)
    pdf.ln(4)

    # Divider line
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    for line in notes_text.splitlines():
        stripped = line.strip()

        if not stripped:
            pdf.ln(3)
            continue

        # Skip horizontal rule separators
        if re.match(r"^-{2,}$", stripped) or re.match(r"^={2,}$", stripped):
            pdf.ln(2)
            continue

        # Heading levels
        if stripped.startswith("###"):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 7, _clean(stripped))
            pdf.ln(1)

        elif stripped.startswith("##"):
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(0, 8, _clean(stripped))
            pdf.ln(2)

        elif stripped.startswith("#"):
            pdf.set_font("Helvetica", "B", 13)
            pdf.multi_cell(0, 9, _clean(stripped))
            pdf.ln(3)

        # Bullet points
        elif stripped.startswith(("- ", "* ")):
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, _safe(f"  - {_clean(stripped[2:])}"))

        # Numbered list
        elif re.match(r"^\d+\.", stripped):
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, _safe(f"  {_clean(stripped)}"))

        # Normal text
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, _clean(stripped))

    # Save file
    base = os.path.splitext(source_filename)[0]
    out_filename = f"{base}_notes_{mode}.pdf"
    out_path = os.path.join(OUTPUT_DIR, out_filename)
    pdf.output(out_path, "F")
    return out_path
