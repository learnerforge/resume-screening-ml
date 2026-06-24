from __future__ import annotations

import difflib
import logging
from functools import lru_cache
from pathlib import Path
from typing import Union

import spacy

from config import settings

logger = logging.getLogger(__name__)

_nlp = spacy.load(settings.spacy_model)

_FUZZY_CUTOFF = 0.82


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

    canonical, _ = _parse_skill_file(path)
    logger.debug("Loaded %d skills from %s", len(canonical), path)
    return canonical


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
                canonical = stripped.lower().split("|")[0].strip()
                if canonical:
                    categories.setdefault(current_category, set()).add(canonical)

    logger.debug("Loaded %d categories with skills from %s", len(categories), path)
    return categories


def load_skill_aliases(skill_file: Union[str, Path]) -> dict[str, str]:
    path = Path(skill_file)
    if not path.exists():
        raise FileNotFoundError(f"Skill file not found: {path}")

    _, alias_map = _parse_skill_file(path)
    logger.debug("Loaded %d skill aliases from %s", len(alias_map), path)
    return alias_map


def _parse_skill_file(path: Path) -> tuple[set[str], dict[str, str]]:
    canonical_skills: set[str] = set()
    alias_map: dict[str, str] = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            parts = [p.strip().lower() for p in stripped.split("|") if p.strip()]
            if not parts:
                continue

            canonical = parts[0]
            canonical_skills.add(canonical)

            for alias in parts:
                alias_map[alias] = canonical

    return canonical_skills, alias_map


def _normalize_skill(skill: str) -> str:
    return skill.lower().strip()


def extract_skills(text: str, skill_file: Union[str, Path], use_fuzzy: bool = False) -> set[str]:
    cleaned_text = clean_text(text)
    word_set = set(cleaned_text.split())
    canonical_skills, alias_map = _parse_skill_file(Path(skill_file))

    matched: set[str] = set()

    for token in word_set:
        if token in alias_map:
            matched.add(alias_map[token])

    for skill in canonical_skills:
        normal_skill = _normalize_skill(skill)
        if not normal_skill:
            continue

        normal_words = normal_skill.split()
        if len(normal_words) == 1:
            if normal_skill in word_set:
                matched.add(skill)
        else:
            if normal_skill in cleaned_text:
                matched.add(skill)

    if use_fuzzy:
        fuzzy_matches = _fuzzy_skill_match(word_set, canonical_skills)
        matched.update(fuzzy_matches)

    return matched


def _fuzzy_skill_match(word_set: set[str], canonical_skills: set[str]) -> set[str]:
    matched: set[str] = set()
    sorted_skills = sorted(canonical_skills)

    for word in word_set:
        if len(word) <= 2:
            continue
        close = difflib.get_close_matches(word, sorted_skills, n=1, cutoff=_FUZZY_CUTOFF)
        if close:
            matched.add(close[0])

    return matched


def extract_skills_ner(text: str, skill_file: Union[str, Path]) -> set[str]:
    doc = _nlp(text.lower())
    _, alias_map = _parse_skill_file(Path(skill_file))

    ner_text_entities = {ent.text.lower() for ent in doc.ents if ent.text.strip()}
    ner_words = set()
    for ent in ner_text_entities:
        ner_words.update(ent.split())

    matched: set[str] = set()

    for token in ner_words:
        if token in alias_map:
            matched.add(alias_map[token])

    for token in ner_text_entities:
        if token in alias_map:
            matched.add(alias_map[token])

    return matched


def extract_skills_hybrid(text: str, skill_file: Union[str, Path]) -> set[str]:
    keyword_matches = extract_skills(text, skill_file, use_fuzzy=True)
    ner_matches = extract_skills_ner(text, skill_file)
    return keyword_matches | ner_matches
