# This is used to extract the text from pdf and docx files(Since, resumes are
                                                           # often in .pdf or
                                                           # .docx files)

# Importing necessary dependencies
import pdfplumber
from docx import Document
from pathlib import Path

# Function to extract text from pdf file
def extract_text_from_pdf(pdf_file):
    text = []

    try:
        with pdfplumber.open(pdf_file) as pdf:
            for pages in pdf.pages:
                pages_text = pages.extract_text()
                if pages_text:
                    text.append(pages_text)

    except Exception as e:
        raise RuntimeError(f"Error reading PDF File: {e}")

    return " ".join(text)

# Function used to extract text from docx files
def extract_text_from_docx(docx_file):
    try:
        docx = Document(docx_file)
        text = [para.text for para in docx.paragraphs if para.text.strip()]

    except Exception as e:
        raise RuntimeError(f"Error reading DOCX file: {e}")

    return " ".join(text)

#  Function to extract text from uploaded resume 
def extract_resume_text(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(file_path)

    elif file_path.suffix.lower() == ".docx":
        return extract_text_from_docx(file_path)

    else:
        raise ValueError("Upload only PDF or DOCX files")
