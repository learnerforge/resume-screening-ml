from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Resume Matcher",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = Path(__file__).resolve().parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "results" not in st.session_state:
    st.session_state.results = []
if "parsed_infos" not in st.session_state:
    st.session_state.parsed_infos = []
if "file_names" not in st.session_state:
    st.session_state.file_names = []
if "history" not in st.session_state:
    history_path = Path(__file__).resolve().parent / "data" / "history.json"
    if history_path.exists():
        try:
            with open(history_path) as f:
                st.session_state.history = json.load(f)
        except (json.JSONDecodeError, OSError):
            st.session_state.history = []
    else:
        st.session_state.history = []
if "jd_input" not in st.session_state:
    st.session_state.jd_input = ""
if "last_settings" not in st.session_state:
    st.session_state.last_settings = {}

if st.session_state.theme == "dark":
    st.markdown("""
    <style>
    :root {
        --bg: #0b1121 !important;
        --bg-secondary: #111827 !important;
        --bg-card: #1e293b !important;
        --text: #e2e8f0 !important;
        --text-secondary: #94a3b8 !important;
        --primary: #60a5fa !important;
        --primary-dark: #3b82f6 !important;
        --primary-light: #1e3a5f !important;
        --success: #34d399 !important;
        --success-light: #064e3b !important;
        --warning: #fbbf24 !important;
        --warning-light: #451a03 !important;
        --danger: #f87171 !important;
        --danger-light: #450a0a !important;
        --info: #38bdf8 !important;
        --info-light: #0c4a6e !important;
        --border: #334155 !important;
        --shadow: rgba(0, 0, 0, 0.3) !important;
        --shadow-lg: rgba(0, 0, 0, 0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)
