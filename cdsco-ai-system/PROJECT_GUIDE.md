# CDSCO AI Regulatory Analysis System - Developer & Architecture Guide

Welcome to the **CDSCO AI Regulatory Analysis System** guide. This document provides a deep, comprehensive overview of the application's architecture, directory structures, data pipeline, and AI models to help developers deploy, run, and modify the system.

---

## Table of Contents
1. [Overview & Core Features](#1-overview--core-features)
2. [System Architecture & Data Flow](#2-system-architecture--data-flow)
3. [File and Folder Map](#3-file-and-folder-map)
4. [Deep Dive on Machine Learning Models](#4-deep-dive-on-machine-learning-models)
5. [The Pipeline: Step-by-Step Data Processing](#5-the-pipeline-step-by-step-data-processing)
6. [Portability & Naming Conventions](#6-portability--naming-conventions)
7. [Installation & Operation Guide](#7-installation--operation-guide)

---

## 1. Overview & Core Features
The CDSCO AI Regulatory Analysis System is a specialized AI-powered compliance platform designed to process clinical trial documentation and Serious Adverse Event (SAE) reports. Key features include:
* **Hybrid Text Extraction:** Pulls raw digital text from PDFs or runs fallback local Tesseract OCR on scanned/unreadable image-only pages.
* **PII Anonymization:** Redacts names, phone numbers, email addresses, and medical center mentions via regular expressions and heuristic masking.
* **Abstractive Summarization:** Uses a hierarchical, recursive summarization approach to condense large documents into structured medical sections.
* **Zero-Shot Document Classification:** Detects the category of documents and predicts clinical event severity levels.
* **Compliance Checks:** Cross-references text to verify the presence of mandatory columns (patient details, drug names, adverse events, and doctors).
* **Document Lineage & Revisions:** Compares two documents to identify duplicates and produces sentence-level revision diffs (added, removed, or modified paragraphs).
* **PDF Report Generator:** Compiles all summaries and checks into a downloadable report with incrementing sequence indices.
* **Hierarchical RAG Chatbot:** Provides an interactive Q&A chatbot to query the uploaded document, utilizing local semantic search over chunk summaries and prompting Meta's **Llama-3-8B-Instruct** model locally.

---

## 2. System Architecture & Data Flow
The following flowchart illustrates the lifecycle of a document from UI upload, through backend pipelines, to report compilation and chat:

```
[ Frontend Dashboard (HTML/CSS/JS) ]
                 │
                 ├──► (Upload multipart File 1 & optional File 2) ──► [ FastAPI Backend (api/main.py) ]
                 │                                                                │
                 │                                                                ▼
                 │                                                [ Preprocessing Pipeline (pipeline.py) ]
                 │                                                                │
                 │                                                                ▼
                 │                                                [ Chunker / Hierarchical Summarization ]
                 │                                                                │
                 │                                                                ▼
                 │                                                [ JSON Results & Saved PDF Reports ]
                 │                                                                │
                 ▼                                                                ▼
         [ Q&A Input Box ] ──► POST /chat ──► [ Embed Question & Search Chunk Summaries (all-MiniLM-L6) ]
                                                                │
                                                                ▼
                                                [ Retrieve Matching Original Raw Text Chunk ]
                                                                │
                                                                ▼
                                                [ Prompt Llama-3-8B-Instruct via Local Ollama ]
```

---

## 3. File and Folder Map
Here is the layout of the source repository:

* **`api/`**
  * `main.py`: The FastAPI application entrypoint. Houses endpoints (`/`, `/process`, `/download`, and `/chat`) and manages temp uploads, sequencing, in-memory session caching, and RAG routing.
* **`preprocessing/`**
  * `pipeline.py`: Orchestrates loading, sanitizing, redacting, chunking, and summarizing documents.
  * `loader.py`: Performs hybrid text loading. Uses PyMuPDF (`fitz`) first, and falls back to rendering pages to images for `pytesseract` OCR if text density is low.
  * `cleaner.py`: Corrects common OCR spelling mistakes and splits lines to filter out headers and formatting noise.
  * `splitter.py`: Splits block text into a list of sentences based on regex terminal punctuation.
  * `chunker.py`: Clusters sentence lists into word-count-bounded blocks (800 words max, 100 overlap words) so they fit inside context windows.
* **`modules/`**
  * `anonymization/`
    * `anonymizer.py`: Orchestrates phone/email/hospital replacement and applies capital-letter title case masking to obscure human names.
    * `regex.py`: Regular expressions for standard entity matches.
  * `classification/`
    * `document_classifier.py`: Zero-shot classifier identifying standard regulatory document kinds.
  * `completeness_check/`
    * `completeness.py`: Verification checks for mandatory columns and zero-shot clinical severity predictions.
  * `duplicate_detection/`
    * `duplicate_detector.py`: Encodes the first 2,000 characters to evaluate document similarity.
  * `comparison/`
    * `document_comparator.py`: Cosine similarity-based mapping of sentence additions, deletions, and updates.
  * `reporting/`
    * `pdf_generator.py`: Generates the PDF layout and styles using ReportLab.
    * `report_builder.py`: Packs structured responses.
* **`utils/`**
  * `config.py`: Configuration variables (chunk sizes, overlap parameters).
  * `text_utils.py`: Text processing helpers.
* **`frontend/`**
  * `index.html`: The user interface dashboard structure.
  * `style.css`: Obsidian dark theme styles, animations, chatbot bubbles, and input layouts.
  * `script.js`: Handles drag-and-drop actions, loading state transitions, renders JSON responses into cards, and manages chatbot messaging loops.
* **`Tesseract-OCR/`**
  * Contains the local Windows Tesseract OCR binaries and libraries.
* **`requirements.txt`**
  * Lists all python package dependencies and version requirements.

---

## 4. Deep Dive on Machine Learning Models
The core processing models run locally and are loaded dynamically (lazy-loaded on demand during the first request) using standard CPU execution:

| Model ID | Module Location | Deep Learning Task | Size / RAM | Role in Dashboard |
| :--- | :--- | :--- | :--- | :--- |
| **`facebook/bart-large-cnn`** | `llm_summarizer.py` | Abstractive Summarization | ~1.62 GB | Condenses text blocks recursively and creates structured medical summaries. |
| **`facebook/bart-large-mnli`** | `completeness.py` | Zero-Shot Entailment | ~1.63 GB | Analyzes reports to predict safety severities ("death", "hospitalization", etc.). |
| **`typeform/distilbert-base-uncased-mnli`** | `document_classifier.py` | Zero-Shot Classification | ~268 MB | Categorizes documents (e.g. serious adverse event report, clinical document). |
| **`all-MiniLM-L6-v2`** | `duplicate_detector.py`, `document_comparator.py` | Sentence Transformers | ~120 MB | Encodes sentences to calculate cosine similarity for duplicate, comparison, and chatbot retrieval. |
| **`Llama-3-8B-Instruct`** | `api/main.py` (via API) | Conversational Chatbot | ~4.70 GB | Runs locally on the target machine (via Ollama) to answer Q&A queries. |

---

## 5. The Pipeline: Step-by-Step Data Processing

1. **Upload & Save:** FastAPI saves the uploaded files (File 1, and optionally File 2) into `data/raw/`.
2. **Text Extraction & Cleanup:** The loader reads the file. If it's a PDF, pages with text content under 50 characters are rasterized and processed using the local `Tesseract-OCR/tesseract.exe`.
3. **Keyword Trimming:** The system searches the first few lines for typical intro keywords ("introduction", "clinical", "trial", "patients") and trims out title pages and tables of contents to feed relevant text to the LLMs.
4. **Anonymization (PII Masking):** Emails, phone numbers, and hospitals matching regex rules are replaced with `[REDACTED]`. Human names matching capitalization sequences (excluding common blacklist words) are masked as `[NAME]`.
5. **Hierarchical Summarization:** The text is sentence-split and grouped into chunks. Each chunk is summarized using `facebook/bart-large-cnn`. If there are multiple chunks, their summaries are grouped and summarized again to generate a cohesive final medical report.
6. **Zero-Shot Checks:** The classifier models evaluate the document type and severity, while rule-based lookups inspect the text for required columns.
7. **Lineage Comparison:** If a second document was supplied, both are encoded to calculate overall cosine match. Individual sentences are compared to identify additions, removals, and modifications.
8. **PDF Build:** The report builder constructs the JSON response and generates a stylized PDF containing all results.
9. **Interactive Chat Q&A:** The backend caches the text chunks and chunk summaries. When the user asks a question via the chatbot UI, the backend embeds the query, searches the chunk summaries using `all-MiniLM-L6-v2` (cos-sim), retrieves the corresponding raw detailed chunk, and prompts local **Llama-3-8B-Instruct** (via Ollama API) with the chunk as context to produce a citation-based answer.

---

## 6. Portability & Naming Conventions
* **Dynamic Base Resolving:** The application uses `Path(__file__).resolve().parent.parent` to determine the project directory dynamically. This allows the folder to be shared and run on another Windows system without breaking paths.
* **Auto-Incrementing Filenames:** Generated reports are saved under `data/reports/`. The system dynamically scans existing files in that folder to determine the highest suffix number and increments it (e.g., saving the next report as `cdsco_report_3.pdf`).
* **Dynamic Serves:** The `/download/{filename}` endpoint serves PDF files directly from the portable `data/reports/` folder.

---

## 7. Installation & Operation Guide

### Prerequisites (For Windows)
* **Python:** Python 3.9 or higher installed.
* **Tesseract Binary:** The `Tesseract-OCR` folder containing `tesseract.exe` must be located inside the project root folder.
* **Ollama (For Chatbot):** Download and install [Ollama](https://ollama.com/) (100% free/local model host). Open your terminal and pull the Llama-3 model:
  ```bash
  ollama pull llama3
  ```
  Ensure the Ollama application is running in the background before starting the FastAPI app.

### Step-by-Step Setup
1. **Navigate to the inner project directory:**
   ```bash
   cd cdsco-ai-system
   ```
2. **Install all dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Start the FastAPI backend server:**
   ```bash
   python api/main.py
   ```
4. **Access the application:**
   Open your browser and go to `http://127.0.0.1:8000`.

*Note: The first time you click "Execute Deep Analysis", the application will pause to download the 3.6 GB of model weights from Hugging Face. Subsequent runs will process instantly.*
