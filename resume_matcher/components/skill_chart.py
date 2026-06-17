from __future__ import annotations

from typing import Any

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_radar_chart(result: dict) -> None:
    fig = go.Figure()
    categories = ["Text Similarity", "Skill Match", "Experience"]
    values = [
        result.get("Text Similarity (%)", 0),
        result.get("Skill Match (%)", 0),
        result.get("Experience Score (%)", 0),
    ]
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=result.get("Candidate", "Candidate"),
        line_color="#4361ee",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=300,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="var(--text)"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_score_distribution(scores: list[float]) -> None:
    fig = px.histogram(
        x=scores,
        nbins=10,
        labels={"x": "Score Range"},
        title="Score Distribution",
        color_discrete_sequence=["#4361ee"],
    )
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_skill_barchart(skill_counts: dict[str, int], title: str = "Top Skills") -> None:
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    if not sorted_skills:
        st.info("No skill data available.")
        return
    names, counts = zip(*sorted_skills)
    fig = px.bar(
        x=list(counts[::-1]),
        y=list(names[::-1]),
        orientation="h",
        title=title,
        color_discrete_sequence=["#4361ee"],
    )
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Count"),
        yaxis=dict(title=""),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_category_pie(category_counts: dict[str, int]) -> None:
    fig = px.pie(
        names=list(category_counts.keys()),
        values=list(category_counts.values()),
        title="Skills by Category",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_multi_radar(results: list[dict]) -> None:
    if not results:
        st.info("Select candidates to compare.")
        return
    fig = go.Figure()
    colors = px.colors.qualitative.Set2
    for i, result in enumerate(results):
        categories = ["Text Similarity", "Skill Match", "Experience"]
        values = [
            result.get("Text Similarity (%)", 0),
            result.get("Skill Match (%)", 0),
            result.get("Experience Score (%)", 0),
        ]
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=result.get("Candidate", f"Candidate {i+1}"),
            line_color=colors[i % len(colors)],
            opacity=0.7,
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=400,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
