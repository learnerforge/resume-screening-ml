from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Also add resume_matcher/ for absolute imports used by src modules
SRC_ROOT = PROJECT_ROOT / "resume_matcher"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(1, str(SRC_ROOT))

import pytest


@pytest.fixture
def sample_resume_text() -> str:
    return """
    Experienced Software Engineer with 5 years of experience in Python, SQL, and cloud computing.
    Skilled in pandas, numpy, and machine learning. B.Tech in Computer Science.
    Email: candidate@example.com, Phone: +1-555-123-4567
    """


@pytest.fixture
def sample_job_text() -> str:
    return """
    Looking for a Data Analyst with 3+ years of experience in Python, SQL,
    data analysis, pandas, numpy, and Power BI.
    """


@pytest.fixture
def sample_empty_text() -> str:
    return ""


@pytest.fixture
def temp_skill_file(tmp_path: Path) -> Path:
    content = """
python
sql
pandas
numpy
machine learning
power bi
docker
kubernetes
"""
    path = tmp_path / "skills.txt"
    path.write_text(content.strip())
    return path
