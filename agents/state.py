from typing import Optional
from typing_extensions import TypedDict
from models.schemas import ClinicalData

class CareNoteState(TypedDict):
    clinical_note: str

    clinical_data: Optional[ClinicalData]

    validation_issues: list[str]

    missing_information: list[str]

    documentation: Optional[str]

    follow_up_task: Optional[str]

    safety_flags: list[str]
