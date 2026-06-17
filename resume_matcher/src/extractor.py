from __future__ import annotations

import logging
from pathlib import Path
from typing import Union

import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_file: Union[str, Path]) -> str:
    text: list[str] = []
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
    except Exception as exc:
        logger.exception("Failed to extract text from PDF: %s", pdf_file)
        raise RuntimeError(f"Error reading PDF file: {exc}") from exc

    return " ".join(text)


def extract_text_from_docx(docx_file: Union[str, Path]) -> str:
    try:
        doc = Document(docx_file)
        text = [para.text for para in doc.paragraphs if para.text.strip()]
    except Exception as exc:
        logger.exception("Failed to extract text from DOCX: %s", docx_file)
        raise RuntimeError(f"Error reading DOCX file: {exc}") from exc

    return " ".join(text)


def extract_resume_text(file_path: Union[str, Path]) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        logger.info("Extracting text from PDF: %s", path)
        return extract_text_from_pdf(path)
    elif suffix == ".docx":
        logger.info("Extracting text from DOCX: %s", path)
        return extract_text_from_docx(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Only PDF and DOCX are supported.")
