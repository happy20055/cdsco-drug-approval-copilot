from sentence_transformers import SentenceTransformer, util

_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading similarity model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def detect_duplicate(text1, text2):

    model = get_model()

    emb1 = model.encode(text1[:2000], convert_to_tensor=True)
    emb2 = model.encode(text2[:2000], convert_to_tensor=True)

    score = util.cos_sim(emb1, emb2).item()

    if score > 0.9:
        confidence = "High"
    elif score > 0.75:
        confidence = "Medium"
    else:
        confidence = "Low"

    return {
        "similarity_score": round(score, 3),
        "is_duplicate": score > 0.85,
        "confidence": confidence
    }