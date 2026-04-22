from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PatientCase:
    symptoms: str
    correct_code: str
    description: str = ""


def load_cases_csv(path: str | Path) -> list[PatientCase]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Cases CSV not found: {p}")

    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        legacy_required = {"symptoms", "correct_code"}
        unified_required = {"code", "description", "symptoms"}
        has_legacy = legacy_required.issubset(fields)
        has_unified = unified_required.issubset(fields)
        if not reader.fieldnames or (not has_legacy and not has_unified):
            raise ValueError(
                "Cases CSV must have either headers: symptoms, correct_code "
                "or unified headers: code, description, symptoms "
                f"(got: {reader.fieldnames})"
            )
        cases: list[PatientCase] = []
        for row in reader:
            sym = (row.get("symptoms") or "").strip()
            desc = (row.get("description") or "").strip()
            code = ((row.get("correct_code") if has_legacy else row.get("code")) or "").strip().upper()
            if not sym or not code:
                continue
            cases.append(PatientCase(symptoms=sym, correct_code=code, description=desc))
    if not cases:
        raise ValueError("Cases CSV loaded 0 valid rows.")
    return cases

