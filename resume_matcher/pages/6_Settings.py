from __future__ import annotations

import json
import logging
from pathlib import Path

import streamlit as st

from config import settings
from src.processor import load_categorized_skills

logger = logging.getLogger(__name__)

st.markdown(
    '<div class="section-header">Settings</div>',
    unsafe_allow_html=True,
)

with st.container():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Default Weights")

    col1, col2, col3 = st.columns(3)
    with col1:
        settings.default_text_weight = st.slider(
            "Text Similarity",
            0.0, 1.0, settings.default_text_weight,
            key="settings_tw",
        )
    with col2:
        settings.default_skill_weight = st.slider(
            "Skill Match",
            0.0, 1.0, settings.default_skill_weight,
            key="settings_sw",
        )
    with col3:
        settings.default_experience_weight = st.slider(
            "Experience",
            0.0, 1.0, settings.default_experience_weight,
            key="settings_ew",
        )
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Theme")

    current_theme = st.session_state.get("theme", "light")
    new_theme = st.selectbox(
        "Appearance",
        options=["light", "dark"],
        index=0 if current_theme == "light" else 1,
        key="theme_select",
    )
    if new_theme != current_theme:
        st.session_state.theme = new_theme
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Scoring Mode")

    current_mode = "TF-IDF (Fast)" if not settings.use_semantic else "Semantic (Accurate)"
    new_mode = st.selectbox(
        "Default scoring algorithm",
        options=["TF-IDF (Fast)", "Semantic (Accurate)"],
        index=0 if not settings.use_semantic else 1,
        key="settings_mode",
    )
    settings.use_semantic = new_mode == "Semantic (Accurate)"
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Upload Limits")

    settings.max_upload_size_mb = st.number_input(
        "Max file size (MB)",
        min_value=1,
        max_value=100,
        value=settings.max_upload_size_mb,
        key="settings_upload",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Skills Database")

    try:
        categorized = load_categorized_skills(settings.skill_file)
        total = sum(len(v) for v in categorized.values())
        st.metric("Total Skills", total)
        st.metric("Categories", len(categorized))

        with st.expander("Browse Skills by Category"):
            for cat, skills in sorted(categorized.items()):
                st.markdown(f"**{cat}** ({len(skills)} skills)")
                tags = "".join(
                    f'<span class="skill-badge matched">{s}</span>'
                    for s in sorted(skills)
                )
                st.markdown(tags, unsafe_allow_html=True)
    except Exception as exc:
        st.error(f"Failed to load skills: {exc}")
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Data Management")

    col_del, col_exp = st.columns(2)
    with col_del:
        if st.button("Clear All History", type="secondary"):
            st.session_state.history = []
            history_path = Path(__file__).resolve().parents[1] / "data" / "history.json"
            with open(history_path, "w") as f:
                json.dump([], f)
            st.success("History cleared.")
    with col_exp:
        history = st.session_state.get("history", [])
        if history:
            import pandas as pd
            all_rows = []
            for session in history:
                for r in session.get("results", []):
                    row = dict(r)
                    row["session_timestamp"] = session.get("timestamp", "")
                    row["session_id"] = session.get("id", "")
                    all_rows.append(row)
            if all_rows:
                df = pd.DataFrame(all_rows)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Export All Data",
                    data=csv,
                    file_name="all_history.csv",
                    mime="text/csv",
                )

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="panel">
        <strong>About</strong><br>
        Resume Matcher v2.0<br>
        NLP engine: {"Sentence Transformers" if settings.use_semantic else "TF-IDF"}<br>
        Skills: {total if 'categorized' in dir() else "?"} entries in {len(categorized) if 'categorized' in dir() else "?"} categories
    </div>
    """,
    unsafe_allow_html=True,
)
