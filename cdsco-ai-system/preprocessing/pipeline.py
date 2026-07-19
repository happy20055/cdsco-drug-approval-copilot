import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from preprocessing.loader import load_file
from preprocessing.cleaner import clean_text, remove_noise_lines
from preprocessing.splitter import split_sentences
from preprocessing.chunker import chunk_text

from modules.anonymization.anonymizer import anonymize
from modules.summarization.llm_summarizer import summarize_large_document



def preprocess_document(file_path):

    print("\nStarting preprocessing...\n")

    
    raw_text = load_file(file_path)

    if not raw_text.strip():
        raise ValueError("No text extracted")

   
    cleaned_text = clean_text(raw_text)

    if file_path.lower().endswith(".pdf"):
        cleaned_text = remove_noise_lines(cleaned_text)

   
    lines = cleaned_text.split("\n")

    start_index = 0
    for i, line in enumerate(lines):
        if any(k in line.lower() for k in [
            "introduction",
            "clinical",
            "study",
            "trial",
            "patients",
            "methods"
        ]):
            start_index = i
            break

    cleaned_text = "\n".join(lines[start_index:])

    print(f"Removed first {start_index} lines")

   
    anon_result = anonymize(cleaned_text)

    anonymized_text = anon_result["anonymized_text"]
    detected_entities = anon_result["detected_entities"]

   
    sentences = split_sentences(cleaned_text)
    anon_sentences = split_sentences(anonymized_text)

  
    chunks = chunk_text(sentences)
    anon_chunks = chunk_text(anon_sentences)

    if not chunks:
        chunks = [cleaned_text]

    if not anon_chunks:
        anon_chunks = [anonymized_text]

    print(f"Total chunks (original): {len(chunks)}")
    print(f"Total chunks (anonymized): {len(anon_chunks)}")

   
    print("Generating original summary...")
    result_normal = summarize_large_document(chunks, cleaned_text)

    print("Generating anonymized summary...")
    result_anon = summarize_large_document(anon_chunks, anonymized_text)


    summary_normal = result_normal["summary"]
    metrics_normal = result_normal["metrics"]   

    summary_anonymized = result_anon["summary"]
    metrics_anon = result_anon["metrics"]

   
    return {
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        "anonymized_text": anonymized_text,
        "entities": detected_entities,

        "summary_normal": summary_normal,
        "summary_anonymized": summary_anonymized,

        "summary_metrics": metrics_normal,
        "summary_metrics_anonymized": metrics_anon,

        "chunks": chunks,
        "chunk_summaries": result_normal.get("partial_summaries", [])
    }