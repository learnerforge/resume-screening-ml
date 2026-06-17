from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Union

import spacy

from config import settings

logger = logging.getLogger(__name__)

_nlp = spacy.load(settings.spacy_model)


@lru_cache(maxsize=256)
def clean_text(text: str) -> str:
    if not text or not text.strip():
        return ""

    doc = _nlp(text.lower())

    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop and not token.is_punct and token.is_alpha
    ]

    return " ".join(tokens)


def load_skills(skill_file: Union[str, Path]) -> set[str]:
    path = Path(skill_file)
    if not path.exists():
        raise FileNotFoundError(f"Skill file not found: {path}")

    skills: set[str] = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                skills.add(stripped.lower())

    logger.debug("Loaded %d skills from %s", len(skills), path)
    return skills


def load_categorized_skills(skill_file: Union[str, Path]) -> dict[str, set[str]]:
    path = Path(skill_file)
    if not path.exists():
        raise FileNotFoundError(f"Skill file not found: {path}")

    categories: dict[str, set[str]] = {}
    current_category = "General"

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                current_category = stripped.lstrip("#").strip()
                if current_category not in categories:
                    categories[current_category] = set()
            else:
                categories.setdefault(current_category, set()).add(stripped.lower())

    logger.debug("Loaded %d categories with skills from %s", len(categories), path)
    return categories


def _normalize_skill(skill: str) -> str:
    return skill.lower().strip()


def extract_skills(text: str, skill_file: Union[str, Path]) -> set[str]:
    cleaned_text = clean_text(text)
    word_set = set(cleaned_text.split())
    skills = load_skills(skill_file)

    matched: set[str] = set()
    for skill in skills:
        normal_skill = _normalize_skill(skill)
        if not normal_skill:
            continue

        normal_words = normal_skill.split()
        if len(normal_words) == 1:
            if normal_skill in word_set or normal_skill in cleaned_text:
                matched.add(skill)
        else:
            if normal_skill in cleaned_text:
                matched.add(skill)

    return matched


def extract_skills_ner(text: str, skill_file: Union[str, Path]) -> set[str]:
    doc = _nlp(text.lower())
    skills = load_skills(skill_file)

    ner_text_entities = {ent.text.lower() for ent in doc.ents if ent.text.strip()}
    ner_words = set()
    for ent in ner_text_entities:
        ner_words.update(ent.split())

    matched: set[str] = set()
    for skill in skills:
        normal_skill = _normalize_skill(skill)
        if not normal_skill:
            continue
        if normal_skill in ner_text_entities or normal_skill in ner_words:
            matched.add(skill)

    return matched


def extract_skills_hybrid(text: str, skill_file: Union[str, Path]) -> set[str]:
    keyword_matches = extract_skills(text, skill_file)
    ner_matches = extract_skills_ner(text, skill_file)
    return keyword_matches | ner_matches
