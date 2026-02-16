# 🧠 Resume Matcher  
### Intelligent Resume ↔ Job Description Matching System

A **high-quality Machine Learning + NLP application** that evaluates how well a candidate’s resume aligns with a given job description by generating a **relevance score, extracted skills, and matching insights**.

Designed as a **portfolio-grade ML system**, this project demonstrates clean architecture, strong NLP fundamentals, and a production-style workflow suitable for **ML / AI internship evaluations**.

---

## 🌟 Why This Project Matters

Recruiters and hiring systems process **hundreds of resumes per role**, making manual screening inefficient and inconsistent.

**Resume Matcher** addresses this by:
- Automating resume–JD relevance evaluation
- Providing objective similarity scoring
- Extracting job-relevant skills
- Offering a clean and interactive UI

This project mirrors the **core logic behind early-stage Applicant Tracking Systems (ATS)**.

---

## 🚀 Key Capabilities

✔ Resume ↔ Job Description similarity scoring  
✔ Supports **PDF and DOCX** resumes  
✔ Dynamic **TF-IDF vectorization at runtime**  
✔ Skill extraction using curated datasets  
✔ Clean and intuitive **Streamlit UI**  
✔ Modular, scalable project structure  

---

## 🧠 Technical Overview

### 🔹 NLP Strategy
- Resume and job description text is:
  - Extracted
  - Cleaned & normalized
  - Vectorized using **TF-IDF**
- Similarity is computed using **Cosine Similarity**

> ⚠️ No pre-trained model is stored.  
> The TF-IDF vectorizer is **trained dynamically for each comparison**, ensuring flexibility and transparency.

### 🔹 Why TF-IDF?
- Lightweight and fast
- Interpretable and explainable
- Strong baseline for text similarity
- Commonly used in ATS prototypes

---

## 🖥️ Application Screenshots

### 🔹 Main Interface
Minimal and focused UI for uploading resumes and entering job descriptions.

![Streamlit UI](screenshots/image1)

---

### 🔹 Matching Results & Skill Insights
Displays the resume–JD match score along with extracted skills.

![Matching Results](screenshots/image2)

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
│   │   ├── extractor.py        # Resume text extraction (PDF/DOCX)
│   │   ├── processor.py        # Text preprocessing pipeline
│   │   ├── matcher.py          # TF-IDF similarity logic
│   │   └── __init__.py
│
├── screenshots/
│   ├── image1                  # Streamlit UI screenshot
│   └── image2                  # Matching results screenshot
│
├── test.py                     # Testing & experimentation
└── venv/                       # Virtual environment (local)
```

---

## 🧩 Component Breakdown

### 🔹 `app.py`
- Streamlit-based frontend
- Handles resume uploads and JD input
- Displays scores and extracted skills

### 🔹 `extractor.py`
- Extracts text from **PDF and DOCX** files
- Handles document parsing logic

### 🔹 `processor.py`
- Cleans and normalizes text
- Prepares data for vectorization

### 🔹 `matcher.py`
- Builds TF-IDF vectors dynamically
- Computes cosine similarity
- Outputs relevance score

### 🔹 `skills.txt`
- Keyword-based skills dataset
- Used for skill extraction and highlighting

---

## ⚙️ Installation & Execution

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Gugilla-Aakash/resume-screening-ml.git
cd resume-screening-ml
```

### 2️⃣ Install Dependencies
```bash
pip install -r resume_matcher/requirements.txt
```

### 3️⃣ Run the Application
```bash
streamlit run resume_matcher/app.py
```

---

## 📊 Output Explanation

- **Match Score**  
  Numerical similarity score between resume and job description

- **Extracted Skills**  
  Job-relevant skills identified from resume content

- **Explainability**  
  Fully transparent — no black-box ML models

---

## 🎯 Intended Use Cases

- ML / AI internship portfolio
- Resume screening system demo
- NLP similarity engine
- ATS proof-of-concept
- Clean, explainable ML project

---

## 🔮 Future Enhancements

- Resume ranking against multiple job descriptions
- Semantic similarity using BERT / Sentence Transformers
- Resume improvement suggestions
- Cloud deployment (Streamlit Cloud / AWS)
- Multi-language resume support

---

## 👨‍💻 Author

**Gugilla Aakash**  
Aspiring Machine Learning Engineer  

GitHub: https://github.com/Gugilla-Aakash

---

## ⭐ Final Note

If this project helped you understand real-world resume screening systems,  
consider starring the repository — it genuinely helps.

This project reflects **strong ML fundamentals, clean engineering, and practical design thinking**.
