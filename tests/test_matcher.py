from __future__ import annotations

from pathlib import Path

from resume_matcher.src.matcher import (
    compute_text_similarity,
    compute_skill_match,
    compute_experience_score,
    match_resume_to_job,
)


def test_compute_text_similarity_identical():
    text = "Python developer with machine learning experience"
    score = compute_text_similarity(text, text)
    assert score == 100.0


def test_compute_text_similarity_completely_different():
    sim = compute_text_similarity(
        "Python and SQL developer",
        "Cooking and baking recipes",
    )
    assert sim < 50.0


def test_compute_skill_match(sample_resume_text: str, sample_job_text: str, temp_skill_file: Path):
    result = compute_skill_match(sample_resume_text, sample_job_text, str(temp_skill_file))
    assert "python" in result["matched_skills"]
    assert "power bi" in result["missing_skills"]
    assert 0 <= result["skill_score"] <= 100


def test_compute_skill_match_no_job_skills(sample_resume_text: str, temp_skill_file: Path):
    result = compute_skill_match(sample_resume_text, "No skills mentioned here", str(temp_skill_file))
    assert result["skill_score"] == 0.0


def test_compute_experience_score_match():
    score = compute_experience_score(
        "5 years of experience in Python",
        "3+ years of experience required",
    )
    assert score >= 100.0  # 5 >= 3


def test_compute_experience_score_below():
    score = compute_experience_score(
        "2 years of experience",
        "5 years of experience required",
    )
    assert score < 100.0  # 2 < 5


def test_compute_experience_score_no_dates():
    score = compute_experience_score(
        "Python developer",
        "JavaScript developer",
    )
    assert score == 100.0  # no data = no penalty


def test_match_resume_to_job(sample_resume_text: str, sample_job_text: str, temp_skill_file: Path):
    result = match_resume_to_job(
        sample_resume_text,
        sample_job_text,
        str(temp_skill_file),
        text_weight=0.5,
        skill_weight=0.4,
        experience_weight=0.1,
    )
    assert "final_score" in result
    assert "text_similarity" in result
    assert "skill_score" in result
    assert "experience_score" in result
    assert "matched_skills" in result
    assert "missing_skills" in result
    assert 0 <= result["final_score"] <= 100


def test_match_resume_to_job_zero_weights(sample_resume_text: str, sample_job_text: str, temp_skill_file: Path):
    result = match_resume_to_job(
        sample_resume_text,
        sample_job_text,
        str(temp_skill_file),
        text_weight=0.0,
        skill_weight=0.0,
        experience_weight=0.0,
    )
    # Should fall back to default weights and still produce a valid score
    assert 0 <= result["final_score"] <= 100


def test_compute_text_similarity_bigram_matching():
    """Bigrams should capture multi-word technical terms better."""
    resume = "experienced in machine learning and deep learning"
    job = "need expertise in machine learning and deep learning"
    score = compute_text_similarity(resume, job)
    assert score > 50.0
