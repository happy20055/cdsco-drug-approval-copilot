from sentence_transformers import SentenceTransformer, util

_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading comparison model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def split_sentences(text):
    return [s.strip() for s in text.split("\n") if len(s.strip()) > 20]


def compare_documents(text1, text2, threshold=0.75):

    model = get_model()

    sents1 = split_sentences(text1)
    sents2 = split_sentences(text2)

    emb1 = model.encode(sents1, convert_to_tensor=True)
    emb2 = model.encode(sents2, convert_to_tensor=True)

    added, removed, modified = [], [], []
    matched = set()

    
    for i, e2 in enumerate(emb2):
        scores = util.cos_sim(e2, emb1)[0]
        best_score = scores.max().item()
        best_idx = scores.argmax().item()

        if best_score < threshold:
            added.append(sents2[i])
        else:
            matched.add(best_idx)

            if best_score < 0.95:
                modified.append({
                    "old": sents1[best_idx],
                    "new": sents2[i],
                    "similarity": round(best_score, 3)
                })

    
    for i, s in enumerate(sents1):
        if i not in matched:
            removed.append(s)

    total_changes = len(added) + len(removed) + len(modified)
    change_ratio = total_changes / max(len(sents1), 1)

    return {
        "added": added[:5],
        "removed": removed[:5],
        "modified": modified[:5],
        "change_ratio": round(change_ratio, 3),
        "num_changes": total_changes
    }