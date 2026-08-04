# tests/test_parser.py

import requests
import json
import os
import sys
import time

# ── Configuration ──────────────────────────────────────────────
# The URL of our running FastAPI server
API_URL = "http://127.0.0.1:8000/api/v1/parse-resume"

# Folder containing our sample resumes
SAMPLE_DIR = "tests/sample_resumes"


# ── Helper Functions ───────────────────────────────────────────

def print_separator(char="─", width=60):
    """Prints a visual separator line."""
    print(char * width)


def print_section(title):
    """Prints a formatted section header."""
    print_separator("═")
    print(f"  {title}")
    print_separator("═")


def print_field(label, value, indent=2):
    """Prints a single field with its value."""
    spaces = " " * indent
    if value is None:
        print(f"{spaces}{label}: ⚠️  Not found")
    elif isinstance(value, list) and len(value) == 0:
        print(f"{spaces}{label}: ⚠️  Empty list")
    elif isinstance(value, list):
        print(f"{spaces}{label}:")
        for item in value:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"{spaces}    {k}: {v}")
                print()
            else:
                print(f"{spaces}    • {item}")
    else:
        # Truncate very long strings for display
        display_value = str(value)
        if len(display_value) > 100:
            display_value = display_value[:100] + "..."
        print(f"{spaces}{label}: {display_value}")


def display_parse_result(result: dict, filename: str):
    """
    Displays the parse result in a readable format.

    Args:
        result: The JSON response from the API
        filename: The name of the tested file
    """

    print_section(f"Results for: {filename}")

    # ── Check if it was successful ─────────────────────────────
    if result.get("status") == "error":
        print(f"  ❌ PARSING FAILED")
        print(f"  Error Code: {result.get('error_code')}")
        print(f"  Message: {result.get('message')}")
        print(f"  Hint: {result.get('hint')}")
        return

    # ── Show metadata ──────────────────────────────────────────
    print("\n📊 METADATA:")
    metadata = result.get("metadata", {})
    print_field("Processing Time",
                f"{metadata.get('processing_time_seconds')}s")
    print_field("Word Count", metadata.get("word_count"))
    print_field("File Size", f"{metadata.get('file_size_mb')} MB")
    print_field("Model Used", metadata.get("model_used"))

    # ── Show extracted data ────────────────────────────────────
    data = result.get("data", {})

    print("\n👤 PERSONAL INFORMATION:")
    print_field("Full Name", data.get("full_name"))
    print_field("Email", data.get("email"))
    print_field("Phone", data.get("phone"))
    print_field("Location", data.get("location"))
    print_field("LinkedIn", data.get("linkedin"))
    print_field("GitHub", data.get("github"))
    print_field("Portfolio", data.get("portfolio"))

    print("\n📝 SUMMARY:")
    print_field("Summary", data.get("summary"))

    print("\n🛠️  SKILLS:")
    skills = data.get("skills", [])
    if skills:
        # Show skills in rows of 4 for readability
        for i in range(0, len(skills), 4):
            row = skills[i:i+4]
            print(f"    {' | '.join(row)}")
    else:
        print("    ⚠️  No skills found")

    print("\n🎓 EDUCATION:")
    education = data.get("education", [])
    if education:
        for i, edu in enumerate(education, 1):
            print(f"    [{i}] {edu.get('degree', 'N/A')}")
            print(f"        Institution: {edu.get('institution', 'N/A')}")
            print(f"        Period: {edu.get('start_date', '?')} "
                  f"- {edu.get('end_date', '?')}")
            print(f"        Grade: {edu.get('grade', 'N/A')}")
            print()
    else:
        print("    ⚠️  No education found")

    print("💼 EXPERIENCE:")
    experience = data.get("experience", [])
    if experience:
        for i, exp in enumerate(experience, 1):
            print(f"    [{i}] {exp.get('job_title', 'N/A')} "
                  f"at {exp.get('company', 'N/A')}")
            print(f"        Period: {exp.get('start_date', '?')} "
                  f"- {exp.get('end_date', '?')}")
            print(f"        Location: {exp.get('location', 'N/A')}")
            desc = exp.get('description', '')
            if desc and len(desc) > 80:
                desc = desc[:80] + "..."
            print(f"        Description: {desc}")
            print()
    else:
        print("    ⚠️  No experience found")

    print("🚀 PROJECTS:")
    projects = data.get("projects", [])
    if projects:
        for i, proj in enumerate(projects, 1):
            print(f"    [{i}] {proj.get('name', 'N/A')}")
            tech = proj.get("technologies", [])
            if tech:
                print(f"        Tech: {', '.join(tech)}")
            print()
    else:
        print("    ⚠️  No projects found")

    print("📜 CERTIFICATIONS:")
    certs = data.get("certifications", [])
    if certs:
        for cert in certs:
            print(f"    • {cert}")
    else:
        print("    ⚠️  No certifications found")

    print("\n🌍 LANGUAGES:")
    languages = data.get("languages", [])
    if languages:
        print(f"    {', '.join(languages)}")
    else:
        print("    ⚠️  No languages found")


def calculate_completeness_score(result: dict) -> dict:
    """
    Calculates how complete the parsed resume is.
    Checks which fields were successfully extracted.

    Returns a dict with score and field-by-field breakdown.
    """

    if result.get("status") == "error":
        return {"score": 0, "message": "Parsing failed"}

    data = result.get("data", {})

    # Define fields and their weights
    fields_to_check = {
        # Simple fields
        "full_name": ("simple", 10),
        "email": ("simple", 10),
        "phone": ("simple", 8),
        "location": ("simple", 5),
        "linkedin": ("simple", 5),
        "github": ("simple", 5),
        "portfolio": ("simple", 3),
        "summary": ("simple", 8),
        # List fields
        "skills": ("list", 15),
        "education": ("list", 15),
        "experience": ("list", 10),
        "projects": ("list", 5),
        "certifications": ("list", 5),
        "languages": ("list", 5),
    }

    total_weight = sum(w for _, (_, w) in fields_to_check.items())
    earned_weight = 0
    field_results = {}

    for field, (field_type, weight) in fields_to_check.items():
        value = data.get(field)

        if field_type == "simple":
            found = value is not None and value != ""
        else:
            found = isinstance(value, list) and len(value) > 0

        field_results[field] = "✅" if found else "⚠️ "
        if found:
            earned_weight += weight

    score = round((earned_weight / total_weight) * 100, 1)

    return {
        "score": score,
        "fields": field_results
    }


def test_single_resume(file_path: str) -> dict:
    """
    Tests the parser with a single resume file.

    Args:
        file_path: Path to the resume file to test

    Returns:
        The JSON response from the API
    """

    filename = os.path.basename(file_path)
    print(f"\n⏳ Testing: {filename}")
    print(f"   Sending to API...")

    # Track request time
    start = time.time()

    try:
        # Open the file and send it to our API
        with open(file_path, "rb") as f:
            files = {"file": (filename, f, "application/octet-stream")}
            response = requests.post(API_URL, files=files, timeout=60)

        elapsed = round(time.time() - start, 2)
        print(f"   Response received in {elapsed}s "
              f"(Status: {response.status_code})")

        # Parse the JSON response
        result = response.json()
        return result

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to the API server.")
        print("   Make sure the server is running:")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)

    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out after 60 seconds.")
        return {"status": "error",
                "error_code": "TIMEOUT",
                "message": "Request timed out"}

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {"status": "error",
                "error_code": "REQUEST_ERROR",
                "message": str(e)}


def run_all_tests():
    """
    Runs tests for all sample resumes in the sample directory.
    Shows results and completeness scores for each.
    """

    print_separator("═", 60)
    print("  RESUME PARSER - TEST SUITE")
    print_separator("═", 60)
    print(f"  API URL: {API_URL}")
    print(f"  Sample Dir: {SAMPLE_DIR}")
    print_separator("═", 60)

    # ── Check if sample directory exists ──────────────────────
    if not os.path.exists(SAMPLE_DIR):
        print(f"❌ Sample directory not found: {SAMPLE_DIR}")
        print("   Please create the directory and add sample resumes.")
        sys.exit(1)

    # ── Get all files in sample directory ─────────────────────
    sample_files = [
        f for f in os.listdir(SAMPLE_DIR)
        if f.endswith((".pdf", ".docx", ".txt"))
    ]

    if not sample_files:
        print(f"❌ No sample files found in {SAMPLE_DIR}")
        print("   Add PDF, DOCX, or TXT files to test.")
        sys.exit(1)

    print(f"\n  Found {len(sample_files)} sample resume(s) to test\n")

    # ── Test each file ─────────────────────────────────────────
    all_scores = []

    for filename in sorted(sample_files):
        file_path = os.path.join(SAMPLE_DIR, filename)

        # Send to API and get result
        result = test_single_resume(file_path)

        # Display the parsed result
        display_parse_result(result, filename)

        # Calculate and show completeness score
        completeness = calculate_completeness_score(result)
        score = completeness.get("score", 0)
        all_scores.append(score)

        print(f"\n📈 COMPLETENESS SCORE: {score}%")

        if "fields" in completeness:
            print("   Field by field:")
            fields = completeness["fields"]
            for field, status in fields.items():
                print(f"   {status} {field}")

        print_separator()

        # Small delay between requests
        # Avoids hitting Groq rate limits
        if len(sample_files) > 1:
            print("\n   ⏳ Waiting 3 seconds before next test...")
            time.sleep(3)

    # ── Final Summary ──────────────────────────────────────────
    print_section("FINAL TEST SUMMARY")

    if all_scores:
        avg_score = round(sum(all_scores) / len(all_scores), 1)
        print(f"\n  Files Tested: {len(sample_files)}")
        print(f"  Average Completeness: {avg_score}%")
        print(f"  Individual Scores:")
        for filename, score in zip(sorted(sample_files), all_scores):
            bar = "█" * int(score / 5)
            print(f"    {filename[:30]:<30} {score}% {bar}")

    print_separator("═")
    print("  Testing complete!")
    print_separator("═")


# ── Run the tests ──────────────────────────────────────────────
if __name__ == "__main__":
    run_all_tests()