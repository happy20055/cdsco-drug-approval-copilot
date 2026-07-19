import sys
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
import httpx

sys.path.append(os.path.dirname(os.path.dirname(__file__)))



from preprocessing.pipeline import preprocess_document

from modules.classification.document_classifier import classify_document
from modules.completeness_check.completeness import check_completeness
from modules.duplicate_detection.duplicate_detector import detect_duplicate
from modules.comparison.document_comparator import compare_documents

from modules.reporting.report_builder import build_report
from modules.reporting.pdf_generator import generate_pdf



app = FastAPI()

SESSION_DATA = {}

class ChatRequest(BaseModel):
    question: str

async def call_ollama(question: str, context: str) -> str:
    url = "http://localhost:11434/api/chat"
    system_prompt = (
        "You are a helpful, professional medical regulatory assistant. "
        "Answer the user's question as accurately and clearly as possible using only the provided clinical document context. "
        "State facts exactly as they appear in the context. "
        "If the answer cannot be found in the context, say 'I cannot find that information in the document.' "
        "Do not make up facts or assume anything outside the context."
    )
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
    payload = {
        "model": "llama3",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return f"Local Ollama API returned status code: {response.status_code}"
    except Exception as e:
        return (
            "Error connecting to local Ollama. Please ensure Ollama is installed, "
            "running, and you have run 'ollama pull llama3' on your system. "
            f"Detail: {str(e)}"
        )


def get_next_report_filename(directory: Path, prefix="cdsco_report", extension="pdf") -> str:
    import re
    max_seq = 0
    pattern = re.compile(rf"^{prefix}_(\d+)\.{extension}$")
    if directory.exists():
        for entry in directory.iterdir():
            if entry.is_file():
                match = pattern.match(entry.name)
                if match:
                    seq = int(match.group(1))
                    if seq > max_seq:
                        max_seq = seq
    return f"{prefix}_{max_seq + 1}.{extension}"

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

UPLOAD_DIR = "data/raw"
os.makedirs(UPLOAD_DIR, exist_ok=True)




@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")



@app.post("/process")
async def process_files(
    file1: UploadFile = File(...),
    file2: UploadFile = File(None)
):

    try:


        path1 = os.path.join(UPLOAD_DIR, file1.filename)

        with open(path1, "wb") as buffer:
            shutil.copyfileobj(file1.file, buffer)

        print(f"File1 saved: {path1}")

       

        data1 = preprocess_document(path1)

        text1 = data1["cleaned_text"]
        summary1 = data1["summary_normal"]
        summary1_anon = data1["summary_anonymized"]
        metrics1 = data1["summary_metrics"]

        # Cache text chunks and chunk summaries for interactive Q&A chatbot
        SESSION_DATA["active_doc"] = {
            "chunks": data1.get("chunks", []),
            "chunk_summaries": data1.get("chunk_summaries", [])
        }

      

        doc_type1 = classify_document(text1, summary1)
        comp1 = check_completeness(text1, summary1)

       
        file1_data = {
            "doc_type": doc_type1,
            "completeness": comp1,
            "summary_original": summary1,
            "summary_anonymized": summary1_anon,
            "summary_metrics": metrics1
        }

       

        file2_data = None
        duplicate = None
        comparison = None

        if file2:
            path2 = os.path.join(UPLOAD_DIR, file2.filename)

            with open(path2, "wb") as buffer:
                shutil.copyfileobj(file2.file, buffer)

            print(f"File2 saved: {path2}")

            
            data2 = preprocess_document(path2)

            text2 = data2["cleaned_text"]
            summary2 = data2["summary_normal"]
            summary2_anon = data2["summary_anonymized"]
            metrics2 = data2["summary_metrics"]

            
            doc_type2 = classify_document(text2, summary2)
            comp2 = check_completeness(text2, summary2)

            
            file2_data = {
                "doc_type": doc_type2,
                "completeness": comp2,
                "summary_original": summary2,
                "summary_anonymized": summary2_anon,
                "summary_metrics": metrics2
            }

           

            duplicate = detect_duplicate(text1, text2)   
            comparison = compare_documents(text1, text2)

        
        report = build_report(
            file1_data,
            file2_data,
            duplicate,
            comparison
        )

        reports_dir = BASE_DIR / "data" / "reports"
        os.makedirs(reports_dir, exist_ok=True)
        pdf_filename = get_next_report_filename(reports_dir)
        pdf_path = reports_dir / pdf_filename

        generate_pdf(report, filename=str(pdf_path))

        print("PDF generated:", pdf_path)



        return {
    "message": "Processing complete",

    "summary": summary1,

    "summary_anonymized": summary1_anon,

    "summary_metrics": metrics1,

    "classification": doc_type1,

    "completeness": comp1,

    "duplicate": duplicate if duplicate else "Not Compared",

    "comparison": comparison if comparison else "No comparison document uploaded",

    "pdf_file": pdf_filename
}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/download/{filename}")
def download_pdf(filename: str):

    reports_dir = BASE_DIR / "data" / "reports"
    pdf_path = reports_dir / filename

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        path=str(pdf_path),
        filename=filename,
        media_type="application/pdf"
    )


from modules.duplicate_detection.duplicate_detector import get_model as get_similarity_model
from sentence_transformers import util

@app.post("/chat")
async def chat_with_doc(request: ChatRequest):
    active_doc = SESSION_DATA.get("active_doc")
    if not active_doc or not active_doc.get("chunks"):
        raise HTTPException(status_code=400, detail="No active document found. Please upload and analyze a document first.")

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # Hierarchical retrieval: search the chunk summaries
        similarity_model = get_similarity_model()
        query_emb = similarity_model.encode(question, convert_to_tensor=True)

        chunk_summaries = active_doc["chunk_summaries"]
        # Fallback to raw chunks if summaries are empty
        if not chunk_summaries:
            chunk_summaries = active_doc["chunks"]

        summaries_emb = similarity_model.encode(chunk_summaries, convert_to_tensor=True)
        scores = util.cos_sim(query_emb, summaries_emb)[0]

        best_idx = scores.argmax().item()
        retrieved_chunk = active_doc["chunks"][best_idx]

        # Call local Llama 3 via Ollama
        answer = await call_ollama(question, retrieved_chunk)

        return {
            "answer": answer,
            "matched_summary": chunk_summaries[best_idx],
            "chunk_index": best_idx
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)