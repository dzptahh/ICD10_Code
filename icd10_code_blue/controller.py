from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

from .icd_database import ICD_Database, ICDEntry
from .cases import PatientCase
from .patient import Patient, template_symptoms_for_category
from .stats import StatsTracker


class GameState(str, Enum):
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"


@dataclass
class GameConfig:
    base_seconds_per_case: int = 30
    min_seconds_per_case: int = 12
    difficulty_step_points: int = 300  # each N score reduces time limit
    difficulty_step_seconds: int = 2
    wrong_streak_soften_at: int = 3
    wrong_streak_bonus_seconds: int = 2
    max_stability: int = 100
    stability_decay_per_second: int = 2
    stability_penalty_wrong: int = 20
    stability_penalty_skip: int = 10
    points_correct: int = 100
    points_wrong: int = -25
    bonus_fast_threshold_s: int = 15
    bonus_fast_points: int = 25


class GameController:
    def __init__(self, db: ICD_Database, stats: StatsTracker, config: GameConfig | None = None) -> None:
        self.db = db
        self.stats = stats
        self.config = config or GameConfig()

        self.game_state: GameState = GameState.MENU
        self.score: int = 0
        self.time_limit_s: int = self.config.base_seconds_per_case
        self.time_remaining: int = self.time_limit_s
        self.stability: int = self.config.max_stability
        self.case_index: int = 0
        self.current_patient: Patient | None = None
        self._active_entry: ICDEntry | None = None  # the correct ICD entry for current case (if known)
        self._deck: list[ICDEntry] = []  # ICD deck (fallback)
        self._deck_pos: int = 0
        self._wrong_streak: int = 0
        self._cases: list[PatientCase] = []
        self._case_deck: list[PatientCase] = []
        self._case_deck_pos: int = 0
        self._active_correct_code: str = ""
        self._active_category: str = ""
        self.last_game_over_reason: str = ""
        self.last_case_answer: str = ""
        self._case_clock_started: bool = False

    def load_cases(self, cases: list[PatientCase]) -> None:
        self._cases = list(cases)
        self._reset_case_deck()

    def clear_cases(self) -> None:
        self._cases = []
        self._case_deck = []
        self._case_deck_pos = 0

    def start_game(self) -> None:
        self.game_state = GameState.PLAYING
        self.score = 0
        self.case_index = 0
        self.stability = self.config.max_stability
        self._wrong_streak = 0
        self._reset_deck()
        self._reset_case_deck()
        self.last_game_over_reason = ""
        self.last_case_answer = ""
        self._next_case()

    def _reset_deck(self) -> None:
        self._deck = list(self.db.entries)
        random.shuffle(self._deck)
        self._deck_pos = 0

    def _pick_next_entry(self) -> ICDEntry:
        if not self._deck:
            self._reset_deck()
        if self._deck_pos >= len(self._deck):
            self._reset_deck()
        entry = self._deck[self._deck_pos]
        self._deck_pos += 1
        return entry

    def _reset_case_deck(self) -> None:
        self._case_deck = list(self._cases)
        random.shuffle(self._case_deck)
        self._case_deck_pos = 0

    def _pick_next_case(self) -> PatientCase | None:
        if not self._cases:
            return None
        if not self._case_deck:
            self._reset_case_deck()
        if self._case_deck_pos >= len(self._case_deck):
            self._reset_case_deck()
        c = self._case_deck[self._case_deck_pos]
        self._case_deck_pos += 1
        return c

    def _compute_time_limit(self) -> int:
        steps = 0 if self.config.difficulty_step_points <= 0 else self.score // self.config.difficulty_step_points
        reduced = self.config.base_seconds_per_case - int(steps) * self.config.difficulty_step_seconds
        softened = reduced
        if self._wrong_streak >= self.config.wrong_streak_soften_at:
            softened += self.config.wrong_streak_bonus_seconds
        return max(self.config.min_seconds_per_case, softened)

    def _next_case(self) -> None:
        if not self.db.entries:
            raise RuntimeError("ICD database is empty. Load data first.")

        self.case_index += 1
        self.time_limit_s = self._compute_time_limit()
        self.time_remaining = self.time_limit_s
        self._case_clock_started = False
        case = self._pick_next_case()
        if case is not None:
            self._active_correct_code = case.correct_code.strip().upper()
            self._active_entry = self.db.get_by_code(self._active_correct_code)
            self._active_category = self._active_entry.category if self._active_entry else "Uncategorized"
            self.current_patient = Patient(
                symptoms_text=case.symptoms,
                correct_code=self._active_correct_code,
                category=self._active_category,
            )
        else:
            # fallback: random ICD entry + templated symptoms
            self._active_entry = self._pick_next_entry()
            self._active_correct_code = self._active_entry.code.upper()
            self._active_category = self._active_entry.category
            symptoms = random.choice(template_symptoms_for_category(self._active_category))
            self.current_patient = Patient(
                symptoms_text=symptoms,
                correct_code=self._active_correct_code,
                category=self._active_category,
            )

    def start_case_clock(self) -> None:
        """
        Start timing/logging for the current case.
        Intended to be called by the UI after a 'briefing' phase.
        """
        if self.game_state != GameState.PLAYING:
            return
        if self._case_clock_started:
            return
        if not self._active_correct_code:
            return
        self._case_clock_started = True
        self.stats.start_case_timer()
        self.stats.log_attempt(
            event="case_start",
            case_code=self._active_correct_code,
            case_category=self._active_category,
            entered_code="",
            correct=False,
            response_time_s=0,
            keystrokes=0,
            code_length=len(self._active_correct_code),
            time_remaining_s=self.time_remaining,
            time_limit_s=self.time_limit_s,
            stability=self.stability,
            score=self.score,
        )

    def tick(self) -> None:
        if self.game_state != GameState.PLAYING:
            return
        if not self._case_clock_started:
            return

        self.time_remaining = max(0, self.time_remaining - 1)
        self.stability = max(0, self.stability - self.config.stability_decay_per_second)

        if self.time_remaining <= 0 or self.stability <= 0:
            self.end_game(reason="timeout" if self.time_remaining <= 0 else "stability")

    def submit_code(self, entered_code: str, *, keystrokes: int = 0) -> tuple[bool, str]:
        if self.game_state != GameState.PLAYING or not self._active_correct_code:
            return False, "Game not running."
        if not self._case_clock_started:
            # UI should start the clock after briefing; be safe anyway.
            self.start_case_clock()

        code = entered_code.strip().upper()
        correct = code == self._active_correct_code
        rt = self.stats.response_time_s()
        correct_desc = self._active_entry.description if self._active_entry else ""
        self.last_case_answer = self._active_correct_code if not correct_desc else f"{self._active_correct_code} — {correct_desc}"

        if correct:
            self._wrong_streak = 0
            bonus = self.config.bonus_fast_points if self.time_remaining >= self.config.bonus_fast_threshold_s else 0
            self.score += self.config.points_correct + bonus
            self.stats.end_case_timer(self._active_category)
            self.stats.log_attempt(
                event="submit",
                case_code=self._active_correct_code,
                case_category=self._active_category,
                entered_code=code,
                correct=True,
                response_time_s=rt,
                keystrokes=keystrokes,
                code_length=len(self._active_correct_code),
                time_remaining_s=self.time_remaining,
                time_limit_s=self.time_limit_s,
                stability=self.stability,
                score=self.score,
            )
            answer = self._active_correct_code if not correct_desc else f"{self._active_correct_code} — {correct_desc}"
            msg = f"Correct: {answer}. +{self.config.points_correct + bonus} points."
            self._next_case()
            return True, msg

        self._wrong_streak += 1
        self.score += self.config.points_wrong
        self.stability = max(0, self.stability - self.config.stability_penalty_wrong)
        self.stats.log_attempt(
            event="submit",
            case_code=self._active_correct_code,
            case_category=self._active_category,
            entered_code=code,
            correct=False,
            response_time_s=rt,
            keystrokes=keystrokes,
            code_length=len(self._active_correct_code),
            time_remaining_s=self.time_remaining,
            time_limit_s=self.time_limit_s,
            stability=self.stability,
            score=self.score,
        )
        if self.stability <= 0:
            self.end_game(reason="stability")
            answer = self._active_correct_code if not correct_desc else f"{self._active_correct_code} — {correct_desc}"
            return False, f"Wrong. Correct: {answer}. Patient coded blue."
        answer = self._active_correct_code if not correct_desc else f"{self._active_correct_code} — {correct_desc}"
        return False, f"Wrong. Correct: {answer}. -{abs(self.config.points_wrong)} points."

    def skip_case(self) -> None:
        if self.game_state != GameState.PLAYING or not self._active_correct_code:
            return
        if not self._case_clock_started:
            self.start_case_clock()
        self._wrong_streak = max(0, self._wrong_streak - 1)
        self.stability = max(0, self.stability - self.config.stability_penalty_skip)
        self.stats.end_case_timer(self._active_category)
        self.stats.log_attempt(
            event="skip",
            case_code=self._active_correct_code,
            case_category=self._active_category,
            entered_code="",
            correct=False,
            response_time_s=self.stats.response_time_s(),
            keystrokes=0,
            code_length=len(self._active_correct_code),
            time_remaining_s=self.time_remaining,
            time_limit_s=self.time_limit_s,
            stability=self.stability,
            score=self.score,
        )
        if self.stability <= 0:
            self.end_game(reason="stability")
            return
        self._next_case()

    def end_game(self, *, reason: str) -> None:
        if self.game_state != GameState.PLAYING:
            return
        self.game_state = GameState.GAME_OVER
        self.last_game_over_reason = reason
        # Freeze the final case answer for the results screen
        if not self.last_case_answer:
            desc = self._active_entry.description if self._active_entry else ""
            self.last_case_answer = self._active_correct_code if not desc else f"{self._active_correct_code} — {desc}"
        code = self._active_correct_code
        cat = self._active_category
        self.stats.log_attempt(
            event=f"game_over:{reason}",
            case_code=code,
            case_category=cat,
            entered_code="",
            correct=False,
            time_remaining_s=self.time_remaining,
            stability=self.stability,
            score=self.score,
        )

