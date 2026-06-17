from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

EMAIL_PATTERN = re.compile(r"[\w\.\-]+@[\w\.\-]+\.\w+")
PHONE_PATTERN = re.compile(
    r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
)
LINKEDIN_PATTERN = re.compile(
    r"https?://(?:www\.)?linkedin\.com/in/[\w\-/]+",
    re.IGNORECASE,
)
EXPERIENCE_PATTERN = re.compile(
    r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?experience",
    re.IGNORECASE,
)

DEGREE_PATTERNS = [
    re.compile(r"B\.?(?:Tech|E|S|A|Sc|Com)\b", re.IGNORECASE),
    re.compile(r"M\.?(?:Tech|E|S|Sc|A|Com|BA)\b", re.IGNORECASE),
    re.compile(r"Ph\.?D\.?", re.IGNORECASE),
    re.compile(r"Bachelor(?:'s)?\s+(?:of\s+)?", re.IGNORECASE),
    re.compile(r"Master(?:'s)?\s+(?:of\s+)?", re.IGNORECASE),
    re.compile(r"MBA", re.IGNORECASE),
    re.compile(r"BBA", re.IGNORECASE),
    re.compile(r"BCA", re.IGNORECASE),
    re.compile(r"MCA", re.IGNORECASE),
    re.compile(r"BE\b", re.IGNORECASE),
    re.compile(r"ME\b", re.IGNORECASE),
    re.compile(r"BTech", re.IGNORECASE),
    re.compile(r"MTech", re.IGNORECASE),
    re.compile(r"Associate(?:'s)?\s+(?:of\s+)?", re.IGNORECASE),
    re.compile(r"High\s+School", re.IGNORECASE),
]


def parse_resume(text: str) -> dict[str, Any]:
    info: dict[str, Any] = {}

    email_match = EMAIL_PATTERN.search(text)
    info["email"] = email_match.group(0) if email_match else None

    phone_match = PHONE_PATTERN.search(text)
    info["phone"] = phone_match.group(0).strip() if phone_match else None

    linkedin_match = LINKEDIN_PATTERN.search(text)
    info["linkedin"] = linkedin_match.group(0) if linkedin_match else None

    exp_matches = EXPERIENCE_PATTERN.findall(text)
    info["experience_years"] = max(int(y) for y in exp_matches) if exp_matches else None

    degrees_found: list[str] = []
    for pattern in DEGREE_PATTERNS:
        for match in pattern.finditer(text):
            degree = match.group(0).strip()
            if degree not in degrees_found:
                degrees_found.append(degree)
    info["degrees"] = degrees_found

    found_any = any(v is not None and v != [] for v in info.values())
    if found_any:
        logger.debug("Parsed resume fields: email=%s, phone=%s, degrees=%s",
                     info.get("email"), info.get("phone"), info.get("degrees"))

    return info
