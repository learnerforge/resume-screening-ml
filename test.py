# small test for resume sceening 

from pathlib import Path

from resume_matcher.src.extractor import extract_resume_text
from resume_matcher.src.processor import clean_text, extract_skills
from resume_matcher.src.matcher import match_resume_to_job


BASE_DIR = Path(__file__).resolve().parent
SKILL_FILE = BASE_DIR / "resume_matcher" / "data" / "skills.txt"


def test_clean_text():
    text = "Experienced Amazon Associate with 5 years of experience!"
    cleaned = clean_text(text)
    print("[OK] clean_text output:", cleaned)


def test_skill_extraction():
    text = """
    Experienced Amazon Associate with skills in Python, SQL, Linux,
    and data analysis using pandas and numpy.
    """
    skills = extract_skills(text, SKILL_FILE)
    print("[OK] extracted skills:", skills)


def test_matcher():
    resume_text = """
    Experienced Amazon Associate with skills in Python, SQL, Linux,
    and data analysis using pandas and numpy.
    """

    job_text = """
    Looking for a Data Analyst with experience in Python, SQL,
    data analysis, pandas, numpy, and Power BI.
    """

    result = match_resume_to_job(
        resume_text,
        job_text,
        SKILL_FILE,
        text_weight=0.7,
        skill_weight=0.3,
    )

    print("\n[OK] match_resume_to_job result:")
    for key, value in result.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    print("🔍 Running Resume Matcher Tests...\n")

    test_clean_text()
    test_skill_extraction()
    test_matcher()

    print("\n✅ All tests completed successfully.")

