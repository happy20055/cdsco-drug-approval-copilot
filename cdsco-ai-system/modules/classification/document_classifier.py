from transformers import pipeline

_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        print("Loading classification model...")
        _classifier = pipeline(
            "zero-shot-classification",
            model="typeform/distilbert-base-uncased-mnli"
        )
    return _classifier


def classify_document(text, summary=""):

    classifier = get_classifier()

    combined = text[:800] + " " + summary[:500]

    labels = [
        "serious adverse event report",
        "clinical regulatory document",
        "general document"
    ]

    result = classifier(combined, labels)

    return {
        "type": result["labels"][0],
        "confidence": round(result["scores"][0], 3)
    }