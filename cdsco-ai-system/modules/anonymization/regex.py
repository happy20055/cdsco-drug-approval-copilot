

import re


def detect_emails(text):
    return re.findall(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        text
    )


def detect_phone_numbers(text):
    return re.findall(
        r"(?:\+91[\s\-]?|0)?[6-9]\d{9}\b",
        text
    )


def detect_hospital(text):
    return re.findall(
        r"\b[A-Z][a-zA-Z]+\s(?:Hospital|Clinic|Medical Center)\b",
        text
    )