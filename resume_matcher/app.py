import streamlit as st
import pandas as pd
import tempfile
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.extractor import extract_resume_text
from src.matcher import match_resume_to_job

st.set_page_config(page_title="AI Resume Matcher", layout="wide")
st.title("AI-Powered Resume Screener")

BASE_DIR = Path(__file__).resolve().parent
SKILL_FILE = BASE_DIR / "data" / "skills.txt"

with st.sidebar:
    st.header("Settings")
    t_weight = st.slider("Text Similarity Weight", 0.0, 1.0, 0.7)
    s_weight = 1.0 - t_weight
    st.write(f"Skill Match Weight: {round(s_weight, 1)}")

jd_input = st.text_area("Paste Job Description:", height=200)
uploaded_files = st.file_uploader(
    "Upload resumes", type=["pdf", "docx"], accept_multiple_files=True
)

if st.button("Analyse & Rank"):
    if not jd_input:
        st.error("Please paste a job description.")
    elif not uploaded_files:
        st.error("Please upload at least one resume.")
    else:
        all_results = []

        for file in uploaded_files:
            tmp_path = None
            try:
                suffix = Path(file.name).suffix.lower()
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=suffix
                ) as tmp:
                    tmp.write(file.getbuffer())
                    tmp_path = tmp.name

                raw_text = extract_resume_text(tmp_path)
                result = match_resume_to_job(
                    raw_text, jd_input, SKILL_FILE, t_weight, s_weight
                )
                result["Candidate"] = file.name
                result["matched_skills"] = ", ".join(result["matched_skills"])
                result["missing_skills"] = ", ".join(result["missing_skills"])
                all_results.append(result)

            except Exception as e:
                st.error(f"Failed to process {file.name}: {e}")

            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)

        if not all_results:
            st.warning("No resumes could be processed successfully.")
        else:
            all_results.sort(key=lambda x: x["final_score"], reverse=True)
            st.write("### Ranking Results")

            df = pd.DataFrame(all_results).rename(columns={
                "final_score": "Final Score (%)",
                "text_similarity": "Text Similarity (%)",
                "skill_score": "Skill Match (%)",
                "matched_skills": "Matched Skills",
                "missing_skills": "Missing Skills",
                "Candidate": "Candidate",
            })

            st.dataframe(df, use_container_width=True)
