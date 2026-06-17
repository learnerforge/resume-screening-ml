from __future__ import annotations

import pandas as pd
import streamlit as st


def render_candidate_table(results: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(results)
    display_cols = [
        "Candidate",
        "Final Score (%)",
        "Text Similarity (%)",
        "Skill Match (%)",
        "Experience Score (%)",
        "Matched Skills",
        "Missing Skills",
    ]
    available = [c for c in display_cols if c in df.columns]
    df_display = df[available]

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Final Score (%)": st.column_config.ProgressColumn(
                "Final Score (%)",
                help="Overall match score",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "Text Similarity (%)": st.column_config.NumberColumn(
                "Text Similarity (%)", format="%.1f%%"
            ),
            "Skill Match (%)": st.column_config.NumberColumn(
                "Skill Match (%)", format="%.1f%%"
            ),
            "Experience Score (%)": st.column_config.NumberColumn(
                "Experience Score (%)", format="%.1f%%"
            ),
        },
    )
    return df
