import os
import pytesseract
from PIL import Image

# On Windows locally, set the path if tesseract is installed
# On Linux (Render), tesseract is on PATH automatically
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_image_text(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text
