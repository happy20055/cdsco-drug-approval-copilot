from transformers import pipeline

_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading severity model...")
        _model = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
    return _model


def classify_severity(text):

    model = get_model()

    labels = [
        "death",
        "life threatening",
        "hospitalization",
        "serious adverse event",
        "not serious"
    ]

    result = model(text[:1000], labels)

    return {
        "severity": result["labels"][0],
        "confidence": round(result["scores"][0], 3)
    }


def check_completeness(text, summary=""):

    combined = (text + " " + summary).lower()

    fields = {
        "patient": ["patient"],
        "drug": ["drug", "treatment"],
        "adverse_event": ["adverse", "reaction", "death"],
        "doctor": ["doctor", "physician"]
    }

    present = []
    missing = []

    for field, keys in fields.items():
        if any(k in combined for k in keys):
            present.append(field)
        else:
            missing.append(field)

    score = round(len(present) / len(fields), 2)

    severity = classify_severity(combined)

    return {
        "present_fields": present,
        "missing_fields": missing,
        "completeness_score": score,
        "severity": severity
    }