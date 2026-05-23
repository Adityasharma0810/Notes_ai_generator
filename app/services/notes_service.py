import os
import base64
import logging

import pdfplumber
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

from app.services.ppt_service import extract_ppt_text

load_dotenv()
logger = logging.getLogger(__name__)

# Load first available Groq key for vision
_GROQ_KEYS = [
    os.getenv("GROQ_API_KEY_1", ""),
    os.getenv("GROQ_API_KEY_2", ""),
    os.getenv("GROQ_API_KEY_3", ""),
    os.getenv("GROQ_API_KEY", ""),
]
_GROQ_KEYS = [k.strip() for k in _GROQ_KEYS if k.strip()]

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def _image_to_base64(image: Image.Image) -> str:
    """Convert PIL image to base64 JPEG string."""
    import io
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _groq_vision_ocr(image: Image.Image, key: str) -> str:
    """Use Groq vision model to extract text from an image."""
    client = Groq(api_key=key)
    b64 = _image_to_base64(image)
    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                },
                {
                    "type": "text",
                    "text": (
                        "Extract ALL text from this image exactly as written. "
                        "Preserve structure, headings, bullet points, and formulas. "
                        "Output only the extracted text, nothing else."
                    )
                }
            ]
        }],
        max_tokens=2048,
    )
    return response.choices[0].message.content.strip()


def _ocr_image_with_groq(image: Image.Image) -> str:
    """Try each Groq key for vision OCR."""
    for key in _GROQ_KEYS:
        try:
            return _groq_vision_ocr(image, key)
        except Exception as e:
            logger.warning(f"Groq vision OCR failed with key: {e}")
    return ""


def _ocr_pdf_with_groq(file_path: str) -> str:
    """Render each PDF page as image and OCR with Groq vision."""
    text = ""
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(file_path)
        for i, page in enumerate(pdf):
            try:
                bitmap = page.render(scale=150 / 72)
                pil_image = bitmap.to_pil()
                page_text = _ocr_image_with_groq(pil_image)
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

        # If nothing extracted, it's a scanned PDF — use Groq vision OCR
        if not text.strip():
            logger.info(f"No text in PDF, using Groq vision OCR: {file_path}")
            text = _ocr_pdf_with_groq(file_path)

        return text

    elif ext == ".pptx":
        return extract_ppt_text(file_path)

    elif ext in (".png", ".jpg", ".jpeg"):
        # Use Groq vision for image OCR
        image = Image.open(file_path)
        return _ocr_image_with_groq(image)

    return ""
