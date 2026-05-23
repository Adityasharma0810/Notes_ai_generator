import os
from typing import List

import requests as http_requests
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.services.notes_service import process_file
from app.services.pdf_generator import generate_pdf
from app.services.sarvam_service import generate_notes
from app.utils.chunk_text import chunk_text

router = APIRouter()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".pptx", ".png", ".jpg", ".jpeg"}


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
                                "description": "Notes type:\n- detailed: Full explanations, examples, definitions\n- important: Pointer notes for MCQ/exam revision (bullet points only)\n- mixed: Mix of both detailed and pointer notes"
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
    files: List[UploadFile] = File(..., description="Upload PDF, PPT, or image files"),
    mode: str = Form(...)
):
    if mode not in ("detailed", "important", "mixed"):
        raise HTTPException(
            status_code=400,
            detail="Invalid mode. Choose one of: 'detailed' (full notes), 'important' (MCQ pointer notes), 'mixed' (both)"
        )

    all_notes = []

    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}' for '{file.filename}'. Allowed: pdf, pptx, png, jpg, jpeg"
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
                "warning": "No text could be extracted from this file."
            })
            continue

        # Chunk + generate notes
        chunks = chunk_text(extracted_text, chunk_size=3000)
        combined_notes = ""
        try:
            for chunk in chunks:
                combined_notes += generate_notes(chunk, mode) + "\n\n"
        except http_requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            if status == 402:
                raise HTTPException(
                    status_code=402,
                    detail="Sarvam API has no credits. Please top up at dashboard.sarvam.ai"
                )
            raise HTTPException(status_code=502, detail=f"Sarvam API error: {str(e)}")
        combined_notes = combined_notes.strip()

        # Generate PDF
        pdf_path = generate_pdf(file.filename, combined_notes, mode)
        pdf_filename = os.path.basename(pdf_path)

        all_notes.append({
            "file": file.filename,
            "notes": combined_notes,
            "pdf_url": f"/download-notes/{pdf_filename}"
        })

    return {
        "success": True,
        "mode": mode,
        "results": all_notes
    }


@router.get("/download-notes/{filename}")
async def download_notes(filename: str):
    """Download a previously generated notes PDF."""
    # Prevent path traversal
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(OUTPUT_DIR, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=safe_filename
    )
