from __future__ import annotations

import streamlit as st


def render_result_card(result: dict, selected: bool = False, on_click=None) -> None:
    score = result.get("Final Score (%)", 0)
    name = result.get("Candidate", "Unknown")
    text_sim = result.get("Text Similarity (%)", 0)
    skill_match = result.get("Skill Match (%)", 0)
    exp_score = result.get("Experience Score (%)", 0)
    matched = result.get("Matched Skills", "")
    missing = result.get("Missing Skills", "")

    card_class = "score-card selected" if selected else "score-card"

    st.markdown(
        f"""
        <div class="{card_class}" onclick="alert('{name}')">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div class="candidate-name">{name}</div>
                    <div class="sub-scores">
                        Text: {text_sim}% &middot; Skills: {skill_match}% &middot; Exp: {exp_score}%
                    </div>
                </div>
                <div class="score-value">{score}%</div>
            </div>
            <div style="margin-top: 8px;">
                <div style="height: 4px; background: var(--border); border-radius: 2px;">
                    <div style="height: 100%; width: {score}%; background: var(--primary); border-radius: 2px;"></div>
                </div>
            </div>
            <div style="margin-top: 8px; display: flex; flex-wrap: wrap;">
                {_skill_tags(matched, "matched")}
                {_skill_tags(missing, "missing")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _skill_tags(skills_str: str, kind: str) -> str:
    if not skills_str:
        return ""
    skills = [s.strip() for s in skills_str.split(",") if s.strip()]
    if not skills:
        return ""
    return "".join(f'<span class="skill-badge {kind}">{s}</span>' for s in skills)
