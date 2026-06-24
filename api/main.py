from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "resume_matcher"))

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from src.extractor import extract_resume_text
from src.matcher import match_resume_to_job
from src.processor import extract_skills, load_skills, load_categorized_skills

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Resume Matcher API",
    description="Match resumes against job descriptions using NLP",
    version="2.0.0",
)

HISTORY_FILE = Path(__file__).resolve().parents[1] / "resume_matcher" / "data" / "history.json"


def _normalize_results(results: list) -> list[dict]:
    key_map = {
        "candidate": "Candidate",
        "final_score": "Final Score (%)",
        "text_similarity": "Text Similarity (%)",
        "skill_score": "Skill Match (%)",
        "experience_score": "Experience Score (%)",
    }
    out = []
    for r in results:
        if not isinstance(r, dict):
            continue
        if "Candidate" in r:
            out.append(r)
            continue
        row = {}
        for old_key, new_key in key_map.items():
            if old_key in r:
                row[new_key] = r[old_key]
        for key in ("Matched Skills", "Missing Skills"):
            src_key = key.lower().replace(" ", "_")
            if src_key in r:
                val = r[src_key]
                row[key] = ", ".join(val) if isinstance(val, list) else str(val)
        if row:
            out.append(row)
    return out


# ==================== API ROUTES (defined first, highest priority) ====================

@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/match")
async def match_single(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    text_weight: float = Form(0.5),
    skill_weight: float = Form(0.4),
    experience_weight: float = Form(0.1),
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
            raw_text, job_description, str(settings.skill_file),
            text_weight=text_weight, skill_weight=skill_weight, experience_weight=experience_weight,
        )
        result["filename"] = file.filename
        return JSONResponse(content=result)
    except Exception as exc:
        logger.exception("Match failed for %s", file.filename)
        return JSONResponse(status_code=500, content={"error": str(exc), "filename": file.filename})
    finally:
        if tmp_path and Path(tmp_path).exists():
            Path(tmp_path).unlink()


@app.post("/api/match-batch")
async def match_batch(
    files: list[UploadFile] = File(...),
    job_description: str = Form(...),
    text_weight: float = Form(0.5),
    skill_weight: float = Form(0.4),
    experience_weight: float = Form(0.1),
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
                raw_text, job_description, str(settings.skill_file),
                text_weight=text_weight, skill_weight=skill_weight, experience_weight=experience_weight,
            )
            result["filename"] = file.filename
            results.append(result)
        except Exception as exc:
            logger.warning("Failed to process %s: %s", file.filename, exc)
            results.append({"filename": file.filename, "error": str(exc)})
        finally:
            if tmp_path and Path(tmp_path).exists():
                Path(tmp_path).unlink()
    results.sort(key=lambda x: x.get("final_score", -1), reverse=True)
    return JSONResponse(content={"results": results, "count": len(results)})


@app.get("/api/skills")
async def list_skills() -> JSONResponse:
    try:
        skills = load_skills(settings.skill_file)
        return JSONResponse(content={"skills": sorted(skills), "count": len(skills)})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.get("/api/skills/categorized")
async def list_categorized_skills() -> JSONResponse:
    try:
        categorized = load_categorized_skills(settings.skill_file)
        return JSONResponse(content={"categories": categorized})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.get("/api/history")
async def get_history() -> JSONResponse:
    if not HISTORY_FILE.exists():
        return JSONResponse(content=[])
    try:
        with open(HISTORY_FILE) as f:
            data = json.load(f)
        for session in data:
            if isinstance(session, dict) and "results" in session:
                session["results"] = _normalize_results(session["results"])
        return JSONResponse(content=data)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.post("/api/history")
async def save_history(data: list[dict]) -> JSONResponse:
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return JSONResponse(content={"status": "ok", "count": len(data)})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.delete("/api/history")
async def clear_history() -> JSONResponse:
    try:
        if HISTORY_FILE.exists():
            HISTORY_FILE.write_text("[]")
        return JSONResponse(content={"status": "ok"})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


# ==================== STATIC FILES (lower priority) ====================

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(frontend_dir / "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa_fallback(full_path: str):
        p = frontend_dir / full_path
        if p.exists() and not p.is_dir() and p.suffix in (".html", ".js", ".css", ".png", ".ico", ".svg"):
            return FileResponse(str(p))
        return FileResponse(str(frontend_dir / "index.html"))
