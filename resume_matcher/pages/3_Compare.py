from __future__ import annotations

import streamlit as st

from components.skill_chart import render_multi_radar
from components.candidate_table import render_candidate_table

st.markdown(
    '<div class="section-header">Candidate Comparison</div>',
    unsafe_allow_html=True,
)

results = st.session_state.get("results", [])
if not results:
    st.info("No results available. Run a matching session first.")
    st.stop()

names = [r["Candidate"] for r in results]
selected_names = st.multiselect(
    "Select candidates to compare",
    names,
    default=names[: min(3, len(names))],
    max_selections=5,
)

if not selected_names:
    st.info("Select at least one candidate.")
    st.stop()

selected_results = [r for r in results if r["Candidate"] in selected_names]

st.subheader("Score Comparison")
render_multi_radar(selected_results)

st.subheader("Detailed Comparison")
render_candidate_table(selected_results)

st.subheader("Skill Matrix")
for result in selected_results:
    matched = result.get("Matched Skills", "")
    missing = result.get("Missing Skills", "")
    all_skills_for_row: dict[str, str] = {}
    if matched:
        for s in matched.split(","):
            s = s.strip()
            if s:
                all_skills_for_row[s] = "matched"
    if missing:
        for s in missing.split(","):
            s = s.strip()
            if s:
                all_skills_for_row[s] = "missing"

    md_parts = [f"**{result['Candidate']}**  \n"]
    for skill, status in all_skills_for_row.items():
        badge = (
            f'<span class="skill-badge matched">{skill}</span>'
            if status == "matched"
            else f'<span class="skill-badge missing">{skill}</span>'
        )
        md_parts.append(badge)
    st.markdown(" ".join(md_parts), unsafe_allow_html=True)
