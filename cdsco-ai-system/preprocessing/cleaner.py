import re

MEDICAL_SHORT_TERMS = {
    "mg", "ml", "mL", "kg", "iv", "IV", "bp", "BP",
    "hr", "HR", "rr", "RR", "sp", "O2", "pH"
}


def clean_token(token):
    if token.lower() in {t.lower() for t in MEDICAL_SHORT_TERMS}:
        return token

    if len(token) == 1 and not token.isalnum():
        return ""

    if re.search(r"[^a-zA-Z0-9\-/.]", token) and len(token) <= 2:
        return ""

    return token




def clean_line_tokens(line):
    tokens = line.split()
    cleaned = [clean_token(t) for t in tokens]
    return " ".join([t for t in cleaned if t])


def fix_ocr_errors(text):
    corrections = {
        "c1inical": "clinical",
        "stucly": "study",
        "drng": "drug",
        "patlent": "patient",
        "hospitai": "hospital",
        "deaih": "death"
    }

    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)

    return text


def clean_text(text):
    text = text.replace("\r", "\n")
    text = fix_ocr_errors(text)

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    lines = text.split("\n")
    clean_lines = []

    important_keywords = [
        "patient", "hospital", "doctor", "drug", "died",
        "death", "pain", "adverse", "event", "diagnosis",
        "treatment", "dose", "administered", "recovered",
        "age", "gender"
    ]

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if any(k in line.lower() for k in important_keywords):
            clean_lines.append(line)
            continue

        if len(line.split()) < 2:
            continue

        line = clean_line_tokens(line)

        if line:
            clean_lines.append(line)

    return "\n".join(clean_lines)


def remove_noise_lines(text, min_length=15):
    lines = text.split("\n")
    return "\n".join([l for l in lines if len(l.strip()) >= min_length])