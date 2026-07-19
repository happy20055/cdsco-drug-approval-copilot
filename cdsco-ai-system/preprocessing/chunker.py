def chunk_text(sentences, max_words=800, overlap_words=100):


    if not sentences:
        return []

    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        words = sentence.split()
        word_len = len(words)

        
        if current_word_count + word_len > max_words:
            chunks.append(" ".join(current_chunk))

            
            overlap_chunk = []
            overlap_count = 0

            for s in reversed(current_chunk):
                w = len(s.split())
                if overlap_count + w > overlap_words:
                    break
                overlap_chunk.insert(0, s)
                overlap_count += w

            current_chunk = overlap_chunk
            current_word_count = overlap_count

        current_chunk.append(sentence)
        current_word_count += word_len

    
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks