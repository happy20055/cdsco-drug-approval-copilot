# CDSCO Drug Approval Copilot 

An AI-powered agentic copilot designed to automate the pre-screening and compliance auditing of clinical trial applications and Serious Adverse Event (SAE) reports for the **Central Drugs Standard Control Organisation (CDSCO)**. 

This system turns days of manual regulatory review into a 30-second automated scan—flagging missing compliance columns, checking report similarity, and providing an interactive RAG chatbot to query clinical findings locally.

---

##  Core Capabilities

* **Hybrid Text Extraction (OCR):** Extracts digital text from PDFs and automatically falls back to a local **Tesseract-OCR** engine to run high-resolution text extraction on scanned/image-only pages.
* **PII Anonymization (Privacy Compliance):** Redacts patient names, phone numbers, email addresses, and medical centers using title-case sequence heuristics and regular expressions.
* **Hierarchical Abstractive Summarization:** Employs a recursive chunk-and-summarize approach using **`BART-large-cnn`** to compile long trials (200+ pages) into structured compliance summaries.
* **Zero-Shot Event Classification:** Categorizes the document type and predicts severity levels ("death", "hospitalization", etc.) using a zero-shot **BART-MNLI** model.
* **Regulatory Field Checklists:** Audits text to verify the presence of mandatory regulatory columns (Patient Details, Drug Name, Adverse Events, and Doctor signatures).
* **Document Lineage & Revisions:** Compares two documents using cosine similarity metrics and displays sentence-by-sentence addition, deletion, and modification diffs.
* **Interactive RAG Chatbot:** A local, private Q&A chatbot using **`Llama-3-8B-Instruct`** (via Ollama) mapped onto a hierarchical semantic search index using **`all-MiniLM-L6-v2`**.

---

##  Tech Stack & AI Models

* **Frontend:** Vanilla HTML5, Glassmorphic CSS3 (Obsidian Dark Theme), JavaScript (ES6)
* **Backend:** FastAPI, Uvicorn, Python 3.9+
* **PDF Processing & Layouts:** PyMuPDF (`fitz`), ReportLab
* **OCR Engine:** pytesseract (with Windows local binaries)
* **Machine Learning Frameworks:** PyTorch, Transformers, SentenceTransformers
* **Hosted Local LLM:** Ollama (`llama3`)

---

##  Repository Structure

```directory
cdsco-drug-approval-copilot/
├── api/
│   └── main.py              # FastAPI server, endpoints, and chatbot RAG router
├── preprocessing/
│   ├── loader.py            # Hybrid PDF text loader & Tesseract wrapper
│   ├── cleaner.py           # Text error-corrector & sanitization
│   └── pipeline.py          # Data pipeline orchestrator
├── modules/
│   ├── anonymization/       # PII redaction (Regex + Capital casing)
│   ├── classification/      # Zero-shot document classification
│   ├── completeness_check/  # Mandatory field checker & severity scoring
│   ├── duplicate_detection/ # Document cosine similarity matching
│   ├── comparison/          # Sentence-level change comparisons
│   └── reporting/           # ReportLab sequenced PDF generator
├── Tesseract-OCR/           # Local OCR engine binaries (Windows)
├── samples/                 # Sample PDFs for clinical trials and audits
├── Dockerfile               # Hugging Face Spaces deployment instructions
├── requirements.txt         # Project package dependencies
└── PROJECT_GUIDE.md         # Detailed developer architecture guide
