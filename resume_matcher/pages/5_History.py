from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

st.markdown(
    '<div class="section-header">History</div>',
    unsafe_allow_html=True,
)

history = st.session_state.get("history", [])

if not history:
    st.info("No previous sessions found. Run a matching session first.")
    st.stop()

search = st.text_input("Search sessions...", placeholder="Filter by job description...")
filtered = history
if search:
    filtered = [
        s for s in filtered
        if search.lower() in (s.get("job_description", "") or "").lower()
    ]

st.markdown(f"**{len(filtered)} sessions** found")

for idx, session in enumerate(reversed(filtered)):
    ts = session.get("timestamp", "unknown")
    jd = (session.get("job_description") or "")[:120]
    jd_short = jd[:120] + "..." if len(jd) > 120 else jd
    results_count = len(session.get("results", []))
    top_score = max(
        (r.get("final_score", 0) for r in session.get("results", [])),
        default=0,
    )

    with st.expander(f"{ts} -- {jd_short}"):
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Candidates", results_count)
        col_b.metric("Top Score", f"{top_score}%")
        settings_used = session.get("settings", {})
        col_c.markdown(
            f"**Settings**  \n"
            f"Mode: {settings_used.get('mode', 'TF-IDF')}  \n"
            f"Weights: T={settings_used.get('text_weight', 0.7)}, "
            f"S={settings_used.get('skill_weight', 0.3)}, "
            f"E={settings_used.get('experience_weight', 0.0)}"
        )

        results = session.get("results", [])
        if results:
            import pandas as pd
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"Download Session CSV",
                data=csv,
                file_name=f"session_{ts.replace(':', '-')}.csv",
                mime="text/csv",
                key=f"hist_dl_{idx}",
            )

if st.button("Clear All History", type="secondary"):
    st.session_state.history = []
    history_path = Path(__file__).resolve().parents[1] / "data" / "history.json"
    with open(history_path, "w") as f:
        json.dump([], f)
    st.success("History cleared.")
    st.rerun()
