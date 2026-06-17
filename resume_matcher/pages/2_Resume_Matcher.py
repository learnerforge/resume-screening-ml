from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st

from config import settings
from src.extractor import extract_resume_text
from src.matcher import (
    compute_text_similarity_batch,
    compute_skill_match,
    compute_experience_score,
)
from src.parser import parse_resume
from src.processor import load_categorized_skills
from components.result_card import render_result_card
from components.skill_chart import render_radar_chart
from components.candidate_table import render_candidate_table

logger = logging.getLogger(__name__)

st.markdown(
    '<div class="section-header">Resume Matcher</div>',
    unsafe_allow_html=True,
)

categorized_skills = load_categorized_skills(settings.skill_file)

with st.sidebar:
    st.markdown("### Settings")
    scoring_mode = st.selectbox(
        "Scoring Mode",
        options=["TF-IDF (Fast)", "Semantic (Accurate)"],
        index=0,
        key="matcher_scoring",
    )
    settings.use_semantic = scoring_mode == "Semantic (Accurate)"

    t_weight = st.slider(
        "Text Similarity Weight", 0.0, 1.0,
        settings.default_text_weight, key="matcher_tw",
    )
    s_weight = st.slider(
        "Skill Match Weight", 0.0, 1.0,
        settings.default_skill_weight, key="matcher_sw",
    )
    e_weight = st.slider(
        "Experience Weight", 0.0, 1.0,
        settings.default_experience_weight, key="matcher_ew",
        help="Weight for years-of-experience match",
    )

    show_parsed = st.checkbox("Show parsed resume info", value=True, key="matcher_parsed")

    st.divider()
    st.caption(
        f"Skills: {sum(len(v) for v in categorized_skills.values())} in "
        f"{len(categorized_skills)} categories"
    )

tab_upload, tab_results, tab_details = st.tabs(["Upload", "Results", "Details"])

with tab_upload:
    jd_input = st.text_area(
        "Paste Job Description:",
        height=200,
        value=st.session_state.get("jd_input", ""),
        key="matcher_jd",
    )

    uploaded_files = st.file_uploader(
        "Upload Resumes",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help=f"Max {settings.max_upload_size_mb}MB per file",
        key="matcher_files",
    )

    if st.button("Analyse & Rank", type="primary", key="matcher_go"):
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
                    st.error(
                        f"{file.name} exceeds {settings.max_upload_size_mb}MB limit "
                        f"({file_size_mb:.1f}MB). Skipped."
                    )
                    progress_bar.progress(
                        (i + 1) / len(uploaded_files),
                        text=f"Processed {i + 1}/{len(uploaded_files)}",
                    )
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

                progress_bar.progress(
                    (i + 1) / len(uploaded_files),
                    text=f"Processed {i + 1}/{len(uploaded_files)}",
                )

            if not resume_texts:
                st.warning("No resumes could be processed successfully.")
            else:
                status_text.text("Computing similarity scores...")
                text_scores = compute_text_similarity_batch(resume_texts, jd_input)

                for idx, fname in enumerate(file_names):
                    sr = compute_skill_match(
                        resume_texts[idx], jd_input, str(settings.skill_file)
                    )
                    exp_score = compute_experience_score(resume_texts[idx], jd_input)

                    total_w = t_weight + s_weight + e_weight
                    tw = t_weight / total_w if total_w > 0 else 0.7
                    sw = s_weight / total_w if total_w > 0 else 0.3
                    ew = e_weight / total_w if total_w > 0 else 0.0

                    final = (
                        tw * text_scores[idx]
                        + sw * sr["skill_score"]
                        + ew * exp_score
                    )

                    all_results.append({
                        "Candidate": fname,
                        "Final Score (%)": round(final, 2),
                        "Text Similarity (%)": text_scores[idx],
                        "Skill Match (%)": sr["skill_score"],
                        "Experience Score (%)": float(exp_score),
                        "Matched Skills": ", ".join(sr["matched_skills"]),
                        "Missing Skills": ", ".join(sr["missing_skills"]),
                    })

                all_results.sort(key=lambda x: x["Final Score (%)"], reverse=True)

                st.session_state.results = all_results
                st.session_state.file_names = file_names
                st.session_state.parsed_infos = parsed_infos
                st.session_state.jd_input = jd_input
                st.session_state.last_settings = {
                    "text_weight": t_weight,
                    "skill_weight": s_weight,
                    "experience_weight": e_weight,
                    "mode": scoring_mode,
                }

                history_entry = {
                    "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "timestamp": datetime.now().isoformat(),
                    "job_description": jd_input,
                    "settings": st.session_state.last_settings,
                    "results": [
                        {
                            "candidate": r["Candidate"],
                            "final_score": r["Final Score (%)"],
                            "text_similarity": r["Text Similarity (%)"],
                            "skill_score": r["Skill Match (%)"],
                            "experience_score": r["Experience Score (%)"],
                            "matched_skills": r["Matched Skills"],
                            "missing_skills": r["Missing Skills"],
                        }
                        for r in all_results
                    ],
                }
                st.session_state.history.append(history_entry)
                history_path = (
                    Path(__file__).resolve().parents[1] / "data" / "history.json"
                )
                with open(history_path, "w") as f:
                    json.dump(st.session_state.history, f, indent=2)

                status_text.text("")
                st.success(f"Processed {len(all_results)} resumes successfully!")
                st.rerun()

with tab_results:
    results = st.session_state.get("results", [])
    if not results:
        st.info("No results yet. Go to the Upload tab and run a matching session.")
    else:
        st.markdown(f"### {len(results)} Candidates Ranked")

        cols = st.columns(3)
        for i, result in enumerate(results):
            with cols[i % 3]:
                render_result_card(result)

        csv_data = pd_to_csv(results)
        if csv_data:
            st.download_button(
                label="Download Results as CSV",
                data=csv_data,
                file_name="resume_ranking_results.csv",
                mime="text/csv",
            )

        render_candidate_table(results)

with tab_details:
    results = st.session_state.get("results", [])
    parsed_infos = st.session_state.get("parsed_infos", [])
    file_names = st.session_state.get("file_names", [])

    if not results:
        st.info("No results to show.")
    else:
        candidate_names = [r["Candidate"] for r in results]
        selected = st.selectbox("Select Candidate", candidate_names, key="detail_select")

        idx = candidate_names.index(selected)
        result = results[idx]

        col_r, col_i = st.columns([1, 1])
        with col_r:
            render_radar_chart(result)

        with col_i:
            st.markdown(f"**{result['Candidate']}**")
            st.markdown(
                f"- Final Score: **{result['Final Score (%)']}%**\n"
                f"- Text Similarity: {result['Text Similarity (%)']}%\n"
                f"- Skill Match: {result['Skill Match (%)']}%\n"
                f"- Experience: {result['Experience Score (%)']}%"
            )

        matched = result.get("Matched Skills", "")
        missing = result.get("Missing Skills", "")

        if matched:
            tags = "".join(
                f'<span class="skill-badge matched">{s.strip()}</span>'
                for s in matched.split(",") if s.strip()
            )
            st.markdown(f"**Matched Skills:**  \n{tags}", unsafe_allow_html=True)

        if missing:
            tags = "".join(
                f'<span class="skill-badge missing">{s.strip()}</span>'
                for s in missing.split(",") if s.strip()
            )
            st.markdown(f"**Missing Skills:**  \n{tags}", unsafe_allow_html=True)

        if parsed_infos and idx < len(parsed_infos):
            info = parsed_infos[idx]
            if info.get("email") or info.get("phone") or info.get("experience_years") or info.get("degrees"):
                with st.expander("Parsed Resume Info"):
                    if info.get("email"):
                        st.markdown(f"Email: {info['email']}")
                    if info.get("phone"):
                        st.markdown(f"Phone: {info['phone']}")
                    if info.get("experience_years"):
                        st.markdown(f"Experience: {info['experience_years']}+ years")
                    if info.get("degrees"):
                        st.markdown(f"Education: {', '.join(info['degrees'])}")


def pd_to_csv(results: list[dict]) -> bytes | None:
    try:
        import pandas as pd
        df = pd.DataFrame(results)
        return df.to_csv(index=False).encode("utf-8")
    except Exception:
        return None
