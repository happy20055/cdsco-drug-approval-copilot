import fitz
import pytesseract
import os
from PIL import Image

from pathlib import Path

import platform

BASE_DIR = Path(__file__).resolve().parent.parent

current_os = platform.system()

if current_os == "Windows":
    TESSERACT_PATH = BASE_DIR / "Tesseract-OCR" / "tesseract.exe"
    if not TESSERACT_PATH.exists():
        raise FileNotFoundError(
            f"Tesseract not found at: {TESSERACT_PATH}"
        )
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)
    print("Using Windows Local Tesseract:", TESSERACT_PATH)
else:
    pytesseract.pytesseract.tesseract_cmd = "tesseract"
    print("Using Linux System Tesseract")

print("NEW LOADER FILE RUNNING")


def extract_text_hybrid(doc):
    text = ""

    total_pages = len(doc)
    print(f"Total pages in PDF: {total_pages}")

    for i in range(total_pages):
        page = doc[i]

        page_text = page.get_text()

        
        if page_text and len(page_text.strip()) > 50:
            text += page_text + "\n"

       
        else:
            print(f"OCR page {i+1}/{total_pages}")

            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            ocr_text = pytesseract.image_to_string(img)
            text += ocr_text + "\n"

    return text



def load_pdf(file_path):
    doc = fitz.open(file_path)

    print(f"Opening PDF with {len(doc)} pages")

    text = extract_text_hybrid(doc)

    return text



def load_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()



def load_file(file_path):
    if file_path.lower().endswith(".pdf"):
        return load_pdf(file_path)

    elif file_path.lower().endswith(".txt"):
        return load_txt(file_path)

    else:
        raise ValueError("Unsupported file format")