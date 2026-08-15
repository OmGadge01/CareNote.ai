from pydantic import BaseModel, Field
from typing import List, Optional


class Symptom(BaseModel):
    name: str
    duration: Optional[str] = None


class VitalSigns(BaseModel):
    blood_pressure: Optional[str] = None
    temperature: Optional[str] = None
    heart_rate: Optional[str] = None


class ClinicalData(BaseModel):
    visit_type: Optional[str] = None

    conditions: List[str] = Field(default_factory=list)

    symptoms: List[Symptom] = Field(default_factory=list)

    vitals: VitalSigns = Field(default_factory=VitalSigns)

    medications: List[str] = Field(default_factory=list)

    follow_up: Optional[str] = None