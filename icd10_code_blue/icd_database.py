from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ICDEntry:
    code: str
    description: str
    category: str


class ICD_Database:
    def __init__(self) -> None:
        self.entries: list[ICDEntry] = []
        self._by_code: dict[str, ICDEntry] = {}

    @staticmethod
    def _levenshtein(a: str, b: str) -> int:
        if a == b:
            return 0
        if not a:
            return len(b)
        if not b:
            return len(a)
        # O(len(a)*len(b)) DP; fine for classroom-size datasets.
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, start=1):
            cur = [i]
            for j, cb in enumerate(b, start=1):
                ins = cur[j - 1] + 1
                delete = prev[j] + 1
                sub = prev[j - 1] + (0 if ca == cb else 1)
                cur.append(min(ins, delete, sub))
            prev = cur
        return prev[-1]

    @classmethod
    def _similarity(cls, needle: str, hay: str) -> float:
        n = needle.strip().lower()
        h = hay.strip().lower()
        if not n or not h:
            return 0.0
        if n in h:
            # reward substring hits strongly
            return 1.0
        dist = cls._levenshtein(n, h)
        denom = max(len(n), len(h))
        return 0.0 if denom == 0 else max(0.0, 1.0 - dist / denom)

    @staticmethod
    def _norm(s: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

    @classmethod
    def _tokens(cls, s: str) -> list[str]:
        n = cls._norm(s)
        return [t for t in n.split() if t]

    def load_data(self, file_path: str | Path) -> None:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ICD-10 CSV not found: {path}")

        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required = {"code", "description", "category"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                raise ValueError(
                    "CSV must have headers: code, description, category "
                    f"(got: {reader.fieldnames})"
                )

            entries: list[ICDEntry] = []
            for row in reader:
                code = (row.get("code") or "").strip()
                desc = (row.get("description") or "").strip()
                cat = (row.get("category") or "").strip()
                if not code or not desc:
                    continue
                if not cat:
                    cat = "Uncategorized"
                entries.append(ICDEntry(code=code, description=desc, category=cat))

        self.entries = entries
        self._by_code = {e.code.upper(): e for e in entries}

    def get_by_code(self, code: str) -> ICDEntry | None:
        return self._by_code.get(code.strip().upper())

    def search_code(self, keyword: str, *, limit: int = 50) -> list[ICDEntry]:
        kw = keyword.strip().lower()
        if not kw:
            return []

        q_norm = self._norm(kw)
        q_tokens = self._tokens(kw)
        q_compact = re.sub(r"[^a-z0-9]+", "", kw)

        scored: list[tuple[float, ICDEntry]] = []
        for e in self.entries:
            code = e.code
            code_l = code.lower()
            code_compact = re.sub(r"[^a-z0-9]+", "", code_l)
            desc_l = e.description.lower()
            cat_l = e.category.lower()
            combined = f"{e.description} {e.category}"
            combined_norm = self._norm(combined)
            combined_tokens = self._tokens(combined)

            # Strong ranking signals first.
            score = 0.0
            if q_compact and code_compact == q_compact:
                score += 7.0  # exact code hit should always float to top
            elif q_compact and code_compact.startswith(q_compact):
                score += 4.8
            elif kw and code_l.startswith(kw):
                score += 4.2

            if q_norm and q_norm in desc_l:
                score += 2.6
            if q_norm and q_norm in cat_l:
                score += 1.8

            # Token coverage helps multi-word queries rank better.
            if q_tokens:
                covered = sum(1 for t in q_tokens if t in combined_tokens)
                prefix_covered = sum(1 for t in q_tokens if any(tok.startswith(t) for tok in combined_tokens))
                score += 1.8 * (covered / len(q_tokens))
                score += 0.9 * (prefix_covered / len(q_tokens))

            # Fuzzy fallback so typos still return useful results.
            s_code = self._similarity(kw, code)
            s_desc = self._similarity(kw, e.description)
            s_cat = self._similarity(kw, e.category)
            s_comb = self._similarity(q_norm or kw, combined_norm)
            score += (s_code * 1.2) + (s_desc * 0.9) + (s_cat * 0.5) + (s_comb * 0.8)

            if score <= 0.65:
                continue
            scored.append((score, e))

        scored.sort(
            key=lambda t: (
                -t[0],
                t[1].code.lower(),
                t[1].category.lower(),
                t[1].description.lower(),
            )
        )
        return [e for _s, e in scored[:limit]]

    def filter_by_category(self, category: str) -> list[ICDEntry]:
        cat = category.strip().lower()
        if not cat:
            return []
        return [e for e in self.entries if e.category.lower() == cat]

    def categories(self) -> list[str]:
        cats = sorted({e.category for e in self.entries})
        return cats

    def iter_entries(self) -> Iterable[ICDEntry]:
        return iter(self.entries)

