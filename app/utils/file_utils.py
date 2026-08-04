# app/utils/file_utils.py

import os
import uuid
from fastapi import UploadFile, HTTPException
from app.core.config import settings


def validate_file(file: UploadFile) -> None:
    """
    Validates the uploaded file.
    Checks file extension and file size.
    Raises HTTPException if validation fails.
    """

    # ── Check if file was actually provided ───────────────────
    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "NO_FILE_PROVIDED",
                "message": "No file was uploaded.",
                "hint": "Please attach a PDF or DOCX file to your request."
            }
        )

    # ── Check file extension ───────────────────────────────────
    original_filename = file.filename
    _, file_extension = os.path.splitext(original_filename)
    file_extension = file_extension.lower()

    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "INVALID_FILE_TYPE",
                "message": f"Invalid file type '{file_extension}'. "
                           f"Only PDF and DOCX files are allowed.",
                "hint": "Please upload a resume in PDF or DOCX format."
            }
        )

    # ── Check file size ────────────────────────────────────────
    file_content = file.file.read()
    file_size_mb = len(file_content) / (1024 * 1024)

    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "FILE_TOO_LARGE",
                "message": f"File too large ({file_size_mb:.2f} MB). "
                           f"Maximum allowed size is "
                           f"{settings.MAX_FILE_SIZE_MB} MB.",
                "hint": "Please compress your resume or remove large images."
            }
        )

    # ── Check file is not empty ────────────────────────────────
    if len(file_content) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "EMPTY_FILE",
                "message": "The uploaded file is empty.",
                "hint": "Please upload a valid resume file with content."
            }
        )

    # ── Reset file pointer ─────────────────────────────────────
    file.file.seek(0)


def generate_safe_filename(original_filename: str) -> str:
    """
    Generates a safe unique filename using UUID.
    """
    _, file_extension = os.path.splitext(original_filename)
    file_extension = file_extension.lower()
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_extension}"


def save_upload_file(file: UploadFile) -> str:
    """
    Saves the uploaded file to the uploads directory.
    Returns the full path where the file was saved.
    """
    safe_filename = generate_safe_filename(file.filename)
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    try:
        with open(file_path, "wb") as saved_file:
            content = file.file.read()
            saved_file.write(content)
        file.file.seek(0)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "FILE_SAVE_ERROR",
                "message": f"Failed to save the uploaded file.",
                "hint": "Please try again. If the problem persists, "
                        "contact support."
            }
        )

    return file_path


def delete_file(file_path: str) -> None:
    """
    Safely deletes a file from disk.
    Used to clean up uploaded files after processing.

    Args:
        file_path: Path to the file to delete
    """
    try:
        # Check if file exists before trying to delete
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception:
        # If deletion fails, we just ignore it
        # The file will stay in uploads/ but that is not critical
        pass


def get_file_size_mb(file_path: str) -> float:
    """
    Returns the size of a file in megabytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in MB rounded to 4 decimal places
    """
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    return round(size_mb, 4)