from langgraph.graph import StateGraph, START, END

from agents.state import CareNoteState
from agents.extraction import extract_clinical_data


def extraction_node(state: CareNoteState):
    print("🔍 Extraction Agent running...")

    clinical_data = extract_clinical_data(
        state["clinical_note"]
    )

    return {
        "clinical_data": clinical_data
    }


def validation_node(state: CareNoteState):
    print("🔎 Validation Agent running...")

    data = state["clinical_data"]

    issues = []
    missing = []

    if not data:
        issues.append("No clinical data extracted.")

        return {
            "validation_issues": issues,
            "missing_information": missing,
        }

    # Required clinical information checks

    if not data.conditions:
        missing.append("Medical condition")

    if not data.symptoms:
        missing.append("Symptoms")

    if not data.vitals.blood_pressure:
        missing.append("Blood pressure")

    if not data.visit_type:
        missing.append("Visit type")

    # Medication information is optional
    # Follow-up is optional

    return {
        "validation_issues": issues,
        "missing_information": missing,
    }
    print("🔎 Validation Agent running...")

    data = state["clinical_data"]

    issues = []
    missing = []

    if not data:
        issues.append("No clinical data extracted.")
        return {
            "validation_issues": issues,
            "missing_information": missing,
        }

    if not data.vitals.blood_pressure:
        missing.append("Blood pressure")

    if not data.visit_type:
        missing.append("Visit type")

    return {
        "validation_issues": issues,
        "missing_information": missing,
    }


def documentation_node(state: CareNoteState):
    print("📝 Documentation Agent running...")

    data = state["clinical_data"]

    documentation = (
        f"Patient visit type: {data.visit_type or 'Not specified'}. "
        f"Conditions: {', '.join(data.conditions) or 'None documented'}. "
        f"Symptoms: {', '.join(s.name for s in data.symptoms) or 'None documented'}. "
        f"Blood pressure: "
        f"{data.vitals.blood_pressure or 'Not documented'}. "
        f"Medications: "
        f"{', '.join(data.medications) or 'None documented'}. "
        f"Follow-up: {data.follow_up or 'Not specified'}."
    )

    return {
        "documentation": documentation
    }


def followup_node(state: CareNoteState):
    print("📌 Follow-up Agent running...")

    follow_up = state["clinical_data"].follow_up

    if follow_up:
        task = f"Schedule follow-up: {follow_up}"
    else:
        task = None

    return {
        "follow_up_task": task
    }


def build_workflow():

    graph = StateGraph(CareNoteState)

    graph.add_node("extract", extraction_node)
    graph.add_node("validate", validation_node)
    graph.add_node("document", documentation_node)
    graph.add_node("followup", followup_node)

    graph.add_edge(START, "extract")
    graph.add_edge("extract", "validate")
    graph.add_edge("validate", "document")
    graph.add_edge("document", "followup")
    graph.add_edge("followup", END)

    return graph.compile()