# app/services/parser.py

import json
import time
from groq import Groq
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging_config import logger
from app.models.resume import ResumeSchema


# ── Initialize the Groq client ─────────────────────────────────
client = Groq(api_key=settings.GROQ_API_KEY)


def build_system_prompt() -> str:
    """
    Builds the system prompt for the LLM.
    """

    system_prompt = """
You are an expert resume parser with years of experience 
extracting structured information from resumes.

Your job is to carefully read the resume text provided 
and extract all relevant information into a structured JSON object.

Follow these rules strictly:
1. Extract ONLY information that is explicitly present in the resume.
2. Do NOT invent, guess, or hallucinate any information.
3. If a field is not found in the resume, return null for that field.
4. For list fields (skills, certifications, languages), 
   return an empty list [] if nothing is found.
5. For nested list fields (education, experience, projects), 
   return an empty list [] if nothing is found.
6. Return ONLY valid JSON. No extra text, no explanations, 
   no markdown formatting.
7. Dates should be kept as they appear in the resume (as strings).
8. For skills, extract ALL skills mentioned anywhere in the resume,
   including from experience descriptions and project sections.
""".strip()

    return system_prompt


def build_user_prompt(resume_text: str) -> str:
    """
    Builds the user prompt with schema and resume text.
    """

    schema = ResumeSchema.model_json_schema()
    schema_str = json.dumps(schema, indent=2)

    user_prompt = f"""
Please extract all information from the resume below and return 
it as a JSON object that strictly follows this schema:

SCHEMA:
{schema_str}

FIELD DESCRIPTIONS:
- full_name: The complete name of the candidate
- email: Primary email address
- phone: Phone number as written in the resume
- location: City, state, or country
- linkedin: LinkedIn URL or username
- github: GitHub URL or username  
- portfolio: Personal website or portfolio URL
- summary: Professional summary or objective statement (2-5 sentences)
- skills: ALL skills found anywhere in the resume as a flat list
- education: List of education history (most recent first)
- experience: List of work experience (most recent first)
- projects: List of personal or professional projects
- certifications: List of certifications or licenses
- languages: List of spoken/written languages

RESUME TEXT:
{resume_text}

Remember: Return ONLY the JSON object. No other text.
""".strip()

    return user_prompt


def parse_resume_with_llm(resume_text: str) -> ResumeSchema:
    """
    Sends resume text to Groq LLM and returns validated ResumeSchema.
    Includes detailed logging of every step.
    """

    logger.info(
        f"Starting LLM parsing with model: {settings.MODEL_NAME}"
    )
    logger.debug(
        f"Resume text length: {len(resume_text)} characters, "
        f"{len(resume_text.split())} words"
    )

    # ── Build prompts ──────────────────────────────────────────
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(resume_text)

    logger.debug(
        f"Prompt built — "
        f"System: {len(system_prompt)} chars, "
        f"User: {len(user_prompt)} chars"
    )

    # ── Call Groq API ──────────────────────────────────────────
    llm_start = time.time()

    try:
        logger.info("Sending request to Groq API...")

        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=2000,
        )

        llm_time = round(time.time() - llm_start, 2)
        logger.info(f"Groq API responded in {llm_time}s")

    except Exception as e:
        logger.error(f"Groq API call failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error_code": "LLM_UNAVAILABLE",
                "message": "The AI parsing service is temporarily "
                           "unavailable.",
                "hint": "Please try again in a few seconds. "
                        "If the problem persists, check your "
                        "Groq API key."
            }
        )

    # ── Extract JSON string ────────────────────────────────────
    raw_json_string = response.choices[0].message.content
    logger.debug(
        f"Raw LLM response length: {len(raw_json_string)} characters"
    )

    # ── Parse JSON ────────────────────────────────────────────
    try:
        parsed_dict = json.loads(raw_json_string)
        logger.debug(
            f"JSON parsed successfully — "
            f"{len(parsed_dict)} top-level fields"
        )

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        logger.debug(f"Raw response was: {raw_json_string[:200]}...")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INVALID_LLM_RESPONSE",
                "message": "The AI returned an invalid response.",
                "hint": "Please try again."
            }
        )

    # ── Validate with Pydantic ─────────────────────────────────
    try:
        validated_resume = ResumeSchema(**parsed_dict)

        # Log what was found
        fields_found = []
        if validated_resume.full_name:
            fields_found.append("name")
        if validated_resume.email:
            fields_found.append("email")
        if validated_resume.skills:
            fields_found.append(
                f"{len(validated_resume.skills)} skills"
            )
        if validated_resume.education:
            fields_found.append(
                f"{len(validated_resume.education)} education"
            )
        if validated_resume.experience:
            fields_found.append(
                f"{len(validated_resume.experience)} experience"
            )
        if validated_resume.projects:
            fields_found.append(
                f"{len(validated_resume.projects)} projects"
            )

        logger.info(
            f"Validation successful — Found: {', '.join(fields_found)}"
        )

    except Exception as e:
        logger.error(f"Pydantic validation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "VALIDATION_FAILED",
                "message": "Resume data validation failed.",
                "hint": "Please try again with a different resume."
            }
        )

    return validated_resume