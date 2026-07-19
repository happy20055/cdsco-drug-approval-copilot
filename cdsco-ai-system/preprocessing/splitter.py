import re

def split_sentences(text):
    

    if not text:
        return []

   
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)

    
    sentences = [
        s.strip()
        for s in sentences
        if len(s.strip()) > 10
    ]

    return sentences
