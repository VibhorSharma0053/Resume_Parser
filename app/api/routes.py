# app/api/routes.py

import os
import time
from fastapi import APIRouter, UploadFile, File
from app.utils.file_utils import (
    validate_file,
    save_upload_file,
    delete_file,
    get_file_size_mb
)
from app.services.extractor import extract_text
from app.services.parser import parse_resume_with_llm
from app.models.resume import ParseSuccessResponse, ParseMetadata
from app.core.config import settings
from app.core.logging_config import logger


router = APIRouter()


@router.get("/health")
def health_check():
    """
    Health check endpoint.
    Returns server status and configuration info.
    """
    logger.debug("Health check requested")
    return {
        "status": "ok",
        "message": "Resume Parser API is running",
        "version": settings.APP_VERSION,
        "model": settings.MODEL_NAME
    }


@router.post(
    "/parse-resume",
    response_model=ParseSuccessResponse,
    summary="Parse a Resume",
    description=(
        "Upload a PDF or DOCX resume file. "
        "Returns structured JSON with all extracted information."
    )
)
async def parse_resume(file: UploadFile = File(...)):
    """
    Complete resume parsing endpoint.

    Flow:
    1. Validate file (type + size + not empty)
    2. Save file to uploads/
    3. Extract text from file
    4. Send text to LLM for structured parsing
    5. Validate LLM output with Pydantic
    6. Clean up uploaded file
    7. Return clean JSON with metadata
    """

    # Track total processing time
    start_time = time.time()
    saved_path = None

    logger.info(
        f"New parse request — File: '{file.filename}', "
        f"Content-Type: {file.content_type}"
    )

    try:
        # ── Step 1: Validate file ──────────────────────────────
        logger.debug("Validating uploaded file...")
        validate_file(file)
        logger.debug("File validation passed")

        # ── Step 2: Save file ──────────────────────────────────
        logger.debug("Saving file to uploads/...")
        saved_path = save_upload_file(file)
        file_size_mb = get_file_size_mb(saved_path)
        logger.info(
            f"File saved — Path: {saved_path}, "
            f"Size: {file_size_mb} MB"
        )

        # ── Step 3: Extract text ───────────────────────────────
        extracted_text = extract_text(saved_path)
        word_count = len(extracted_text.split())
        character_count = len(extracted_text)

        # ── Step 4: Parse with LLM ────────────────────────────
        parsed_resume = parse_resume_with_llm(extracted_text)

        # ── Step 5: Calculate total time ──────────────────────
        total_time = round(time.time() - start_time, 2)

        logger.info(
            f"Parse complete — "
            f"Total time: {total_time}s, "
            f"Words: {word_count}"
        )

        # ── Step 6: Build and return response ─────────────────
        metadata = ParseMetadata(
            original_filename=file.filename,
            file_size_mb=file_size_mb,
            word_count=word_count,
            character_count=character_count,
            model_used=settings.MODEL_NAME,
            processing_time_seconds=total_time
        )

        return ParseSuccessResponse(
            status="success",
            message="Resume parsed successfully",
            metadata=metadata,
            data=parsed_resume
        )

    except Exception as e:
        # Log unexpected errors
        logger.error(
            f"Unexpected error during parsing: "
            f"{type(e).__name__}: {str(e)}"
        )
        # Re-raise so global handler catches it
        raise

    finally:
        # ── Always clean up the uploaded file ─────────────────
        if saved_path:
            delete_file(saved_path)
            logger.debug(f"Cleaned up file: {saved_path}")