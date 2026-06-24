from __future__ import annotations

from pathlib import Path

import pytest

from resume_matcher.src.processor import (
    clean_text,
    extract_skills,
    load_skills,
    load_skill_aliases,
    load_categorized_skills,
)


def test_clean_text_normal():
    result = clean_text("Experienced Python developer with 5 years!")
    assert isinstance(result, str)
    assert len(result) > 0
    assert "experience" in result  # "Experienced" → "experience"


def test_clean_text_empty():
    assert clean_text("") == ""
    assert clean_text("   ") == ""


def test_clean_text_stopwords_removed():
    result = clean_text("the and of in a an is for with")
    assert result == ""


def test_load_skills(temp_skill_file: Path):
    skills = load_skills(temp_skill_file)
    assert "python" in skills
    assert "machine learning" in skills
    assert "javascript" in skills
    assert len(skills) == 9


def test_load_skills_missing_file():
    with pytest.raises(FileNotFoundError):
        load_skills("/nonexistent/skills.txt")


def test_load_categorized_skills(temp_skill_file: Path):
    categories = load_categorized_skills(temp_skill_file)
    assert "General" in categories  # no # headers in test file


def test_load_categorized_skills_with_headers(tmp_path: Path):
    content = """
# Languages
python
java

# Cloud
aws
gcp
"""
    path = tmp_path / "categorized_skills.txt"
    path.write_text(content.strip())

    categories = load_categorized_skills(path)
    assert "Languages" in categories
    assert "Cloud" in categories
    assert "python" in categories["Languages"]
    assert "aws" in categories["Cloud"]


def test_extract_skills(sample_resume_text: str, temp_skill_file: Path):
    skills = extract_skills(sample_resume_text, temp_skill_file)
    assert "python" in skills
    assert "sql" in skills
    assert "pandas" in skills
    assert "numpy" in skills


def test_extract_skills_no_match(sample_empty_text: str, temp_skill_file: Path):
    skills = extract_skills(sample_empty_text, temp_skill_file)
    assert skills == set()


def test_load_skill_aliases(temp_skill_file: Path):
    aliases = load_skill_aliases(temp_skill_file)
    assert aliases["powerbi"] == "power bi"
    assert aliases["js"] == "javascript"
    assert aliases["javascript"] == "javascript"
    assert aliases["python"] == "python"


def test_extract_skills_with_alias(temp_skill_file: Path):
    text = "Experienced in js, powerbi, and python"
    skills = extract_skills(text, temp_skill_file)
    assert "javascript" in skills
    assert "power bi" in skills
    assert "python" in skills


def test_load_categorized_skills_with_aliases(tmp_path: Path):
    content = """
# Languages
python
javascript|js

# Cloud
aws|amazon web services
gcp
"""
    path = tmp_path / "aliased_skills.txt"
    path.write_text(content.strip())

    categories = load_categorized_skills(path)
    assert "Languages" in categories
    assert "Cloud" in categories
    assert "python" in categories["Languages"]
    assert "javascript" in categories["Languages"]
    assert "js" not in categories["Languages"]
    assert "aws" in categories["Cloud"]
