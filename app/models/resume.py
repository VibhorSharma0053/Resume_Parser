# app/models/resume.py

from pydantic import BaseModel, Field
from typing import Optional, List, Any


# ──────────────────────────────────────────────────────────────
# SUB-MODELS (Nested Models)
# ──────────────────────────────────────────────────────────────


class Education(BaseModel):
    """
    Represents one education entry on a resume.
    """
    degree: Optional[str] = Field(
        default=None,
        description="The degree or qualification obtained. "
                    "Example: B.Sc. Computer Science, MBA"
    )
    institution: Optional[str] = Field(
        default=None,
        description="The name of the school, college, or university."
    )
    start_date: Optional[str] = Field(
        default=None,
        description="When the education started. Example: 2018"
    )
    end_date: Optional[str] = Field(
        default=None,
        description="When the education ended. Example: 2022, Present"
    )
    grade: Optional[str] = Field(
        default=None,
        description="Grade, GPA, percentage, or classification."
    )


class Experience(BaseModel):
    """
    Represents one work experience entry on a resume.
    """
    job_title: Optional[str] = Field(
        default=None,
        description="The job title or position held."
    )
    company: Optional[str] = Field(
        default=None,
        description="The name of the company or organization."
    )
    start_date: Optional[str] = Field(
        default=None,
        description="When the job started. Example: June 2022"
    )
    end_date: Optional[str] = Field(
        default=None,
        description="When the job ended. Example: Present"
    )
    location: Optional[str] = Field(
        default=None,
        description="Location of the job. Example: New York, NY or Remote"
    )
    description: Optional[str] = Field(
        default=None,
        description="Summary of responsibilities and achievements."
    )


class Project(BaseModel):
    """
    Represents one project entry on a resume.
    """
    name: Optional[str] = Field(
        default=None,
        description="The name or title of the project."
    )
    description: Optional[str] = Field(
        default=None,
        description="A brief description of the project."
    )
    technologies: Optional[List[str]] = Field(
        default=[],
        description="List of technologies used."
    )


# ──────────────────────────────────────────────────────────────
# MAIN RESUME SCHEMA
# ──────────────────────────────────────────────────────────────


class ResumeSchema(BaseModel):
    """
    The complete structured schema for a parsed resume.
    """

    # Personal Information
    full_name: Optional[str] = Field(
        default=None,
        description="The full name of the candidate."
    )
    email: Optional[str] = Field(
        default=None,
        description="The primary email address."
    )
    phone: Optional[str] = Field(
        default=None,
        description="The phone number."
    )
    location: Optional[str] = Field(
        default=None,
        description="City, state, or country of the candidate."
    )

    # Online Presence
    linkedin: Optional[str] = Field(
        default=None,
        description="LinkedIn profile URL or username."
    )
    github: Optional[str] = Field(
        default=None,
        description="GitHub profile URL or username."
    )
    portfolio: Optional[str] = Field(
        default=None,
        description="Personal portfolio or website URL."
    )

    # Professional Summary
    summary: Optional[str] = Field(
        default=None,
        description="Professional summary or objective statement."
    )

    # Skills
    skills: Optional[List[str]] = Field(
        default=[],
        description="All technical and soft skills as a flat list."
    )

    # Nested Sections
    education: Optional[List[Education]] = Field(
        default=[],
        description="List of all education entries."
    )
    experience: Optional[List[Experience]] = Field(
        default=[],
        description="List of all work experience entries."
    )
    projects: Optional[List[Project]] = Field(
        default=[],
        description="List of projects."
    )

    # Simple Lists
    certifications: Optional[List[str]] = Field(
        default=[],
        description="List of certifications or licenses."
    )
    languages: Optional[List[str]] = Field(
        default=[],
        description="List of spoken or written languages."
    )


# ──────────────────────────────────────────────────────────────
# RESPONSE MODELS
# These define the structure of our API responses
# ──────────────────────────────────────────────────────────────


class ParseMetadata(BaseModel):
    """
    Metadata about the parsing process.
    Included in every successful response.
    """

    original_filename: str = Field(
        description="The original name of the uploaded file."
    )

    file_size_mb: float = Field(
        description="Size of the uploaded file in megabytes."
    )

    word_count: int = Field(
        description="Number of words extracted from the resume."
    )

    character_count: int = Field(
        description="Number of characters extracted from the resume."
    )

    model_used: str = Field(
        description="The LLM model used for parsing."
    )

    processing_time_seconds: float = Field(
        description="Total time taken to parse the resume in seconds."
    )


class ParseSuccessResponse(BaseModel):
    """
    The complete success response returned by the parse endpoint.

    Structure:
    {
        "status": "success",
        "message": "Resume parsed successfully",
        "metadata": { ... },
        "data": { ... parsed resume ... }
    }
    """

    status: str = Field(
        default="success",
        description="Always 'success' for successful responses."
    )

    message: str = Field(
        default="Resume parsed successfully",
        description="Human readable success message."
    )

    metadata: ParseMetadata = Field(
        description="Information about the parsing process."
    )

    data: ResumeSchema = Field(
        description="The extracted and structured resume data."
    )


class ParseErrorResponse(BaseModel):
    """
    The error response returned when parsing fails.

    Structure:
    {
        "status": "error",
        "error_code": "INVALID_FILE_TYPE",
        "message": "...",
        "hint": "..."
    }
    """

    status: str = Field(
        default="error",
        description="Always 'error' for error responses."
    )

    error_code: str = Field(
        description="A machine readable error code."
    )

    message: str = Field(
        description="Human readable error message."
    )

    hint: Optional[str] = Field(
        default=None,
        description="A helpful hint to fix the problem."
    )