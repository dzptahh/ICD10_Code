from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class AttemptRecord:
    ts_utc: str
    event: str
    case_code: str
    case_category: str
    entered_code: str
    correct: int
    response_time_s: int
    keystrokes: int
    code_length: int
    keystroke_efficiency: float
    time_remaining_s: int
    time_limit_s: int
    stability: int
    score: int


@dataclass
class CategoryStats:
    attempts: int = 0
    correct: int = 0
    total_time_spent_s: int = 0

    @property
    def accuracy(self) -> float:
        return 0.0 if self.attempts == 0 else self.correct / self.attempts


class StatsTracker:
    def __init__(self, *, global_csv_path: str | Path | None = None) -> None:
        self.data_records: list[AttemptRecord] = []
        self.category_stats: dict[str, CategoryStats] = {}
        self._case_started_at: datetime | None = None
        self._global_csv_path: Path | None = Path(global_csv_path) if global_csv_path else None

    def start_case_timer(self) -> None:
        self._case_started_at = datetime.now(timezone.utc)

    def response_time_s(self) -> int:
        if not self._case_started_at:
            return 0
        delta = datetime.now(timezone.utc) - self._case_started_at
        return max(0, int(delta.total_seconds()))

    def end_case_timer(self, category: str) -> None:
        if not self._case_started_at:
            return
        delta = datetime.now(timezone.utc) - self._case_started_at
        spent = max(0, int(delta.total_seconds()))
        self._case_started_at = None
        self._ensure_cat(category).total_time_spent_s += spent

    def _ensure_cat(self, category: str) -> CategoryStats:
        if category not in self.category_stats:
            self.category_stats[category] = CategoryStats()
        return self.category_stats[category]

    @staticmethod
    def _keystroke_efficiency(keystrokes: int, code_length: int) -> float:
        if code_length <= 0:
            return 0.0
        # 1.0 means exactly typed length, >1.0 means extra typing (less efficient)
        return keystrokes / code_length

    def _append_global_csv_row(self, rec: AttemptRecord) -> None:
        if not self._global_csv_path:
            return
        path = self._global_csv_path
        path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not path.exists()

        with path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(
                    [
                        "timestamp",
                        "response_time",
                        "keystrokes",
                        "accuracy",
                        "category",
                        "remaining_time",
                        "time_limit",
                        "code",
                        "entered_code",
                        "keystroke_efficiency",
                        "score",
                        "stability",
                    ]
                )
            writer.writerow(
                [
                    rec.ts_utc,
                    rec.response_time_s,
                    rec.keystrokes,
                    rec.correct,
                    rec.case_category,
                    rec.time_remaining_s,
                    rec.time_limit_s,
                    rec.case_code,
                    rec.entered_code,
                    f"{rec.keystroke_efficiency:.3f}",
                    rec.score,
                    rec.stability,
                ]
            )

    def log_attempt(
        self,
        *,
        event: str,
        case_code: str,
        case_category: str,
        entered_code: str,
        correct: bool,
        response_time_s: int = 0,
        keystrokes: int = 0,
        code_length: int = 0,
        time_remaining_s: int,
        time_limit_s: int = 0,
        stability: int,
        score: int,
    ) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        eff = self._keystroke_efficiency(keystrokes, code_length)
        rec = AttemptRecord(
            ts_utc=ts,
            event=event,
            case_code=case_code,
            case_category=case_category,
            entered_code=entered_code,
            correct=1 if correct else 0,
            response_time_s=int(response_time_s),
            keystrokes=int(keystrokes),
            code_length=int(code_length),
            keystroke_efficiency=float(eff),
            time_remaining_s=int(time_remaining_s),
            time_limit_s=int(time_limit_s),
            stability=int(stability),
            score=int(score),
        )
        self.data_records.append(rec)

        cat = self._ensure_cat(case_category)
        if event == "submit":
            cat.attempts += 1
            cat.correct += 1 if correct else 0
            self._append_global_csv_row(rec)

    def save_to_csv(self, file_path: str | Path) -> Path:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "ts_utc",
                    "event",
                    "case_code",
                    "case_category",
                    "entered_code",
                    "correct",
                    "response_time_s",
                    "keystrokes",
                    "code_length",
                    "keystroke_efficiency",
                    "time_remaining_s",
                    "time_limit_s",
                    "stability",
                    "score",
                ]
            )
            for r in self.data_records:
                writer.writerow(
                    [
                        r.ts_utc,
                        r.event,
                        r.case_code,
                        r.case_category,
                        r.entered_code,
                        r.correct,
                        r.response_time_s,
                        r.keystrokes,
                        r.code_length,
                        f"{r.keystroke_efficiency:.3f}",
                        r.time_remaining_s,
                        r.time_limit_s,
                        r.stability,
                        r.score,
                    ]
                )
        return path

    def summary_rows(self) -> list[tuple[str, int, int, float, int]]:
        rows: list[tuple[str, int, int, float, int]] = []
        for cat, st in sorted(self.category_stats.items(), key=lambda x: x[0].lower()):
            rows.append((cat, st.attempts, st.correct, st.accuracy, st.total_time_spent_s))
        return rows

    def submit_records(self) -> list[AttemptRecord]:
        return [r for r in self.data_records if r.event == "submit"]

    def response_time_series(self) -> list[int]:
        return [r.response_time_s for r in self.submit_records()]

    def accuracy_series(self) -> list[int]:
        return [r.correct for r in self.submit_records()]

    def category_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self.submit_records():
            counts[r.case_category] = counts.get(r.case_category, 0) + 1
        return counts

    def stress_factor_correlation(self) -> float | None:
        """
        Pearson correlation between remaining_time and error (1=wrong, 0=correct).
        Returns None if not enough variance/data.
        """
        recs = self.submit_records()
        if len(recs) < 2:
            return None
        xs = [float(r.time_remaining_s) for r in recs]
        ys = [float(1 - r.correct) for r in recs]

        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        denx = sum((x - mx) ** 2 for x in xs)
        deny = sum((y - my) ** 2 for y in ys)
        if denx <= 0 or deny <= 0:
            return None
        return num / math.sqrt(denx * deny)

    @staticmethod
    def mean_std(values: list[int]) -> tuple[float | None, float | None]:
        if not values:
            return None, None
        m = sum(values) / len(values)
        if len(values) < 2:
            return m, 0.0
        var = sum((v - m) ** 2 for v in values) / (len(values) - 1)
        return m, math.sqrt(var)

