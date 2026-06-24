from __future__ import annotations

import logging
import re
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import settings
from src.processor import clean_text, extract_skills_hybrid as extract_skills

logger = logging.getLogger(__name__)

_sentence_model: Any = None

_TFIDF_NGRAM_RANGE = (1, 2)
_TFIDF_SUBLINEAR_TF = True


def _get_sentence_model():
    global _sentence_model
    if _sentence_model is None:
        from sentence_transformers import SentenceTransformer

        logger.info("Loading SentenceTransformer model: %s", settings.sentence_transformer_model)
        _sentence_model = SentenceTransformer(settings.sentence_transformer_model)
    return _sentence_model


def _make_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        ngram_range=_TFIDF_NGRAM_RANGE,
        sublinear_tf=_TFIDF_SUBLINEAR_TF,
    )


def compute_text_similarity(resume_text: str, job_text: str) -> float:
    if settings.use_semantic:
        return compute_semantic_similarity(resume_text, job_text)

    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_text)

    vectorizer = _make_vectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_clean, job_clean])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return float(round(similarity * 100, 2))


def compute_text_similarity_batch(resume_texts: list[str], job_text: str) -> list[float]:
    if settings.use_semantic:
        model = _get_sentence_model()
        all_texts = resume_texts + [job_text]
        embeddings = model.encode(all_texts)
        job_emb = embeddings[-1:]
        resume_embs = embeddings[:-1]
        sims = cosine_similarity(job_emb, resume_embs)[0]
        return [float(round(s * 100, 2)) for s in sims]

    cleaned_resumes = [clean_text(r) for r in resume_texts]
    cleaned_job = clean_text(job_text)

    all_texts = cleaned_resumes + [cleaned_job]
    vectorizer = _make_vectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    job_vec = tfidf_matrix[-1:]
    resume_vecs = tfidf_matrix[:-1]
    similarities = cosine_similarity(job_vec, resume_vecs)[0]

    logger.debug("Batch TF-IDF computed for %d resumes", len(resume_texts))
    return [float(round(s * 100, 2)) for s in similarities]


def compute_semantic_similarity(resume_text: str, job_text: str) -> float:
    model = _get_sentence_model()
    embeddings = model.encode([resume_text, job_text])
    sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(round(sim * 100, 2))


def compute_skill_match(
    resume_text: str, job_text: str, skill_file: str
) -> dict[str, Any]:
    resume_skills = set(extract_skills(resume_text, skill_file))
    job_skills = set(extract_skills(job_text, skill_file))

    matched_skills = resume_skills.intersection(job_skills)
    missing_skills = job_skills - resume_skills

    skill_score = (
        len(matched_skills) / len(job_skills) * 100 if job_skills else 0.0
    )

    logger.debug(
        "Skill match: %d matched, %d missing, score=%.2f",
        len(matched_skills),
        len(missing_skills),
        skill_score,
    )

    return {
        "matched_skills": list(matched_skills),
        "missing_skills": list(missing_skills),
        "skill_score": float(round(skill_score, 2)),
    }


def compute_experience_score(resume_text: str, job_text: str) -> float:
    exp_pattern = re.compile(r"(\d+)\+?\s*years?\s*(?:of\s+)?experience", re.IGNORECASE)

    resume_years = [int(m.group(1)) for m in exp_pattern.finditer(resume_text)]
    job_years = [int(m.group(1)) for m in exp_pattern.finditer(job_text)]

    if not resume_years or not job_years:
        return 100.0

    resume_max = max(resume_years)
    job_max = max(job_years)

    score = min(resume_max / job_max, 1.0) * 100
    return float(round(score, 2))


def match_resume_to_job(
    resume_text: str,
    job_text: str,
    skill_file: str,
    text_weight: float = 0.5,
    skill_weight: float = 0.4,
    experience_weight: float = 0.1,
) -> dict[str, Any]:
    text_score = compute_text_similarity(resume_text, job_text)
    skill_result = compute_skill_match(resume_text, job_text, skill_file)
    exp_score = compute_experience_score(resume_text, job_text)

    # Re-normalize weights to sum to 1.0
    total_weight = text_weight + skill_weight + experience_weight
    if total_weight > 0:
        t_w = text_weight / total_weight
        s_w = skill_weight / total_weight
        e_w = experience_weight / total_weight
    else:
        t_w, s_w, e_w = 0.5, 0.4, 0.1

    final_score = t_w * text_score + s_w * skill_result["skill_score"] + e_w * exp_score

    logger.debug(
        "Final score: %.2f (text=%.2f/%.2f, skill=%.2f/%.2f, exp=%.2f/%.2f)",
        final_score, text_score, t_w,
        skill_result["skill_score"], s_w,
        exp_score, e_w,
    )

    return {
        "final_score": float(round(final_score, 2)),
        "text_similarity": float(text_score),
        "skill_score": float(skill_result["skill_score"]),
        "experience_score": float(exp_score),
        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
    }
