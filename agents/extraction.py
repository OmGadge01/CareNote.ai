import re

from langchain_ollama import ChatOllama
from models.schemas import ClinicalData, Symptom


llm = ChatOllama(
    model="qwen3:4b",
    temperature=0,
)

structured_llm = llm.with_structured_output(ClinicalData)


def extract_vitals(note: str):

    blood_pressure = None
    temperature = None
    heart_rate = None

    bp_match = re.search(
        r"(?:BP|blood pressure)\s*(?:today\s*)?(?:is\s*)?"
        r"(\d{2,3}\s*/\s*\d{2,3})",
        note,
        re.IGNORECASE,
    )

    if bp_match:
        blood_pressure = bp_match.group(1).replace(" ", "")

    temp_match = re.search(
        r"(?:temperature|temp)\s*(?:is\s*)?"
        r"(\d{2}(?:\.\d+)?)",
        note,
        re.IGNORECASE,
    )

    if temp_match:
        temperature = temp_match.group(1)

    hr_match = re.search(
        r"(?:heart rate|HR|pulse)\s*(?:is\s*)?(\d{2,3})",
        note,
        re.IGNORECASE,
    )

    if hr_match:
        heart_rate = hr_match.group(1)

    return {
        "blood_pressure": blood_pressure,
        "temperature": temperature,
        "heart_rate": heart_rate,
    }


def extract_common_clinical_terms(note: str):

    text = note.lower()

    conditions = []
    symptoms = []

    # Prototype clinical vocabulary
    known_conditions = [
        "hypertension",
        "diabetes",
        "asthma",
        "migraine",
        "pneumonia",
    ]

    known_symptoms = [
        "headache",
        "fever",
        "cough",
        "fatigue",
        "nausea",
        "vomiting",
        "chest pain",
        "shortness of breath",
    ]

    for condition in known_conditions:

        if condition in text:
            conditions.append(condition)

    for symptom in known_symptoms:

        if symptom in text:

            duration = None

            # Example:
            # "headache for three days"
            duration_match = re.search(
                rf"{re.escape(symptom)}\s+for\s+"
                r"([a-z0-9\s]+?)(?:\.|,|$)",
                text,
            )

            if duration_match:
                duration = duration_match.group(1).strip()

            symptoms.append(
                Symptom(
                    name=symptom,
                    duration=duration,
                )
            )

    return conditions, symptoms


def extract_clinical_data(note: str):

    prompt = f"""
Extract information explicitly stated in this clinical note.

Extract:

- medical conditions
- symptoms
- medications
- visit purpose
- follow-up instructions

Do not diagnose.
Do not infer.
Do not provide medical advice.

Clinical note:

{note}
"""

    result = structured_llm.invoke(prompt)

    # --------------------------------------------------------
    # Deterministic extraction
    # --------------------------------------------------------

    vitals = extract_vitals(note)

    conditions, symptoms = extract_common_clinical_terms(note)

    # --------------------------------------------------------
    # Merge
    # --------------------------------------------------------

    if conditions:
        result.conditions = list(
            dict.fromkeys(
                result.conditions + conditions
            )
        )

    if symptoms:
        existing = {
            symptom.name.lower()
            for symptom in result.symptoms
        }

        for symptom in symptoms:

            if symptom.name.lower() not in existing:
                result.symptoms.append(symptom)

    result.vitals.blood_pressure = (
        vitals["blood_pressure"]
        or result.vitals.blood_pressure
    )

    result.vitals.temperature = (
        vitals["temperature"]
        or result.vitals.temperature
    )

    result.vitals.heart_rate = (
        vitals["heart_rate"]
        or result.vitals.heart_rate
    )

    # Detect follow-up from common wording
    if not result.follow_up:

        follow_up_match = re.search(
            r"follow[- ]?up\s+(?:in\s+)?([^\.]+)",
            note,
            re.IGNORECASE,
        )

        if follow_up_match:
            result.follow_up = (
                "in "
                + follow_up_match.group(1).strip()
            )

    # Detect visit purpose
    if not result.visit_type:

        if re.search(
            r"follow[- ]up",
            note,
            re.IGNORECASE,
        ):
            result.visit_type = "Follow-up"

    return result