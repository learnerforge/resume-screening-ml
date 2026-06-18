from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "resume_matcher"))

from config import settings
from src.extractor import extract_resume_text
from src.matcher import match_resume_to_job
from src.processor import extract_skills, load_skills

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Resume Matcher API",
    description="Match resumes against job descriptions using NLP",
    version="2.0.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/match")
async def match_single(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    text_weight: float = Form(0.7),
    skill_weight: float = Form(0.3),
    experience_weight: float = Form(0.0),
) -> JSONResponse:
    suffix = Path(file.filename).suffix.lower() if file.filename else ".pdf"
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        raw_text = extract_resume_text(tmp_path)
        result = match_resume_to_job(
            raw_text,
            job_description,
            str(settings.skill_file),
            text_weight=text_weight,
            skill_weight=skill_weight,
            experience_weight=experience_weight,
        )
        result["filename"] = file.filename
        return JSONResponse(content=result)

    except Exception as exc:
        logger.exception("Match failed for %s", file.filename)
        return JSONResponse(
            status_code=500,
            content={"error": str(exc), "filename": file.filename},
        )

    finally:
        if tmp_path and Path(tmp_path).exists():
            Path(tmp_path).unlink()


@app.post("/match-batch")
async def match_batch(
    files: list[UploadFile] = File(...),
    job_description: str = Form(...),
    text_weight: float = Form(0.7),
    skill_weight: float = Form(0.3),
    experience_weight: float = Form(0.0),
) -> JSONResponse:
    results: list[dict[str, Any]] = []

    for file in files:
        suffix = Path(file.filename).suffix.lower() if file.filename else ".pdf"
        tmp_path = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name

            raw_text = extract_resume_text(tmp_path)
            result = match_resume_to_job(
                raw_text,
                job_description,
                str(settings.skill_file),
                text_weight=text_weight,
                skill_weight=skill_weight,
                experience_weight=experience_weight,
            )
            result["filename"] = file.filename
            results.append(result)

        except Exception as exc:
            logger.warning("Failed to process %s: %s", file.filename, exc)
            results.append({
                "filename": file.filename,
                "error": str(exc),
            })

        finally:
            if tmp_path and Path(tmp_path).exists():
                Path(tmp_path).unlink()

    results.sort(
        key=lambda x: x.get("final_score", -1),
        reverse=True,
    )

    return JSONResponse(content={"results": results, "count": len(results)})


@app.get("/skills")
async def list_skills() -> JSONResponse:
    try:
        skills = load_skills(settings.skill_file)
        return JSONResponse(content={"skills": sorted(skills), "count": len(skills)})
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"error": str(exc)},
        )
