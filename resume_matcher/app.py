# UI for resume matcher
# importing dependecnies
import streamlit as st
import os
import pandas as pd
import sys
from pathlib import Path

# Add project root to PYTHONPATH to make sure there are no problems
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))
from resume_matcher.src.extractor import extract_resume_text
from resume_matcher.src.matcher import match_resume_to_job

# Page heading
st.set_page_config(page_title="AI Resume Matcher", layout="wide")
st.title("AI-Powered Resume Screener")

BASE_DIR = Path(__file__).resolve().parent
SKILL_FILE = BASE_DIR / "data" / "skills.txt"

# side bar 
with st.sidebar:
    st.header("Settings")
    t_weight = st.slider("Text Similarity Weight", 0.0, 1.0, 0.7)
    s_weight = 1.0 - t_weight
    st.write(f"Skill Match Weight: {round(s_weight, 1)}")

jd_input = st.text_area("Paste Job Description:", height=200)
uploaded_files = st.file_uploader("Upload resumes", type=['pdf', 'docx'],
                                  accept_multiple_files=True)

# Analyase and rank button 
if st.button("Analyse & Rank"):
    if jd_input and uploaded_files:
        all_results = []

        for file in uploaded_files:
            temp_path = f"temp_{file.name}"
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())

            raw_resume_text = extract_resume_text(temp_path)
            result = match_resume_to_job(raw_resume_text, jd_input, SKILL_FILE, t_weight, s_weight)
            result["Candidate"] = file.name
            result["matched_skills"] = ", ".join(result["matched_skills"])
            result["missing_skills"] = ", ".join(result["missing_skills"])
            all_results.append(result)


            os.remove(temp_path)

        all_results.sort(key=lambda x: x["final_score"], reverse=True)

        st.write("### Ranking Result")

        # We make it pandas data frame for better tablular structure
        df = pd.DataFrame(all_results)

        df = df.rename(columns={
            "final_score": "Final Score (%)",
            "text_similarity": "Text Similarity (%)",
            "skill_score": "Skill Match (%)",
            "matched_skills": "Matched Skills",
            "missing_skills": "Missing Skills",
            "Candidate": "Candidate"
        })

        st.dataframe(df, use_container_width=True)

    else:
        st.error("Please upload resumes and paste a job description.")
