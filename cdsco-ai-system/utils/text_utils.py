# def get_clean_preview(text, max_lines=8):
#     lines = text.split("\n")

#     good_lines = []

#     for line in lines:
#         if len(line.split()) > 5:
#             good_lines.append(line)

#         if len(good_lines) >= max_lines:
#             break

#     return "\n".join(good_lines)
"""
def get_clean_preview(text, max_lines=8):
    lines = text.split("\n")

    good_lines = []

    for line in lines:
        stripped = line.strip()

        # FIX: old threshold (>5 words) silently dropped valid structured lines
        # like "Doctor: Dr. Mehta" (3 words) or "Phone: 9876543210" (2 words).
        # Now we keep lines that either:
        #   - have more than 3 words, OR
        #   - look like a structured field (contain a colon)
        if len(stripped.split()) > 3 or ":" in stripped:
            good_lines.append(stripped)

        if len(good_lines) >= max_lines:
            break

    return "\n".join(good_lines)
"""
def get_clean_preview(text, length=500):
    text = text.replace("\n", " ")
    return text[:length]