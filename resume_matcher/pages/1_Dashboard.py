from __future__ import annotations

from collections import Counter

import streamlit as st

from components.skill_chart import render_score_distribution, render_skill_barchart

st.markdown('<div class="section-header">Dashboard</div>', unsafe_allow_html=True)

results = st.session_state.get("results", [])
history = st.session_state.get("history", [])

all_results = list(results)
for session in history:
    all_results.extend(session.get("results", []))

total_candidates = len(all_results)
total_sessions = len(history) + (1 if results else 0)
avg_score = (
    sum(r.get("Final Score (%)", 0) for r in all_results) / total_candidates
    if total_candidates
    else 0
)
all_skills = []
for r in all_results:
    matched = r.get("Matched Skills", "")
    if matched:
        all_skills.extend(s.strip() for s in matched.split(",") if s.strip())
unique_skills = len(set(all_skills))

top_score = max((r.get("Final Score (%)", 0) for r in all_results), default=0)

if not total_candidates:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">Welcome to Resume Matcher</div>
            <div class="hero-text">
                Upload resumes, describe your ideal role, and let the system rank candidates
                by skill match, experience, and text similarity.
            </div>
            <div class="hero-actions">
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/2_Resume_Matcher.py", label="Get Started", use_container_width=True)
    with col2:
        st.page_link("pages/6_Settings.py", label="Configure Settings", use_container_width=True)
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Candidates Processed", f"{total_candidates}")
col2.metric("Matching Sessions", f"{total_sessions}")
col3.metric("Average Score", f"{avg_score:.1f}%")
col4.metric("Top Score", f"{top_score:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

la1, la2, la3 = st.columns(3)
with la1:
    st.page_link("pages/2_Resume_Matcher.py", label="New Match", use_container_width=True)
with la2:
    st.page_link("pages/3_Compare.py", label="Compare Candidates", use_container_width=True)
with la3:
    st.page_link("pages/4_Analytics.py", label="View Analytics", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    if all_results:
        scores = [r.get("Final Score (%)", 0) for r in all_results]
        render_score_distribution(scores)

with col_b:
    if all_skills:
        skill_counts = Counter(all_skills)
        render_skill_barchart(
            dict(skill_counts.most_common(15)), "Most Common Skills"
        )

if history:
    st.markdown("### Recent Sessions")
    timeline_html = '<div class="timeline">'
    for session in reversed(history[-8:]):
        ts = session.get("timestamp", "unknown")
        jd = session.get("job_description", "")
        jd_short = (jd[:70] + "...") if len(jd) > 70 else (jd if jd else "(no description)")
        count = len(session.get("results", []))
        top = max((r.get("final_score", 0) for r in session.get("results", [])), default=0)
        timeline_html += f"""
        <div class="timeline-item">
            <div class="tl-header">
                <span class="tl-title">{jd_short}</span>
                <span class="tl-time">{ts}</span>
            </div>
            <div class="tl-meta">{count} candidates  &middot;  top score: {top}%</div>
        </div>
        """
    timeline_html += "</div>"
    st.markdown(timeline_html, unsafe_allow_html=True)
