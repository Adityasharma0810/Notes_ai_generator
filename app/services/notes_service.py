import os

import pdfplumber
import pytesseract
from PIL import Image

from app.services.ppt_service import extract_ppt_text

# On Windows locally, set the path if tesseract is installed
# On Linux (Render), tesseract is on PATH automatically
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def _ocr_pdf(file_path: str) -> str:
    """Convert each PDF page to an image and run OCR on it."""
    text = ""
    try:
        # pypdfium2 is already installed — use it to render pages
        import pypdfium2 as pdfium

        pdf = pdfium.PdfDocument(file_path)
        for page in pdf:
            # Render at 200 DPI for decent OCR accuracy
            bitmap = page.render(scale=200 / 72)
            pil_image = bitmap.to_pil()
            page_text = pytesseract.image_to_string(pil_image)
            if page_text.strip():
                text += page_text + "\n"
        pdf.close()
    except Exception:
        # Fallback: try pdf2image if pypdfium2 fails
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(file_path, dpi=200)
            for img in images:
                page_text = pytesseract.image_to_string(img)
                if page_text.strip():
                    text += page_text + "\n"
        except Exception:
            pass
    return text


def process_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        # Try text extraction first (fast, works for digital PDFs)
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

        # If nothing extracted, the PDF is scanned — fall back to OCR
        if not text.strip():
            text = _ocr_pdf(file_path)

        return text

    elif ext == ".pptx":
        return extract_ppt_text(file_path)

    elif ext in (".png", ".jpg", ".jpeg"):
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)

    return ""
