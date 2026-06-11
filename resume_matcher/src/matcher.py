from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .processor import clean_text, extract_skills

# this is used to see the similarities between resume and required skill set
def compute_text_similarity(resume_text: str, job_text: str) -> float:

    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_text)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_clean, job_clean])

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return float(round(similarity * 100, 2))

# compares skills in resume with requires skills and see gaps
def compute_skill_match(resume_text: str, job_text: str, skill_file: str) -> dict:

    resume_skills = set(extract_skills(resume_text, skill_file))
    job_skills = set(extract_skills(job_text, skill_file))

    matched_skills = resume_skills.intersection(job_skills)
    missing_skills = job_skills - resume_skills

    skill_score = (
            len(matched_skills) / len(job_skills) * 100
            if job_skills else 0.0
            )

    return {
            "matched_skills": list(matched_skills),
            "missing_skills": list(missing_skills),
            "skill_score": float(round(skill_score, 2)),
            }

# Combines all into one similar score
def match_resume_to_job(resume_text: str, job_text: str, skill_file: str,
                        text_weight: float = 0.7, skill_weight: float = 0.3,) -> dict:


    text_score = compute_text_similarity(resume_text, job_text)
    skill_result = compute_skill_match(resume_text, job_text, skill_file)

    final_score = (
            text_weight * text_score +
            skill_weight * skill_result["skill_score"]
            )

    return {
            "final_score" : float(round(final_score, 2)),
            "text_similarity": float(text_score),
            "skill_score": float(skill_result["skill_score"]),
            "matched_skills": skill_result["matched_skills"],
            "missing_skills": skill_result["missing_skills"],
            }


