from __future__ import annotations

import spacy
from pathlib import Path
from typing import Union

_nlp = spacy.load("en_core_web_sm")

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
def load_skills(skill_file: Union[str, Path]) -> set[str]:
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

def extract_skills(text: str, skill_file: Union[str, Path]) -> set[str]:
    cleaned_text = clean_text(text)
    word_set = set(cleaned_text.split())

    skills = load_skills(skill_file)

    matched_skills = set()
    for skill in skills:
        normal_skill = clean_text(skill)
        if not normal_skill:
            continue

        normal_words = normal_skill.split()
        if len(normal_words) == 1:
            if normal_skill in word_set:
                matched_skills.add(skill)
        else:
            if normal_skill in cleaned_text:
                matched_skills.add(skill)

    return matched_skills
