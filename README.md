# CareNote AI

## Agentic Clinical Documentation Assistant

**Project Type:** Healthcare AI Prototype
**Primary Focus:** Agentic AI, Human-in-the-Loop, Clinical Documentation
**AI Model:** Qwen3 4B via Ollama
**Frontend:** Streamlit
**Workflow:** LangGraph
**Database:** SQLite

---

# 1. Problem Statement

Healthcare professionals spend significant time converting unstructured clinical notes into structured documentation.

A typical clinician may write notes such as:

> Patient came for hypertension follow-up. BP today is 148/92. Patient reports occasional headache for three days. Currently taking amlodipine 5 mg daily. No fever or chest pain. Follow-up in two weeks.

This information contains several clinically relevant elements:

* Visit purpose
* Medical conditions
* Symptoms
* Vital signs
* Medications
* Follow-up instructions

However, the information is stored as free-form text.

Manually converting these notes into structured documentation is:

* Time-consuming
* Repetitive
* Prone to omission
* Difficult to standardize
* Not ideal for creating follow-up tasks

At the same time, using a fully autonomous AI system in healthcare introduces significant risks.

An AI system should not blindly generate or modify clinical records without human oversight.

Therefore, the project addresses two problems:

### Problem 1 — Documentation burden

How can AI help transform unstructured clinical notes into useful structured information and documentation?

### Problem 2 — Healthcare AI safety

How can AI assist clinicians while ensuring that the clinician remains responsible for reviewing and approving the final documentation?

---

# 2. Proposed Solution

**CareNote AI** is an agentic clinical documentation assistant that converts unstructured clinical notes into structured clinical information, validates the extracted information, generates documentation, identifies follow-up tasks, and requires human approval before saving the final record.

The core principle is:

> **AI proposes → System validates → Human reviews → Human approves → System saves**

CareNote AI is designed as an **assistive system**, not an autonomous medical decision-making system.

The prototype uses a local LLM through Ollama, which allows the project to run without sending clinical data to an external AI API.

---

# 3. Example Use Case

### Input

A clinician enters:

```text
Patient came for hypertension follow-up.
BP today is 148/92.
Patient reports occasional headache for three days.
Currently taking amlodipine 5 mg daily.
No fever or chest pain.
Follow-up in two weeks.
```

### AI Processing

The system attempts to extract:

```text
Visit Type:
Follow-up

Condition:
Hypertension

Symptoms:
Headache — three days

Blood Pressure:
148/92

Medication:
Amlodipine 5 mg daily

Follow-up:
In two weeks
```

### Validation

The system checks whether important information is missing.

### Documentation

A draft clinical documentation record is generated.

### Human Review

The clinician can:

* Review the generated documentation
* Edit it
* Approve it
* Request changes

### Persistence

After approval, the encounter and documentation are stored in SQLite.

---

# 4. Key Design Principle

```text
User
 ↓
AI Extraction
 ↓
Validation
 ↓
Documentation
 ↓
Human Review
 ↓
Approval
 ↓
Database
```

This provides a human-in-the-loop safety boundary.

The AI never gets the final authority to save clinical documentation.

---

# 5. Technology Stack

## Frontend

### Streamlit

Used for:

* Clinical note input
* Patient selection
* Visit type selection
* Analysis results
* Validation warnings
* Documentation review
* Human approval
* Agent execution visibility

Why Streamlit?

* Extremely fast to develop
* Python-native
* Minimal frontend code
* Ideal for prototypes
* Easy to demonstrate during interviews

---

# AI / Agent Layer

## Ollama

Ollama runs the local language model.

Current model:

```text
qwen3:4b
```

Benefits:

* Local inference
* No external API dependency
* Suitable for prototyping
* Keeps demonstration data local

---

## LangChain

LangChain provides the LLM integration layer.

Current use:

```text
LangChain
    ↓
ChatOllama
    ↓
Qwen3 4B
```

It is responsible for connecting the application logic to the local LLM.

---

## LangGraph

LangGraph manages the agent workflow.

Instead of a single large LLM call, the system is structured as a sequence of processing nodes.

Current conceptual workflow:

```text
Extraction
    ↓
Validation
    ↓
Documentation
    ↓
Follow-up
```

This allows each step to have a specific responsibility.

---

# Data Validation

## Pydantic

Pydantic defines the expected clinical data structure.

Example:

```python
ClinicalData
├── visit_type
├── conditions
├── symptoms
├── vitals
├── medications
└── follow_up
```

This prevents the application from depending entirely on free-form LLM output.

---

# Database

## SQLite

SQLite is used for the prototype because it requires:

* No database server
* No configuration
* No external service
* Very little code

The current database contains:

```text
patients
encounters
clinical_documents
followup_tasks
```

---

# Supporting Technologies

```text
Python
Streamlit
LangChain
LangGraph
Ollama
Qwen3 4B
Pydantic
SQLite
python-dotenv
Loguru
```

---

# 6. High-Level Architecture

```text
┌─────────────────────────────────────────────┐
│                  CARENOTE AI                │
└─────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                 Streamlit UI                │
│                                             │
│ • Patient Selection                         │
│ • Clinical Note Input                       │
│ • Analysis Results                          │
│ • Review / Edit                             │
│ • Approval                                  │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              LangGraph Workflow             │
│                                             │
│   ┌──────────────┐                          │
│   │  Extraction  │                          │
│   └──────┬───────┘                          │
│          ▼                                  │
│   ┌──────────────┐                          │
│   │  Validation  │                          │
│   └──────┬───────┘                          │
│          ▼                                  │
│   ┌──────────────┐                          │
│   │Documentation │                          │
│   └──────┬───────┘                          │
│          ▼                                  │
│   ┌──────────────┐                          │
│   │  Follow-up   │                          │
│   └──────────────┘                          │
└──────────────────────┬──────────────────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
      ┌─────────────┐     ┌──────────────┐
      │ Qwen3 4B    │     │ Python Logic │
      │ Ollama      │     │ + Pydantic   │
      └─────────────┘     └──────────────┘
                       │
                       ▼
                Human Review
                       │
                 ┌─────┴─────┐
                 │           │
              Reject       Approve
                 │           │
                 │           ▼
                 │      ┌──────────┐
                 │      │ SQLite   │
                 │      └──────────┘
                 │
                 ▼
              Revision
```

---

# 7. System Flow

## Step 1 — Clinician enters note

The clinician enters an unstructured clinical note through Streamlit.

Example:

```text
Patient came for hypertension follow-up.
BP today is 148/92.
Patient reports occasional headache for three days.
Currently taking amlodipine 5 mg daily.
Follow-up in two weeks.
```

---

## Step 2 — Extraction Agent

The extraction component processes the note.

The LLM is used for language understanding and extraction of semantic information such as:

* Conditions
* Symptoms
* Medications
* Visit purpose
* Follow-up information

Highly structured information such as blood pressure can also be handled using deterministic Python extraction.

This hybrid approach is intentional.

Instead of:

```text
LLM → Everything
```

the architecture uses:

```text
LLM → Language understanding
Python → Deterministic patterns
```

This improves reliability and reduces unnecessary LLM work.

---

# 8. Structured Clinical Data

The extracted information follows a Pydantic schema.

Conceptually:

```json
{
  "visit_type": "Follow-up",
  "conditions": [
    "hypertension"
  ],
  "symptoms": [
    {
      "name": "headache",
      "duration": "three days"
    }
  ],
  "vitals": {
    "blood_pressure": "148/92",
    "temperature": null,
    "heart_rate": null
  },
  "medications": [
    "amlodipine 5 mg daily"
  ],
  "follow_up": "in two weeks"
}
```

This structured representation becomes the internal state passed through the workflow.

---

# 9. Validation Agent

The validation stage checks the extracted information.

For example:

```text
Required information
        │
        ├── Condition
        ├── Symptoms
        ├── Blood pressure
        └── Visit type
```

If information is missing:

```text
⚠️ Missing Information

• Blood pressure
• Visit type
```

The system does not silently assume that missing information is absent from the patient.

This distinction is important:

```text
Not mentioned
      ≠
Not extracted
```

A production implementation would maintain stronger provenance information for each extracted field.

---

# 10. Documentation Generation

After extraction and validation, the system generates a human-readable documentation draft.

Example:

```text
Patient attended a follow-up visit for hypertension.

Condition:
Hypertension

Symptoms:
Headache for three days

Blood Pressure:
148/92

Medication:
Amlodipine 5 mg daily

Follow-up:
In two weeks
```

The documentation is treated as a **draft**, not a final medical record.

---

# 11. Human-in-the-Loop Review

This is one of the most important parts of CareNote AI.

The generated documentation is displayed in an editable field.

The clinician can:

```text
AI Draft
   ↓
Review
   ↓
Edit
   ↓
Approve
```

Only after approval does the system save the documentation.

This prevents the AI from becoming the final decision-maker.

---

# 12. Approval and Persistence

When the clinician selects:

```text
✓ Approve & Save
```

the application creates an encounter.

The system stores:

### Encounter

```text
patient_id
visit_type
raw_note
created_at
```

### Clinical Document

```text
encounter_id
documentation
approved
approved_by
approved_at
```

### Follow-up Task

```text
encounter_id
task
status
created_at
```

This provides a basic audit trail.

---

# 13. Database Architecture

```text
                 SQLite
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
   patients     encounters   documents
                    │
                    │
                    ▼
              followup_tasks
```

Relationships:

```text
Patient
   │
   └──→ Encounter
           │
           ├──→ Clinical Document
           │
           └──→ Follow-up Task
```

---

# 14. Current Database Schema

## patients

```text
id
name
age
condition
```

Example:

```text
P001 | Alex Morgan | 45 | Hypertension
```

---

## encounters

```text
id
patient_id
visit_type
raw_note
created_at
```

---

## clinical_documents

```text
id
encounter_id
documentation
approved
approved_by
approved_at
```

---

## followup_tasks

```text
id
encounter_id
task
status
created_at
```

---

# 15. Agentic Architecture

CareNote AI uses an agentic workflow rather than a single prompt.

Current workflow:

```text
                 START
                   │
                   ▼
          ┌─────────────────┐
          │ Extraction Node │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Validation Node │
          └────────┬────────┘
                   │
                   ▼
         ┌───────────────────┐
         │ Documentation Node│
         └─────────┬─────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Follow-up Node  │
          └────────┬────────┘
                   │
                   ▼
                  END
```

Each node has a focused responsibility.

This makes the system:

* Easier to debug
* Easier to extend
* Easier to test
* Easier to explain
* Safer than one unrestricted LLM call

---

# 16. Why LangGraph?

A normal LLM application might look like:

```text
Prompt
  ↓
LLM
  ↓
Answer
```

CareNote AI requires state to move through multiple processing stages.

LangGraph allows the application to maintain a shared state:

```text
CareNoteState
│
├── clinical_note
├── clinical_data
├── validation_issues
├── missing_information
├── documentation
├── follow_up_task
└── safety_flags
```

Each node reads the state and returns updates.

This creates a controllable workflow instead of an unrestricted autonomous agent.

---

# 17. Why Use a Hybrid AI Architecture?

Not every problem needs an LLM.

For example:

### Blood pressure

```text
BP today is 148/92
```

A regular expression can extract:

```text
148/92
```

There is no reason to spend LLM tokens on this.

### Clinical meaning

However:

```text
Patient reports occasional headache for three days.
```

requires language understanding.

Therefore:

```text
Structured pattern
        ↓
Python

Semantic interpretation
        ↓
LLM
```

This makes the system faster, cheaper, and more deterministic.

---

# 18. Healthcare Safety Philosophy

CareNote AI is designed as a documentation assistant.

It should **not**:

* Diagnose patients
* Recommend medication changes
* Prescribe medication
* Replace a clinician
* Automatically approve medical documentation
* Make autonomous clinical decisions

Instead:

```text
AI
 ↓
Assist
 ↓
Validate
 ↓
Flag uncertainty
 ↓
Human Review
 ↓
Human Decision
```

This is the core safety philosophy of the prototype.

---

# 19. Planned Safety Agent

The next major component is a dedicated Safety Agent.

Example input:

```text
Patient asks whether they should double their
amlodipine dose.
```

Instead of generating a medical recommendation, the system should produce:

```text
⚠️ SAFETY REVIEW REQUIRED

Potential medication-change request detected.

CareNote AI does not provide medication
adjustment recommendations.

Clinician review required.
```

Conceptually:

```text
Clinical Note
     │
     ▼
Extraction
     │
     ▼
Validation
     │
     ▼
Safety Agent
     │
     ├───────────────┐
     │               │
     ▼               ▼
   Safe         Requires Review
     │               │
     ▼               ▼
Documentation    Human Review
```

---

# 20. Planned Dashboard

A dashboard will provide an overview of the stored documentation.

Example:

```text
┌──────────────────────────────────────────┐
│              CareNote Dashboard           │
├────────────┬────────────┬────────────────┤
│ 12         │ 8          │ 4              │
│ Documents  │ Approved   │ Follow-ups     │
├────────────┴────────────┴────────────────┤
│                                          │
│ Recent Documentation                     │
│                                          │
│ P001  Alex Morgan      Approved           │
│ P002  Sarah Williams   Pending            │
│ P003  David Brown      Approved           │
│                                          │
└──────────────────────────────────────────┘
```

The dashboard will query SQLite rather than maintain separate state.

---



# 22. Project Structure

Current project structure:

```text
carenote-ai/
│
├── app.py
│
├── agents/
│   ├── __init__.py
│   ├── extraction.py
│   ├── state.py
│   └── workflow.py
│
├── models/
│   ├── __init__.py
│   └── schemas.py
│
├── database/
│   ├── __init__.py
│   ├── db.py
│   └── seed.py
│
├── prompts/
│
├── data/
│
├── carenote.db
│
└── README.md
```

---

# 23. System Flow — Complete

```text
                  ┌──────────────┐
                  │  Clinician   │
                  └──────┬───────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Streamlit UI    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Clinical Note   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Extraction Agent│
                │                 │
                │ Qwen3 + Rules   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Structured Data │
                │   Pydantic      │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Validation      │
                │ Agent           │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Safety Agent    │
                │   [Planned]     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Documentation   │
                │ Generation      │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Human Review    │
                └────────┬────────┘
                         │
                  ┌──────┴──────┐
                  │             │
                  ▼             ▼
                Edit          Approve
                                │
                                ▼
                         ┌────────────┐
                         │   SQLite   │
                         └────────────┘
```


```text
Frontend       → React / Angular
Backend        → Spring Boot / FastAPI
Authentication → OAuth2 / JWT
Database       → PostgreSQL
Vector DB      → Qdrant
AI             → Managed LLM / private model
Deployment     → Docker
Cloud          → Oracle Cloud / AWS / Azure
Monitoring     → OpenTelemetry / Grafana
```

These are **future architecture choices**, not requirements for the current prototype.

---



# 28. Important Design Decisions

## Why Streamlit?

Fast prototyping and minimal frontend complexity.

## Why Ollama?

Allows local LLM inference without requiring an external AI API.

## Why Qwen3 4B?

Small enough for local experimentation while still capable of structured language tasks.

## Why LangGraph?

The problem naturally consists of multiple stateful processing stages.

## Why Pydantic?

Provides a strict schema between probabilistic LLM output and deterministic application code.

## Why SQLite?

The prototype does not require a database server.

## Why Human-in-the-Loop?

Clinical documentation should not be autonomously finalized by an AI system.

## Why hybrid extraction?

Deterministic patterns are faster and more reliable for highly structured information, while LLMs are better suited for semantic interpretation.

---

# 29. Core Project Philosophy

CareNote AI follows three principles:

### 1. AI assists, not replaces

```text
AI → Recommendation / Draft
Human → Final Decision
```

### 2. Deterministic where possible

```text
Rules → structured facts
LLM → language understanding
```

### 3. Safety before autonomy

```text
Uncertain
   ↓
Flag
   ↓
Human Review
```

The goal is not to make the most autonomous AI system possible.

The goal is to build an AI system that is **useful, explainable, controllable, and safe enough for a healthcare workflow prototype.**

---

# 30. Final MVP Goal

The finished interview prototype should demonstrate:

```text
                  CARENOTE AI
                      │
       ┌──────────────┴──────────────┐
       │                             │
       ▼                             ▼
 New Documentation              Dashboard
       │
       ▼
 Unstructured Clinical Note
       │
       ▼
 🧠 Extraction
       │
       ▼
 🔎 Validation
       │
       ▼
 🛡️ Safety Check
       │
       ▼
 📝 Documentation Draft
       │
       ▼
 👨‍⚕️ Human Review
       │
       ▼
 ✓ Approve
       │
       ▼
 💾 SQLite
       │
       ▼
 📌 Follow-up
```

This is intentionally small enough to build quickly, while demonstrating meaningful **agentic AI + software engineering + healthcare safety** concepts.
