from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PatientCase:
    symptoms: str
    correct_code: str


def load_cases_csv(path: str | Path) -> list[PatientCase]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Cases CSV not found: {p}")

    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"symptoms", "correct_code"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError(
                "Cases CSV must have headers: symptoms, correct_code "
                f"(got: {reader.fieldnames})"
            )
        cases: list[PatientCase] = []
        for row in reader:
            sym = (row.get("symptoms") or "").strip()
            code = (row.get("correct_code") or "").strip().upper()
            if not sym or not code:
                continue
            cases.append(PatientCase(symptoms=sym, correct_code=code))
    if not cases:
        raise ValueError("Cases CSV loaded 0 valid rows.")
    return cases

