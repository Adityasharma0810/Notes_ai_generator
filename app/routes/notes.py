import os
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.services.notes_service import process_file
from app.services.pdf_generator import generate_pdf
from app.services.groq_service import generate_notes
from app.services.translate_service import translate_text, SUPPORTED_LANGUAGES
from app.services.tts_service import generate_audio
from app.utils.chunk_text import chunk_text

router = APIRouter()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
AUDIO_DIR = "outputs/audio"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".pptx", ".png", ".jpg", ".jpeg"}


@router.get("/languages")
def get_languages():
    """Return supported languages."""
    return {"languages": SUPPORTED_LANGUAGES}


@router.post(
    "/generate-notes",
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "required": ["files", "mode"],
                        "properties": {
                            "files": {
                                "type": "array",
                                "items": {"type": "string", "format": "binary"},
                                "description": "Upload PDF, PPT, or image files"
                            },
                            "mode": {
                                "type": "string",
                                "enum": ["detailed", "important", "mixed"],
                                "description": "Notes type: detailed, important (MCQ), or mixed"
                            },
                            "language": {
                                "type": "string",
                                "enum": ["en", "hi", "bn", "gu", "kn", "ml", "mr", "od", "pa", "ta", "te"],
                                "description": "Output language for notes (default: en)"
                            }
                        }
                    }
                }
            },
            "required": True
        }
    }
)
async def generate_notes_route(
    files: List[UploadFile] = File(...),
    mode: str = Form(...),
    language: str = Form("en")
):
    if mode not in ("detailed", "important", "mixed"):
        raise HTTPException(status_code=400, detail="mode must be: detailed, important, or mixed")

    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language. Choose from: {list(SUPPORTED_LANGUAGES.keys())}")

    all_notes = []

    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Allowed: pdf, pptx, png, jpg, jpeg"
            )

        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Extract text
        extracted_text = process_file(file_path)

        if not extracted_text.strip():
            all_notes.append({
                "file": file.filename,
                "notes": None,
                "pdf_url": None,
                "audio_url": None,
                "warning": "No text could be extracted from this file."
            })
            continue

        # Generate notes in English via Groq
        chunks = chunk_text(extracted_text, chunk_size=3000)
        combined_notes = ""
        try:
            for chunk in chunks:
                combined_notes += generate_notes(chunk, mode) + "\n\n"
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Notes generation failed: {str(e)}")
        combined_notes = combined_notes.strip()

        # Translate to target language if not English
        final_notes = translate_text(combined_notes, language) if language != "en" else combined_notes

        # Generate PDF in target language
        pdf_path = generate_pdf(file.filename, final_notes, mode, language)
        pdf_filename = os.path.basename(pdf_path)

        # Generate TTS audio (non-blocking — skip on failure)
        base_name = os.path.splitext(file.filename)[0]
        audio_path = generate_audio(final_notes, language, base_name)
        audio_url = f"/download-audio/{os.path.basename(audio_path)}" if audio_path else None

        all_notes.append({
            "file": file.filename,
            "notes": final_notes,
            "pdf_url": f"/download-notes/{pdf_filename}",
            "audio_url": audio_url,
            "language": language
        })

    return {
        "success": True,
        "mode": mode,
        "language": language,
        "results": all_notes
    }


@router.get("/download-notes/{filename}")
async def download_notes(filename: str):
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(OUTPUT_DIR, safe_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(path=file_path, media_type="application/pdf", filename=safe_filename)


@router.get("/download-audio/{filename}")
async def download_audio(filename: str):
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(AUDIO_DIR, safe_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(path=file_path, media_type="audio/wav", filename=safe_filename)
