import os
import io
import base64
import logging

import pdfplumber
import requests
from PIL import Image
from dotenv import load_dotenv

from app.services.ppt_service import extract_ppt_text

load_dotenv()
logger = logging.getLogger(__name__)

OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "")
OCR_SPACE_URL = "https://api.ocr.space/parse/image"


def _image_to_base64(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _ocr_space_image(image: Image.Image) -> str:
    """Send image to OCR.space and return extracted text."""
    try:
        b64 = _image_to_base64(image)
        payload = {
            "base64Image": f"data:image/jpeg;base64,{b64}",
            "apikey": OCR_SPACE_API_KEY,
            "language": "eng",
            "isOverlayRequired": False,
            "detectOrientation": True,
            "scale": True,
            "OCREngine": 2,  # Engine 2 is better for printed text
        }
        response = requests.post(OCR_SPACE_URL, data=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get("IsErroredOnProcessing"):
            logger.warning(f"OCR.space error: {result.get('ErrorMessage')}")
            return ""

        parsed = result.get("ParsedResults", [])
        return "\n".join(p.get("ParsedText", "") for p in parsed).strip()

    except Exception as e:
        logger.warning(f"OCR.space failed: {e}")
        return ""


def _ocr_pdf(file_path: str) -> str:
    """Render each PDF page as image and OCR with OCR.space."""
    text = ""
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(file_path)
        for i, page in enumerate(pdf):
            try:
                bitmap = page.render(scale=150 / 72)
                pil_image = bitmap.to_pil()
                page_text = _ocr_space_image(pil_image)
                if page_text:
                    text += f"\n--- Page {i+1} ---\n{page_text}\n"
            except Exception as e:
                logger.warning(f"Page {i+1} OCR failed: {e}")
        pdf.close()
    except Exception as e:
        logger.warning(f"PDF rendering failed: {e}")
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

        # If nothing extracted, it's a scanned PDF — use OCR.space
        if not text.strip():
            logger.info(f"No text in PDF, using OCR.space: {file_path}")
            text = _ocr_pdf(file_path)

        return text

    elif ext == ".pptx":
        return extract_ppt_text(file_path)

    elif ext in (".png", ".jpg", ".jpeg"):
        image = Image.open(file_path)
        return _ocr_space_image(image)

    return ""
