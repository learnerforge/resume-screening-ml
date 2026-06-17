from __future__ import annotations

from pathlib import Path

import pytest

from resume_matcher.src.extractor import extract_resume_text


def test_extract_resume_text_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        extract_resume_text("/nonexistent/path/file.pdf")


def test_extract_resume_text_unsupported_format(tmp_path: Path):
    path = tmp_path / "file.txt"
    path.write_text("not a resume")
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_resume_text(str(path))


def test_extract_resume_text_corrupted_pdf(tmp_path: Path):
    path = tmp_path / "corrupted.pdf"
    path.write_bytes(b"not a real pdf content")
    with pytest.raises(RuntimeError, match="Error reading PDF file"):
        extract_resume_text(str(path))
