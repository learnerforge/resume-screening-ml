from __future__ import annotations

from collections import Counter

import streamlit as st

from components.skill_chart import (
    render_skill_barchart,
    render_category_pie,
)

st.markdown(
    '<div class="section-header">Skills Analytics</div>',
    unsafe_allow_html=True,
)

results = st.session_state.get("results", [])
history = st.session_state.get("history", [])

all_results = list(results)
for session in history:
    all_results.extend(session.get("results", []))

if not all_results:
    st.info("No data yet. Run a matching session first.")
    st.stop()

all_matched: list[str] = []
all_missing: list[str] = []
all_skills_list: list[str] = []

for r in all_results:
    matched = r.get("Matched Skills") or r.get("matched_skills", "")
    missing = r.get("Missing Skills") or r.get("missing_skills", "")
    if isinstance(matched, str):
        skills = [s.strip() for s in matched.split(",") if s.strip()]
        all_matched.extend(skills)
        all_skills_list.extend(skills)
    if isinstance(missing, str):
        skills = [s.strip() for s in missing.split(",") if s.strip()]
        all_missing.extend(skills)
        all_skills_list.extend(skills)

skill_counts = Counter(all_skills_list)
matched_counts = Counter(all_matched)
missing_counts = Counter(all_missing)

categories = {
    "Languages": {"python", "java", "javascript", "typescript", "c++", "rust", "golang", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab"},
    "Frontend": {"react", "angular", "vue", "svelte", "html", "css", "jquery", "bootstrap", "tailwind"},
    "Backend": {"django", "flask", "fastapi", "spring", "node.js", "nodejs", "express", "dotnet", "rails", "laravel"},
    "Databases": {"sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "sqlite", "oracle"},
    "Cloud": {"aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "git"},
    "Data & ML": {"pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "machine learning", "deep learning", "nlp"},
}
category_dist: dict[str, int] = {}
for cat, cat_skills in categories.items():
    total = sum(skill_counts.get(s, 0) for s in cat_skills)
    if total > 0:
        category_dist[cat] = total
other = sum(v for s, v in skill_counts.items() if not any(s in cats for cats in categories.values()))
if other > 0:
    category_dist["Other"] = other

st.subheader("Top Skills in Candidate Pool")
render_skill_barchart(dict(skill_counts.most_common(20)), "Most Frequent Skills")

col_a, col_b = st.columns(2)
with col_a:
    if category_dist:
        render_category_pie(category_dist)
    else:
        st.info("No skills to categorize.")

with col_b:
    st.markdown("### Skill Summary")

    total_unique = len(skill_counts)
    total_occurrences = sum(skill_counts.values())
    top_skill = skill_counts.most_common(1)

    st.metric("Unique Skills Found", total_unique)
    st.metric("Total Skill Occurrences", total_occurrences)
    if top_skill:
        st.metric("Most Common Skill", f"{top_skill[0][0]} ({top_skill[0][1]})")

    if matched_counts:
        st.metric("Most Frequently Matched", f"{matched_counts.most_common(1)[0][0]} ({matched_counts.most_common(1)[0][1]})")
    if missing_counts:
        st.metric("Most Frequently Missing", f"{missing_counts.most_common(1)[0][0]} ({missing_counts.most_common(1)[0][1]})")

if missing_counts:
    st.subheader("Most Common Missing Skills")
    render_skill_barchart(
        dict(missing_counts.most_common(10)),
        "Skills missing from resumes (but required by JDs)",
    )
