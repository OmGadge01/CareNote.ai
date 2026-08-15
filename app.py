import streamlit as st

from agents.workflow import build_workflow
from database.db import init_db

init_db()


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="CareNote AI",
    page_icon="🩺",
    layout="wide",
)


# ============================================================
# Styling
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }

        .app-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .app-subtitle {
            color: #64748b;
            margin-bottom: 2rem;
        }

        .result-card {
            background: white;
            padding: 1.2rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            min-height: 150px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Session state
# ============================================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "approved" not in st.session_state:
    st.session_state.approved = False


# ============================================================
# Header
# ============================================================

st.markdown(
    '<div class="app-title">🩺 CareNote AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="app-subtitle">'
    "Agentic clinical documentation assistant • Human-in-the-loop"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.header("Clinician")

    st.success("● Demo Mode")

    st.write("Dr. Sarah Smith")

    st.divider()

    st.caption("CareNote AI Prototype")
    st.caption("Synthetic patient data only")


# ============================================================
# Patient information
# ============================================================

st.subheader("New Clinical Documentation")

col1, col2 = st.columns([1, 3])

with col1:

    patient_id = st.selectbox(
        "Patient",
        [
            "P001 — Alex Morgan",
            "P002 — Sarah Williams",
            "P003 — David Brown",
        ],
    )

with col2:

    visit_type = st.selectbox(
        "Visit type",
        [
            "Follow-up",
            "General Consultation",
            "Routine Check-up",
        ],
    )


# ============================================================
# Clinical note
# ============================================================

note = st.text_area(
    "Clinical Note",
    height=220,
    placeholder="Enter the clinician's unstructured note here...",
)


# ============================================================
# Analyze button
# ============================================================

if st.button(
    "✨ Analyze Clinical Note",
    type="primary",
    use_container_width=True,
):

    if not note.strip():

        st.warning("Please enter a clinical note.")

    else:

        workflow = build_workflow()

        initial_state = {
            "clinical_note": note,
            "clinical_data": None,
            "validation_issues": [],
            "missing_information": [],
            "documentation": None,
            "follow_up_task": None,
            "safety_flags": [],
        }

        with st.status(
            "Running CareNote AI agents...",
            expanded=True,
        ):

            st.write("🔍 Documentation Agent")
            st.write("🔎 Validation Agent")
            st.write("📝 Documentation Agent")
            st.write("📌 Follow-up Agent")

            result = workflow.invoke(initial_state)

        st.session_state.analysis_result = result
        st.session_state.approved = False

        st.rerun()


# ============================================================
# Display results
# ============================================================

result = st.session_state.analysis_result


if result:

    st.divider()

    st.subheader("Analysis Results")

    data = result["clinical_data"]

    col1, col2, col3 = st.columns(3)


    # --------------------------------------------------------
    # Clinical data
    # --------------------------------------------------------

    with col1:

        st.markdown(
            '<div class="result-card">',
            unsafe_allow_html=True,
        )

        st.markdown("### 📋 Clinical Data")

        st.write(
            f"**Visit:** "
            f"{data.visit_type or visit_type}"
        )

        st.write(
            f"**Condition:** "
            f"{', '.join(data.conditions) or 'None'}"
        )

        symptoms = ", ".join(
            symptom.name
            for symptom in data.symptoms
        )

        st.write(
            f"**Symptoms:** "
            f"{symptoms or 'None'}"
        )

        st.write(
            f"**Blood Pressure:** "
            f"{data.vitals.blood_pressure or 'Not documented'}"
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    with col2:

        st.markdown(
            '<div class="result-card">',
            unsafe_allow_html=True,
        )

        st.markdown("### ⚠️ Review")

        missing = result["missing_information"]

        if missing:

            st.warning(
                "Missing information detected."
            )

            for item in missing:

                st.write(f"• {item}")

        else:

            st.success(
                "No missing information detected."
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # Follow-up
    # --------------------------------------------------------

    with col3:

        st.markdown(
            '<div class="result-card">',
            unsafe_allow_html=True,
        )

        st.markdown("### 📌 Follow-up")

        task = result["follow_up_task"]

        if task:

            st.info(task)

            st.caption(
                "Requires clinician approval."
            )

        else:

            st.write(
                "No follow-up task detected."
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


    # ========================================================
    # Documentation review
    # ========================================================

    st.divider()

    st.subheader("📝 Review Documentation")

    st.caption(
        "AI-generated draft. Review and edit before approval."
    )

    edited_documentation = st.text_area(
        "Documentation",
        value=result["documentation"],
        height=180,
        key="documentation_editor",
        label_visibility="collapsed",
    )


 # ========================================================
# Approval actions
# ========================================================

st.write("### Human Approval")

col1, col2 = st.columns(2)


with col1:

    approve_clicked = st.button(
        "✓ Approve & Save",
        type="primary",
        use_container_width=True,
    )


with col2:

    reset_clicked = st.button(
        "↻ Reset Review",
        use_container_width=True,
    )


# --------------------------------------------------------
# Reset
# --------------------------------------------------------

if reset_clicked:

    st.session_state.analysis_result = None
    st.session_state.approved = False

    if "documentation_editor" in st.session_state:
        del st.session_state.documentation_editor

    st.rerun()


# --------------------------------------------------------
# Approve & Save
# --------------------------------------------------------

if approve_clicked:

    from database.db import (
        create_encounter,
        save_documentation,
        save_followup_task,
    )

    try:

        # Extract the actual patient ID
        selected_patient_id = patient_id.split(" — ")[0]

        # Create encounter
        encounter_id = create_encounter(
            patient_id=selected_patient_id,
            visit_type=visit_type,
            raw_note=note,
        )

        # Save clinician-approved documentation
        save_documentation(
            encounter_id=encounter_id,
            documentation=edited_documentation,
            approved_by="Dr. Sarah Smith",
        )

        # Save follow-up task if one exists
        save_followup_task(
            encounter_id=encounter_id,
            task=result["follow_up_task"],
        )

        st.session_state.approved = True

        st.success(
            "✓ Documentation approved and saved."
        )

        st.info(
            f"Encounter ID: {encounter_id}"
        )

    except Exception as e:

        st.error(
            f"Failed to save documentation: {e}"
        )


        
    # ========================================================
    # Agent trace
    # ========================================================

    st.divider()

    with st.expander("🔍 View Agent Execution"):

        st.write("✓ Documentation Agent")
        st.write("✓ Validation Agent")
        st.write("✓ Follow-up Agent")

        st.caption(
            "The AI proposes documentation. "
            "Validation checks the output. "
            "The clinician makes the final decision."
        )