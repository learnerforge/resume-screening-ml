from __future__ import annotations

import logging
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import settings
from src.extractor import extract_resume_text
from src.matcher import (
    compute_text_similarity_batch,
    compute_skill_match,
    compute_experience_score,
    match_resume_to_job,
)
from src.parser import parse_resume
from src.processor import load_categorized_skills, extract_skills

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="AI Resume Matcher",
    page_icon="",
    layout="wide",
)

st.title("AI-Powered Resume Screener")

categorized_skills = load_categorized_skills(settings.skill_file)

with st.sidebar:
    st.header("Settings")

    scoring_mode = st.selectbox(
        "Scoring Mode",
        options=["TF-IDF (Fast)", "Semantic (Accurate)"],
        index=0,
    )
    settings.use_semantic = scoring_mode == "Semantic (Accurate)"

    t_weight = st.slider("Text Similarity Weight", 0.0, 1.0, settings.default_text_weight)
    s_weight = st.slider("Skill Match Weight", 0.0, 1.0, settings.default_skill_weight)
    e_weight = st.slider(
        "Experience Weight",
        0.0,
        1.0,
        settings.default_experience_weight,
        help="How much to weigh years-of-experience match",
    )

    if st.checkbox("Show parsed resume info", value=True):
        show_parsed = True
    else:
        show_parsed = False

    st.divider()
    st.caption(f"Skills loaded: {sum(len(v) for v in categorized_skills.values())} across {len(categorized_skills)} categories")

jd_input = st.text_area("Paste Job Description:", height=200)

uploaded_files = st.file_uploader(
    "Upload resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    help=f"Max {settings.max_upload_size_mb}MB per file",
)

if st.button("Analyse & Rank", type="primary"):
    if not jd_input:
        st.error("Please paste a job description.")
    elif not uploaded_files:
        st.error("Please upload at least one resume.")
    else:
        all_results: list[dict] = []
        resume_texts: list[str] = []
        file_names: list[str] = []
        parsed_infos: list[dict] = []

        progress_bar = st.progress(0, text="Processing resumes...")
        status_text = st.empty()

        for i, file in enumerate(uploaded_files):
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            if file_size_mb > settings.max_upload_size_mb:
                st.error(f"{file.name} exceeds {settings.max_upload_size_mb}MB limit ({file_size_mb:.1f}MB). Skipped.")
                continue

            tmp_path = None
            try:
                suffix = Path(file.name).suffix.lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(file.getbuffer())
                    tmp_path = tmp.name

                raw_text = extract_resume_text(tmp_path)
                resume_texts.append(raw_text)
                file_names.append(file.name)

                if show_parsed:
                    parsed_infos.append(parse_resume(raw_text))

            except Exception as exc:
                logger.exception("Failed to process %s", file.name)
                st.error(f"Failed to process {file.name}: {exc}")
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)

            progress_bar.progress((i + 1) / len(uploaded_files),
                                  text=f"Processed {i + 1}/{len(uploaded_files)}")

        if not resume_texts:
            st.warning("No resumes could be processed successfully.")
        else:
            status_text.text("Computing similarity scores...")
            text_scores = compute_text_similarity_batch(resume_texts, jd_input)

            for idx, file_name in enumerate(file_names):
                skill_result = compute_skill_match(resume_texts[idx], jd_input, str(settings.skill_file))
                exp_score = compute_experience_score(resume_texts[idx], jd_input)

                total_w = t_weight + s_weight + e_weight
                t_w = t_weight / total_w if total_w > 0 else 0.7
                s_w = s_weight / total_w if total_w > 0 else 0.3
                e_w = e_weight / total_w if total_w > 0 else 0.0

                final_score = t_w * text_scores[idx] + s_w * skill_result["skill_score"] + e_w * exp_score

                result = {
                    "Candidate": file_name,
                    "Final Score (%)": round(final_score, 2),
                    "Text Similarity (%)": text_scores[idx],
                    "Skill Match (%)": skill_result["skill_score"],
                    "Experience Score (%)": float(exp_score),
                    "Matched Skills": ", ".join(skill_result["matched_skills"]),
                    "Missing Skills": ", ".join(skill_result["missing_skills"]),
                }
                all_results.append(result)

            all_results.sort(key=lambda x: x["Final Score (%)"], reverse=True)

            status_text.text("")

            st.subheader("Ranking Results")

            df = pd.DataFrame(all_results)
            st.dataframe(df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="resume_ranking_results.csv",
                mime="text/csv",
            )

            if show_parsed and parsed_infos:
                with st.expander("Parsed Resume Details"):
                    for file_name, info in zip(file_names, parsed_infos):
                        details = []
                        if info.get("email"):
                            details.append(f"Email: {info['email']}")
                        if info.get("phone"):
                            details.append(f"Phone: {info['phone']}")
                        if info.get("experience_years"):
                            details.append(f"Experience: {info['experience_years']}+ years")
                        if info.get("degrees"):
                            details.append(f"Education: {', '.join(info['degrees'])}")
                        if details:
                            st.markdown(f"**{file_name}**")
                            for d in details:
                                st.markdown(f"- {d}")
