# This is used to process the data came from extractor
# Importing the dependencies
import spacy
from pathlib import Path

# load spacy model to npl, make it private to this file only
_nlp = spacy.load("en_core_web_sm") # this helps to remove conflict

# function to normalize the raw text in rusume for NLP
def clean_text(text: str) -> str:
    if not text or not text.strip():
        return ""

    doc = _nlp(text.lower())

    tokens = [
            token.lemma_
            for token in doc
            if not token.is_stop
            and not token.is_punct
            and token.is_alpha
            ]

    return " ".join(tokens)

# function to load skills from skills.txt
def load_skills(skill_file: str | Path) -> set[str]:
    skill_file = Path(skill_file)

    if not skill_file.exists():
        raise FileNotFoundError(f"Skill file not found: {skill_file}")

    with open(skill_file, "r", encoding="utf-8") as f:
        skills = {
                line.strip().lower()
                for line in f
                if line.strip()
                }
        return skills

# function to find skills appeared in resume
# map original skills to normal_skills
def extract_skills(text: str, skill_file: str | Path) -> set[str]:
    cleaned_text = clean_text(text)
    skills = load_skills(skill_file)

    normalized_skills_map = {
            skill: clean_text(skill)
            for skill in skills
            }

    matched_skills = {
            skill
            for skill, normal_skill in normalized_skills_map.items()
            if normal_skill and normal_skill in cleaned_text
            }

    return matched_skills
