


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


def generate_pdf(report, filename="cdsco_report.pdf"):

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    content = []

    
    content.append(Paragraph("<b>CDSCO AI REGULATORY REPORT</b>", styles["Title"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph(f"Generated on: {datetime.now()}", styles["Normal"]))
    content.append(Spacer(1, 20))

   
    def add_file_section(file_data, title):

        content.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        content.append(Spacer(1, 10))

        content.append(Paragraph(f"Document Type: {file_data['doc_type']}", styles["Normal"]))
        content.append(Paragraph(f"Completeness: {file_data['completeness']['completeness_score']}", styles["Normal"]))
        content.append(Paragraph(f"Severity: {file_data['completeness']['severity']['severity']}", styles["Normal"]))

        content.append(Spacer(1, 10))

        
        content.append(Paragraph("<b>Summary (Original)</b>", styles["Heading3"]))
        content.append(Paragraph(file_data["summary_original"], styles["Normal"]))

        content.append(Spacer(1, 10))

        content.append(Paragraph("<b>Summary (Anonymized)</b>", styles["Heading3"]))
        content.append(Paragraph(file_data["summary_anonymized"], styles["Normal"]))

        content.append(Spacer(1, 10))

        
        m = file_data.get("summary_metrics", {})

        content.append(Paragraph("<b>Summary Metrics</b>", styles["Heading3"]))
        content.append(Paragraph(f"Compression Ratio: {m.get('compression_ratio')}", styles["Normal"]))
        content.append(Paragraph(f"Reduction: {m.get('reduction_percent')}%", styles["Normal"]))

        content.append(Spacer(1, 20))


    add_file_section(report["file1"], "FILE 1")

 
    if "file2" in report:
        content.append(PageBreak())
        add_file_section(report["file2"], "FILE 2")

  
    content.append(Paragraph("<b>GLOBAL ANALYSIS</b>", styles["Heading2"]))

    if report.get("duplicate"):
        d = report["duplicate"]
        content.append(Paragraph(f"Duplicate: {d['is_duplicate']}", styles["Normal"]))
        content.append(Paragraph(f"Similarity Score: {d['similarity_score']}", styles["Normal"]))
        content.append(Paragraph(f"Confidence: {d['confidence']}", styles["Normal"]))

    if report.get("comparison"):
        c = report["comparison"]
        content.append(Paragraph("<b>Comparison Metrics</b>", styles["Heading3"]))
        content.append(Paragraph(f"Change Ratio: {c['change_ratio']}", styles["Normal"]))
        content.append(Paragraph(f"Number of Changes: {c['num_changes']}", styles["Normal"]))

    doc.build(content)

    return filename