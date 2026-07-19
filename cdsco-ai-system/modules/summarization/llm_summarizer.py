from transformers import pipeline, logging


logging.set_verbosity_error()


summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)


def format_for_medical_summary(text):
    return f"""
Summarize the following medical document and extract:

- Drug name
- Indication
- Clinical trial results
- Safety / adverse events
- Conclusion

Text:
{text}
"""


def get_summary_metrics(original_text, summary):

    if not original_text or len(original_text) == 0:
        return {}

    compression_ratio = len(summary) / len(original_text)

    return {
        "original_length": len(original_text),
        "summary_length": len(summary),
        "compression_ratio": round(compression_ratio, 3),
        "reduction_percent": round((1 - compression_ratio) * 100, 2)
    }


def summarize_chunk(text, max_len=200, min_len=60):
    try:
        formatted_text = format_for_medical_summary(text)

        result = summarizer(
            formatted_text,
            max_length=max_len,
            min_length=min_len,
            do_sample=False
        )

        return result[0]['summary_text']

    except Exception as e:
        print("Error in chunk summarization:", e)
        return text[:300]



def summarize_large_document(chunks, original_text=None):

    print("Running BART summarization...")

    partial_summaries = []

    
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}")

        safe_text = chunk[:1000]
        summary = summarize_chunk(safe_text)

        partial_summaries.append(summary)

    
    grouped_summaries = []
    temp = ""

    for summary in partial_summaries:
        if len(temp) + len(summary) < 3000:
            temp += " " + summary
        else:
            grouped_summaries.append(temp.strip())
            temp = summary

    if temp:
        grouped_summaries.append(temp.strip())

    print("Number of grouped summaries:", len(grouped_summaries))

    
    second_level = []

    for i, group in enumerate(grouped_summaries):
        print(f"Refining group {i+1}/{len(grouped_summaries)}")

        refined = summarize_chunk(
            group[:2000],
            max_len=300,
            min_len=100
        )

        second_level.append(refined)

    
    print("Generating final detailed summary...")

    final_input = " ".join(second_level)

    final_prompt = f"""
Create a structured medical report with:

1. Drug Name
2. Indication
3. Clinical Trial Findings
4. Safety and Adverse Events
5. Risk Assessment
6. Final Conclusion

Text:
{final_input}
"""

    final_result = summarizer(
        final_prompt[:3000],
        max_length=800,
        min_length=300,
        do_sample=False
    )

    final_summary = final_result[0]['summary_text']

  
    metrics = {}

    if original_text:
        metrics = get_summary_metrics(original_text, final_summary)

   
    return {
        "summary": final_summary,
        "metrics": metrics,
        "partial_summaries": partial_summaries
    }