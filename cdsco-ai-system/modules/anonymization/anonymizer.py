import re
from modules.anonymization.regex import (
    detect_emails,
    detect_phone_numbers,
    detect_hospital
)



def extract_field(text, field_name):
    pattern = rf"{field_name}\s*:\s*([^\n]+)"
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        value = match.group(1).strip()
        value = re.split(
            r"(Doctor|Hospital|Email|Phone|Age|Gender)\s*:",
            value
        )[0]
        return value.strip()

    return None



def safe_replace(text, value):
    if value:
        return re.sub(re.escape(value), "[REDACTED]", text)
    return text



def mask_person_names(text):
    blacklist = [
        "Department", "Center", "Division", "Drug",
        "Hospital", "University", "Services", "Office",
        "Research", "Evaluation", "Health",
        "Number", "Name", "Date", "Applicant",
        "Director", "Reviewer", "Staff"
    ]

    def replace(match):
        full = match.group()
        word1, word2 = full.split()

        
        if word1 in blacklist or word2 in blacklist:
            return full

        
        if any(char.isdigit() for char in full):
            return full

        
        if full + ":" in text:
            return full

        return "[NAME]"

    return re.sub(r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b", replace, text)



def anonymize(text):
    anonymized_text = text
    detected_entities = set()

    
    for email in detect_emails(text):
        anonymized_text = safe_replace(anonymized_text, email)
        detected_entities.add(email)

    
    for phone in detect_phone_numbers(text):
        anonymized_text = safe_replace(anonymized_text, phone)
        detected_entities.add(phone)

   
    name = extract_field(text, "Patient Name")
    if name:
        anonymized_text = safe_replace(anonymized_text, name)
        detected_entities.add(name)

    
    doctor = extract_field(text, "Doctor")
    if doctor:
        anonymized_text = safe_replace(anonymized_text, doctor)
        detected_entities.add(doctor)

    
    hospital = extract_field(text, "Hospital")
    if hospital:
        anonymized_text = safe_replace(anonymized_text, hospital)
        detected_entities.add(hospital)

    
    for hosp in detect_hospital(text):
        anonymized_text = safe_replace(anonymized_text, hosp)
        detected_entities.add(hosp)

    
    anonymized_text = mask_person_names(anonymized_text)

    return {
        "anonymized_text": anonymized_text,
        "detected_entities": list(detected_entities)
    }