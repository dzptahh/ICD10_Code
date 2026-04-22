from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Patient:
    symptoms_text: str
    correct_code: str
    category: str


_SYMPTOM_TEMPLATES: dict[str, list[str]] = {
    "Cardiology": [
        "Sharp chest pain radiating to the left arm, sweating, nausea.",
        "Crushing substernal chest pressure with shortness of breath.",
        "Palpitations, lightheadedness, irregular pulse on exam.",
    ],
    "Respiratory": [
        "Wheezing, chest tightness, coughing, worse at night.",
        "Fever, productive cough with shortness of breath and crackles.",
        "Sudden pleuritic chest pain with shortness of breath.",
    ],
    "Infectious": [
        "High fever, chills, hypotension and confusion (possible sepsis).",
        "Sore throat, fever, tender cervical lymph nodes.",
        "Dysuria, urinary frequency, suprapubic pain.",
    ],
    "Gastroenterology": [
        "Epigastric burning pain after meals, improved with antacids.",
        "Right upper quadrant pain after fatty meals, nausea.",
        "Watery diarrhea, abdominal cramps, mild fever.",
    ],
    "Neurology": [
        "Sudden unilateral weakness, facial droop, slurred speech.",
        "Severe headache 'worst of life' with neck stiffness.",
        "Tremor at rest, slow movement, rigidity.",
    ],
    "Endocrinology": [
        "Polyuria, polydipsia, weight loss, high glucose.",
        "Fatigue, cold intolerance, weight gain, dry skin.",
        "Heat intolerance, anxiety, weight loss, tremor.",
    ],
    "General": [
        "Fever and malaise with nonspecific symptoms; needs evaluation.",
        "Pain and discomfort with gradual onset; further history needed.",
        "Acute onset symptoms under stress; vitals trending worse.",
    ],
}


def template_symptoms_for_category(category: str) -> list[str]:
    return _SYMPTOM_TEMPLATES.get(category) or _SYMPTOM_TEMPLATES["General"]

