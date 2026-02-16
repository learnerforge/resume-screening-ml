# 🧠 Resume Matcher  
### Intelligent Resume ↔ Job Description Matching System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-NLP-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-red)
![spaCy](https://img.shields.io/badge/spaCy-NLP-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Live%20%26%20Working-brightgreen)

---
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-brightgreen)](https://resume-screening-ml-xnnbsouaxd4onthir8k27g.streamlit.app/)

A **production-style Machine Learning + NLP application** that evaluates how well a candidate’s resume matches a given job description by generating a **relevance score, extracted skills, and matching insights**.

This project is **fully deployed**, interactive, and designed as a **high-impact ML portfolio project** for internships and entry-level ML roles.

---

## 🔗 Live Demo (Deployed)

👉 **Try the application here:**  
🌐 https://resume-screening-ml-xnnbsouaxd4onthir8k27g.streamlit.app/

> No setup required — upload a resume, add a job description, and get instant results.

---

## 🌟 Why This Project Matters

Recruiters and hiring platforms process **hundreds of resumes per role**, making manual screening:
- Time-consuming
- Inconsistent
- Error-prone

**Resume Matcher** automates the first screening layer by:
- Objectively comparing resume content with job requirements
- Highlighting skill relevance
- Providing transparent, explainable similarity scores

This mirrors the **core logic behind real-world ATS (Applicant Tracking Systems)**.

---

## 🚀 Key Features

✔ Resume ↔ Job Description similarity scoring  
✔ Supports **PDF and DOCX** resumes  
✔ **Live deployed Streamlit web application**  
✔ Dynamic **TF-IDF vectorization at runtime**  
✔ Skill extraction using curated datasets  
✔ Clean, responsive, recruiter-friendly UI  

---

## 🧠 Technical Approach

### 🔹 NLP & ML Strategy
- Resume and job description text is:
  - Extracted from documents
  - Cleaned and normalized
  - Vectorized using **TF-IDF**
- Similarity is computed using **Cosine Similarity**

> ⚠️ No static or pre-trained model is stored.  
> The TF-IDF vectorizer is **trained dynamically for each comparison**, ensuring flexibility and up-to-date relevance.

### 🔹 Why TF-IDF?
- Lightweight and fast
- Highly interpretable (important for ATS systems)
- Strong baseline for text similarity problems
- Easy to deploy and scale

---

## 🖥️ Application Screenshots

### 🔹 Main Interface
Upload resumes and enter job descriptions through a clean, minimal UI.

![Main UI](screenshots/image1)

---

### 🔹 Matching Results & Skill Insights
Displays match score and extracted skills clearly and intuitively.

![Results View](screenshots/image2)

---

## 🧱 Project Structure

The repository follows a **clean separation of concerns** between UI, logic, and data.

```
resume-screening-ml/
│
├── resume_matcher/
│   ├── app.py                  # Streamlit UI entry point
│   ├── requirements.txt        # Project dependencies
│   │
│   ├── data/
│   │   ├── skills.txt          # Curated skills dataset
│   │   └── __init__.py
│   │
│   ├── src/
│   │   ├── extractor.py        # PDF & DOCX text extraction
│   │   ├── processor.py        # Text preprocessing (spaCy)
│   │   ├── matcher.py          # TF-IDF & similarity logic
│   │   └── __init__.py
│
├── screenshots/
│   ├── image1                  # UI screenshot
│   └── image2                  # Results screenshot
│
├── test.py                     # Testing & experimentation
└── venv/                       # Local virtual environment
```

---

## 🧩 Module Breakdown

### 🔹 `app.py`
- Streamlit-based frontend
- Handles resume uploads and job description input
- Displays match scores and extracted skills

### 🔹 `extractor.py`
- Extracts raw text from **PDF and DOCX** resumes
- Handles document parsing and edge cases

### 🔹 `processor.py`
- Cleans and normalizes text using **spaCy**
- Prepares data for vectorization

### 🔹 `matcher.py`
- Builds TF-IDF vectors dynamically
- Computes cosine similarity
- Outputs relevance score

### 🔹 `skills.txt`
- Keyword-based skills dataset
- Used for skill extraction and highlighting

---

## ⚙️ Local Installation & Execution

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Gugilla-Aakash/resume-screening-ml.git
cd resume-screening-ml
```

### 2️⃣ Install Dependencies
```bash
pip install -r resume_matcher/requirements.txt
```

### 3️⃣ Run the App Locally
```bash
streamlit run resume_matcher/app.py
```

---

## 📊 Output Explanation

- **Match Score**  
  Numerical similarity score between resume and job description

- **Extracted Skills**  
  Relevant skills detected in the resume

- **Explainability**  
  Fully transparent — no black-box predictions

---

## 🎯 Use Cases

- Resume screening automation
- ATS-style matching demo
- NLP similarity engine
- ML / AI internship portfolio
- Deployed ML system showcase

---

## 🔮 Future Enhancements

- Resume ranking against multiple job descriptions
- Semantic similarity using BERT / Sentence Transformers
- Resume improvement suggestions
- Cloud scaling and performance optimization
- Multi-language resume support

---

## 👨‍💻 Author

**Gugilla Aakash**  
Aspiring Machine Learning Engineer  

GitHub: https://github.com/Gugilla-Aakash

---

## ⭐ Final Note

This project is **fully deployed, functional, and designed with real-world constraints in mind**.

If you find it useful or insightful, consider starring the repository — it genuinely helps.
