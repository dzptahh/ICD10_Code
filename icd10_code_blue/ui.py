from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from .controller import GameController, GameState
from .icd_database import ICDEntry
from .cases import load_cases_csv
from .stats import StatsTracker


@dataclass(frozen=True)
class UIStrings:
    title: str = "ICD-10 Code Blue"


@dataclass(frozen=True)
class Palette:
    bg: str = "#0b1020"
    panel: str = "#121a33"
    panel_2: str = "#0f1730"
    text: str = "#e6e9f2"
    muted: str = "#a8b0c4"
    accent: str = "#2f6fed"
    good: str = "#2aa84a"
    warn: str = "#f0b429"
    bad: str = "#d64545"


class UI_Manager:
    def __init__(
        self,
        root: tk.Tk,
        controller: GameController,
        db_search: Callable[[str], list[ICDEntry]],
        stats: StatsTracker,
        data_dir: Path,
        strings: UIStrings | None = None,
    ) -> None:
        self.root = root
        self.controller = controller
        self.db_search = db_search
        self.stats = stats
        self.data_dir = data_dir
        self.s = strings or UIStrings()
        self.p = Palette()

        self.root.title(self.s.title)
        self.root.geometry("980x620")
        self.root.minsize(920, 580)
        self.root.configure(background=self.p.bg)

        self._timer_job: str | None = None

        self._build_layout()
        self.show_menu()

    def _build_layout(self) -> None:
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        # Base theme (dark, game-like)
        self.style.configure("TFrame", background=self.p.bg)
        self.style.configure("TLabel", background=self.p.bg, foreground=self.p.text)
        self.style.configure("Muted.TLabel", background=self.p.bg, foreground=self.p.muted)
        self.style.configure("Panel.TFrame", background=self.p.panel)
        self.style.configure("Panel.TLabel", background=self.p.panel, foreground=self.p.text)
        self.style.configure("Title.TLabel", background=self.p.panel, foreground=self.p.text, font=("Helvetica", 22, "bold"))
        self.style.configure("Badge.TLabel", background=self.p.panel_2, foreground=self.p.text, padding=(10, 4), font=("Helvetica", 11, "bold"))
        self.style.configure("HUD.TLabel", background=self.p.panel, foreground=self.p.text, font=("Helvetica", 11, "bold"))

        self.style.configure("Game.TButton", font=("Helvetica", 12, "bold"), padding=(14, 10))
        self.style.configure("Small.TButton", font=("Helvetica", 10, "bold"), padding=(10, 6))

        self.style.configure("Green.Horizontal.TProgressbar", troughcolor=self.p.panel_2, background=self.p.good)
        self.style.configure("Yellow.Horizontal.TProgressbar", troughcolor=self.p.panel_2, background=self.p.warn)
        self.style.configure("Red.Horizontal.TProgressbar", troughcolor=self.p.panel_2, background=self.p.bad)

        self.container = ttk.Frame(self.root, padding=16)
        self.container.pack(fill="both", expand=True)

        self.header = ttk.Frame(self.container, style="Panel.TFrame", padding=(12, 10))
        self.header.pack(fill="x")

        self.title_lbl = ttk.Label(self.header, text=self.s.title, style="Title.TLabel")
        self.title_lbl.pack(side="left")

        self.state_badge = ttk.Label(self.header, text="", style="Badge.TLabel")
        self.state_badge.pack(side="right")

        self.body = ttk.Frame(self.container)
        self.body.pack(fill="both", expand=True, pady=(12, 0))

        self.menu_frame = ttk.Frame(self.body)
        self.brief_frame = ttk.Frame(self.body)
        self.game_frame = ttk.Frame(self.body)
        self.over_frame = ttk.Frame(self.body)

        self._build_menu()
        self._build_briefing()
        self._build_game()
        self._build_game_over()

    def _clear_body(self) -> None:
        for child in self.body.winfo_children():
            child.pack_forget()

    def _set_badge(self, text: str) -> None:
        self.state_badge.configure(text=text)

    def show_menu(self) -> None:
        self._stop_timer()
        self._clear_body()
        self._set_badge("MENU")
        self.menu_frame.pack(fill="both", expand=True)

    def start_game(self) -> None:
        self.controller.start_game()
        self._clear_body()
        self._set_badge("PLAYING")
        self.brief_frame.pack(fill="both", expand=True)
        self._begin_case_briefing()
        self._start_timer()

    def show_game_over(self) -> None:
        self._stop_timer()
        self._clear_body()
        self._set_badge("RESULTS")
        self._render_game_over()
        self.over_frame.pack(fill="both", expand=True)

    def _build_menu(self) -> None:
        left = ttk.Frame(self.menu_frame, style="Panel.TFrame", padding=18)
        left.pack(fill="both", expand=True)

        ttk.Label(left, text="Medical coding under pressure.", style="HUD.TLabel").pack(anchor="w")
        ttk.Label(
            left,
            text="Type a code or select from the handbook. Wrong answers or slow play drops stability.",
            style="Muted.TLabel",
            wraplength=820,
            justify="left",
        ).pack(anchor="w", pady=(6, 18))

        btns = ttk.Frame(left)
        btns.pack(anchor="w")

        ttk.Button(btns, text="Start Game", command=self.start_game, style="Game.TButton").grid(
            row=0, column=0, padx=(0, 10), pady=6, sticky="w"
        )
        ttk.Button(btns, text="Load Cases CSV", command=self._load_cases_csv, style="Game.TButton").grid(
            row=0, column=1, padx=(0, 10), pady=6, sticky="w"
        )
        ttk.Button(btns, text="Quit", command=self.root.destroy, style="Game.TButton").grid(
            row=0, column=2, pady=6, sticky="w"
        )

        how = ttk.Labelframe(left, text="How to play", padding=12)
        how.pack(fill="x", pady=(18, 0))
        ttk.Label(
            how,
            text="- Search the handbook on the right.\n- Choose a method: Type or Select.\n- Submit before time runs out.\n- Keep stability above 0 to avoid CODE BLUE.",
            style="Muted.TLabel",
            justify="left",
        ).pack(anchor="w")

        self.cases_status = tk.StringVar(value="Cases: (using auto-generated symptoms)")
        ttk.Label(left, textvariable=self.cases_status, style="Muted.TLabel").pack(anchor="w", pady=(10, 0))

    def _build_briefing(self) -> None:
        panel = ttk.Frame(self.brief_frame, style="Panel.TFrame", padding=18)
        panel.pack(fill="both", expand=True)

        ttk.Label(panel, text="Case Briefing", style="HUD.TLabel").pack(anchor="w")
        ttk.Label(
            panel,
            text="Read the symptoms carefully. The coding timer starts after the briefing.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(6, 12))

        self.brief_countdown = tk.StringVar(value="Starting…")
        ttk.Label(panel, textvariable=self.brief_countdown, style="HUD.TLabel").pack(anchor="w", pady=(0, 12))

        self.brief_text = tk.Text(panel, height=10, wrap="word", font=("Helvetica", 14))
        self.brief_text.pack(fill="x")
        self.brief_text.configure(state="disabled")

        btns = ttk.Frame(panel)
        btns.pack(fill="x", pady=(16, 0))
        ttk.Button(btns, text="Skip Briefing", command=self._enter_play_phase, style="Game.TButton").pack(side="left")
        ttk.Button(btns, text="End Run", command=self._on_end, style="Game.TButton").pack(side="right")

        self._in_briefing = False
        self._brief_remaining_s = 0

    def _load_cases_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="Select patient cases CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            cases = load_cases_csv(path)
            self.controller.load_cases(cases)
            self.cases_status.set(f"Cases loaded: {len(cases)} (from {Path(path).name})")
        except Exception as e:
            messagebox.showerror("Load failed", f"Could not load Cases CSV:\n{e}")

    def _build_game(self) -> None:
        top = ttk.Frame(self.game_frame, style="Panel.TFrame", padding=(12, 10))
        top.pack(fill="x")

        self.score_var = tk.StringVar(value="Score: 0")
        self.time_var = tk.StringVar(value="Time: --")
        self.case_var = tk.StringVar(value="Case: --")
        self.feedback_var = tk.StringVar(value="")

        ttk.Label(top, textvariable=self.case_var, style="HUD.TLabel").pack(side="left")
        ttk.Label(top, textvariable=self.time_var, style="HUD.TLabel").pack(side="right")
        ttk.Label(top, textvariable=self.score_var, style="HUD.TLabel").pack(side="right", padx=(0, 14))

        mid = ttk.Frame(self.game_frame)
        mid.pack(fill="both", expand=True, pady=(12, 0))
        mid.columnconfigure(0, weight=3)
        mid.columnconfigure(1, weight=2)
        mid.rowconfigure(0, weight=1)

        case_box = ttk.Labelframe(mid, text="Patient Case", padding=12)
        case_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.symptoms_txt = tk.Text(
            case_box, height=7, wrap="word", font=("Helvetica", 12)
        )
        self.symptoms_txt.pack(fill="x")
        self.symptoms_txt.configure(state="disabled")

        stability_row = ttk.Frame(case_box)
        stability_row.pack(fill="x", pady=(12, 0))
        ttk.Label(stability_row, text="Patient Stability").pack(side="left")
        self.stability_var = tk.StringVar(value="100%")
        ttk.Label(stability_row, textvariable=self.stability_var).pack(side="right")
        self.stability_bar = ttk.Progressbar(
            stability_row, length=300, maximum=self.controller.config.max_stability
        )
        self.stability_bar.pack(side="left", padx=(10, 0), fill="x", expand=True)

        input_box = ttk.Labelframe(case_box, text="Choose ICD-10 code", padding=12)
        input_box.pack(fill="x", pady=(12, 0))

        self.answer_mode = tk.StringVar(value="type")
        self.selected_code_var = tk.StringVar(value="")

        mode_row = ttk.Frame(input_box)
        mode_row.pack(fill="x", pady=(0, 8))
        ttk.Label(mode_row, text="Method:").pack(side="left")
        ttk.Radiobutton(
            mode_row, text="Type code", variable=self.answer_mode, value="type", command=self._sync_answer_mode
        ).pack(side="left", padx=(8, 0))
        ttk.Radiobutton(
            mode_row, text="Select from handbook", variable=self.answer_mode, value="select", command=self._sync_answer_mode
        ).pack(side="left", padx=(8, 0))
        self.selected_lbl = ttk.Label(mode_row, textvariable=self.selected_code_var, style="Panel.TLabel")
        self.selected_lbl.pack(side="right")

        self.code_entry = ttk.Entry(input_box, font=("Helvetica", 14))
        self.code_entry.pack(fill="x")
        self.code_entry.bind("<Return>", lambda _e: self._on_submit())
        self.code_entry.bind("<Key>", self._on_code_key)
        self._keystrokes_this_case = 0

        actions = ttk.Frame(input_box)
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Submit", command=self._on_submit, style="Small.TButton").pack(
            side="left"
        )
        ttk.Button(actions, text="Skip (-stability)", command=self._on_skip, style="Small.TButton").pack(
            side="left", padx=(10, 0)
        )
        ttk.Button(actions, text="End Run", command=self._on_end, style="Small.TButton").pack(
            side="right"
        )

        feedback = ttk.Label(case_box, textvariable=self.feedback_var, foreground=self.p.good, font=("Helvetica", 11, "bold"))
        feedback.pack(anchor="w", pady=(10, 0))

        handbook = ttk.Labelframe(mid, text="Medical Handbook (Search ICD-10)", padding=12)
        handbook.grid(row=0, column=1, sticky="nsew")
        handbook.rowconfigure(2, weight=1)
        handbook.columnconfigure(0, weight=1)

        self.search_var = tk.StringVar(value="")
        search_entry = ttk.Entry(handbook, textvariable=self.search_var)
        search_entry.grid(row=0, column=0, sticky="ew")
        search_entry.bind("<Return>", lambda _e: self._on_search())

        ttk.Button(handbook, text="Search", command=self._on_search).grid(
            row=0, column=1, padx=(8, 0)
        )

        ttk.Label(handbook, text="Double-click a result to select it.").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(8, 6)
        )

        self.results_tree = ttk.Treeview(
            handbook,
            columns=("code", "desc", "cat"),
            show="headings",
            height=12,
        )
        self.results_tree.heading("code", text="Code")
        self.results_tree.heading("desc", text="Description")
        self.results_tree.heading("cat", text="Category")
        self.results_tree.column("code", width=80, anchor="center")
        self.results_tree.column("desc", width=260, anchor="w")
        self.results_tree.column("cat", width=120, anchor="center")
        self.results_tree.grid(row=2, column=0, columnspan=2, sticky="nsew")

        res_scroll = ttk.Scrollbar(handbook, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=res_scroll.set)
        res_scroll.grid(row=2, column=2, sticky="ns")

        self.results_tree.bind("<<TreeviewSelect>>", lambda _e: self._select_from_result_tree())
        self.results_tree.bind("<Double-1>", lambda _e: self._select_from_result_tree(submit=True))

        self._result_entries: list[ICDEntry] = []
        self._sync_answer_mode()

    def _build_game_over(self) -> None:
        top = ttk.Frame(self.over_frame)
        top.pack(fill="x")

        self.over_title = ttk.Label(top, text="Code Blue", font=("Helvetica", 18, "bold"))
        self.over_title.pack(anchor="w")

        self.over_subtitle = ttk.Label(top, text="", font=("Helvetica", 12))
        self.over_subtitle.pack(anchor="w", pady=(6, 0))

        self.run_var = tk.StringVar(value="")
        ttk.Label(top, textvariable=self.run_var, style="Muted.TLabel").pack(anchor="w", pady=(6, 0))

        self.over_metrics = ttk.Frame(top)
        self.over_metrics.pack(fill="x", pady=(10, 0))
        self.rt_var = tk.StringVar(value="Response time: —")
        self.acc_var = tk.StringVar(value="Accuracy: —")
        self.stress_var = tk.StringVar(value="Stress factor r: —")
        ttk.Label(self.over_metrics, textvariable=self.rt_var).pack(side="left")
        ttk.Label(self.over_metrics, textvariable=self.acc_var).pack(side="left", padx=(16, 0))
        ttk.Label(self.over_metrics, textvariable=self.stress_var).pack(side="left", padx=(16, 0))

        mid = ttk.Frame(self.over_frame)
        mid.pack(fill="both", expand=True, pady=(14, 0))
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)
        mid.rowconfigure(0, weight=1)

        table_box = ttk.Labelframe(mid, text="Learning Curve (by Category)", padding=12)
        table_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        table_box.rowconfigure(0, weight=1)
        table_box.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            table_box,
            columns=("category", "attempts", "correct", "accuracy", "time"),
            show="headings",
            height=12,
        )
        for col, text, w in [
            ("category", "Category", 160),
            ("attempts", "Attempts", 80),
            ("correct", "Correct", 80),
            ("accuracy", "Accuracy", 90),
            ("time", "Time Spent (s)", 120),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(table_box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        chart_box = ttk.Labelframe(mid, text="Data Analysis Report", padding=12)
        chart_box.grid(row=0, column=1, sticky="nsew")
        chart_box.rowconfigure(1, weight=1)
        chart_box.columnconfigure(0, weight=1)

        controls = ttk.Frame(chart_box)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(controls, text="Chart:").pack(side="left")
        self.chart_mode = tk.StringVar(value="Error Histogram")
        self.chart_select = ttk.Combobox(
            controls,
            textvariable=self.chart_mode,
            state="readonly",
            values=["Error Histogram", "Response Time Improvement", "Category Distribution"],
            width=28,
        )
        self.chart_select.pack(side="left", padx=(8, 0))
        self.chart_select.bind("<<ComboboxSelected>>", lambda _e: self._render_game_over())

        self.chart = tk.Canvas(chart_box, background="white", highlightthickness=1, highlightbackground="#ddd")
        self.chart.grid(row=1, column=0, sticky="nsew")

        bottom = ttk.Frame(self.over_frame)
        bottom.pack(fill="x", pady=(12, 0))
        ttk.Button(bottom, text="Play Again", command=self.start_game).pack(side="left")
        ttk.Button(bottom, text="Back to Menu", command=self.show_menu).pack(side="left", padx=(10, 0))
        ttk.Button(bottom, text="Quit", command=self.root.destroy).pack(side="right")

    def _start_timer(self) -> None:
        self._stop_timer()
        self._schedule_tick()

    def _stop_timer(self) -> None:
        if self._timer_job is not None:
            try:
                self.root.after_cancel(self._timer_job)
            except tk.TclError:
                pass
            self._timer_job = None

    def _schedule_tick(self) -> None:
        self._timer_job = self.root.after(1000, self._on_tick)

    def _on_tick(self) -> None:
        if self._in_briefing:
            self._brief_remaining_s = max(0, self._brief_remaining_s - 1)
            self.brief_countdown.set(f"Briefing ends in {self._brief_remaining_s}s")
            if self._brief_remaining_s <= 0:
                self._enter_play_phase()
                return
        else:
            self.controller.tick()
            if self.controller.game_state == GameState.GAME_OVER:
                self.show_game_over()
                return
            self._refresh_hud()
        self._schedule_tick()

    def _begin_case_briefing(self) -> None:
        p = self.controller.current_patient
        if not p:
            return
        self._in_briefing = True
        self._brief_remaining_s = 15
        self.brief_countdown.set(f"Briefing ends in {self._brief_remaining_s}s")
        self.brief_text.configure(state="normal")
        self.brief_text.delete("1.0", "end")
        self.brief_text.insert("1.0", p.symptoms_text)
        self.brief_text.configure(state="disabled")

    def _enter_play_phase(self) -> None:
        if self.controller.game_state != GameState.PLAYING:
            return
        self._in_briefing = False
        self._clear_body()
        self.game_frame.pack(fill="both", expand=True)
        self.controller.start_case_clock()
        self._refresh_case_view()

    def _refresh_case_view(self) -> None:
        p = self.controller.current_patient
        if not p:
            return
        self.symptoms_txt.configure(state="normal")
        self.symptoms_txt.delete("1.0", "end")
        self.symptoms_txt.insert("1.0", p.symptoms_text)
        self.symptoms_txt.configure(state="disabled")

        self.code_entry.delete(0, "end")
        self.code_entry.focus_set()
        self._keystrokes_this_case = 0
        self.selected_code_var.set("")
        self.feedback_var.set("")
        self._refresh_hud()

    def _refresh_hud(self) -> None:
        self.score_var.set(f"Score: {self.controller.score}")
        self.time_var.set(f"Time: {self.controller.time_remaining}s / {self.controller.time_limit_s}s")
        self.case_var.set(f"Case: {self.controller.case_index}")
        self.stability_bar.configure(maximum=self.controller.config.max_stability)
        self.stability_bar["value"] = self.controller.stability
        pct = int((self.controller.stability / max(1, self.controller.config.max_stability)) * 100)
        self.stability_var.set(f"{pct}%")

        # Change bar color by stability level
        style = "Green.Horizontal.TProgressbar"
        if pct <= 30:
            style = "Red.Horizontal.TProgressbar"
        elif pct <= 60:
            style = "Yellow.Horizontal.TProgressbar"
        self.stability_bar.configure(style=style)

    def _on_submit(self) -> None:
        if self.answer_mode.get() == "select":
            code = (self.selected_code_var.get() or "").strip()
            if not code:
                self.feedback_var.set("Select a code from the handbook first.")
                return
            # selected_code_var contains the raw code (e.g., "I21.9")
            ok, msg = self.controller.submit_code(code, keystrokes=0)
        else:
            code = self.code_entry.get()
            ok, msg = self.controller.submit_code(code, keystrokes=self._keystrokes_this_case)
        self.feedback_var.set(msg)
        self._refresh_hud()
        if self.controller.game_state == GameState.GAME_OVER:
            self.show_game_over()
            return
        if ok:
            # next case -> briefing again
            self._clear_body()
            self.brief_frame.pack(fill="both", expand=True)
            self._begin_case_briefing()
        else:
            self.feedback_var.set(msg)

    def _on_code_key(self, e: tk.Event) -> None:
        # Count typing efficiency (exclude pure modifier keys)
        ks = str(getattr(e, "keysym", "") or "").lower()
        if ks in {"shift_l", "shift_r", "control_l", "control_r", "alt_l", "alt_r", "meta_l", "meta_r"}:
            return
        self._keystrokes_this_case += 1

    def _on_skip(self) -> None:
        self.controller.skip_case()
        self._refresh_hud()
        if self.controller.game_state == GameState.GAME_OVER:
            self.show_game_over()
            return
        self._refresh_case_view()

    def _on_end(self) -> None:
        self.controller.end_game(reason="ended")
        self.show_game_over()

    def _on_search(self) -> None:
        q = self.search_var.get()
        results = self.db_search(q)
        self._result_entries = results
        for r in self.results_tree.get_children():
            self.results_tree.delete(r)
        for i, e in enumerate(results):
            self.results_tree.insert("", "end", iid=str(i), values=(e.code, e.description, e.category))

    def _select_from_result_tree(self, *, submit: bool = False) -> None:
        sel = self.results_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if idx < 0 or idx >= len(self._result_entries):
            return
        entry = self._result_entries[idx]
        self.selected_code_var.set(entry.code.strip().upper())

        # Link selection into typing field too (nice UX)
        self._set_code_entry(entry.code)
        if self.answer_mode.get() == "type":
            self.code_entry.focus_set()

        if submit and self.answer_mode.get() == "select":
            self._on_submit()

    def _sync_answer_mode(self) -> None:
        mode = self.answer_mode.get()
        if mode == "select":
            try:
                self.code_entry.state(["readonly"])
            except tk.TclError:
                self.code_entry.configure(state="readonly")
        else:
            try:
                self.code_entry.state(["!readonly"])
            except tk.TclError:
                self.code_entry.configure(state="normal")
            self.code_entry.focus_set()

    def _set_code_entry(self, value: str) -> None:
        """
        Show a code in the entry even if we're in readonly mode.
        """
        try:
            was_readonly = "readonly" in self.code_entry.state()
        except tk.TclError:
            was_readonly = False
        if was_readonly:
            try:
                self.code_entry.state(["!readonly"])
            except tk.TclError:
                self.code_entry.configure(state="normal")
        self.code_entry.delete(0, "end")
        self.code_entry.insert(0, value)
        if was_readonly:
            try:
                self.code_entry.state(["readonly"])
            except tk.TclError:
                self.code_entry.configure(state="readonly")

    def _render_game_over(self) -> None:
        reason = (self.controller.last_game_over_reason or "").strip()
        title = "RUN COMPLETE"
        if reason in {"timeout", "stability"}:
            title = "CODE BLUE"
        elif reason == "ended":
            title = "RUN ENDED"
        submits = self.stats.submit_records()
        attempted = len(submits)
        correct = sum(1 for r in submits if r.correct == 1)
        last_ans = getattr(self.controller, "last_case_answer", "") or ""
        tail = f"   |   Last case answer: {last_ans}" if last_ans else ""
        self.over_title.configure(text=title)
        self.over_subtitle.configure(text=f"Final Score: {self.controller.score}")
        self.run_var.set(f"Attempts: {attempted}   Correct: {correct}   Wrong: {attempted - correct}{tail}")

        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = self.stats.summary_rows()
        for cat, attempts, correct, acc, t in rows:
            self.tree.insert(
                "",
                "end",
                values=(cat, attempts, correct, f"{acc*100:.0f}%", t),
            )

        self._render_metrics()
        self._draw_selected_chart()
        self._save_session_log()

    def _render_metrics(self) -> None:
        rts = self.stats.response_time_series()
        mean, std = self.stats.mean_std(rts)
        if mean is None or std is None:
            self.rt_var.set("Response time: —")
        else:
            self.rt_var.set(f"Response time: mean {mean:.1f}s, sd {std:.1f}s")

        accs = self.stats.accuracy_series()
        if not accs:
            self.acc_var.set("Accuracy: —")
        else:
            pct = (sum(accs) / len(accs)) * 100
            self.acc_var.set(f"Accuracy: {pct:.0f}% ({sum(accs)}/{len(accs)})")

        r = self.stats.stress_factor_correlation()
        self.stress_var.set("Stress factor r: —" if r is None else f"Stress factor r: {r:.2f}")

    def _draw_selected_chart(self) -> None:
        mode = self.chart_mode.get().strip()
        if mode == "Response Time Improvement":
            self._draw_response_time_line()
        elif mode == "Category Distribution":
            self._draw_category_distribution()
        else:
            self._draw_error_histogram()

    def _canvas_dims(self) -> tuple[int, int]:
        return (self.chart.winfo_width() or 420, self.chart.winfo_height() or 320)

    def _draw_axes(self, title: str, x_label: str, y_label: str) -> tuple[int, int, int, int]:
        c = self.chart
        c.delete("all")
        w, h = self._canvas_dims()
        pad = 46
        c.create_text(12, 10, anchor="nw", text=title, font=("Helvetica", 12, "bold"))
        # axes
        x0, y0, x1, y1 = pad, h - pad, w - 16, 40
        c.create_line(x0, y0, x1, y0, fill="#333")
        c.create_line(x0, y0, x0, y1, fill="#333")
        c.create_text((x0 + x1) / 2, h - 10, anchor="s", text=x_label, fill="#333")
        c.create_text(10, (y0 + y1) / 2, anchor="w", text=y_label, angle=90, fill="#333")
        return x0, y0, x1, y1

    def _draw_error_histogram(self) -> None:
        # Histogram of incorrect diagnoses: values are 0/1, so show counts of correct vs incorrect.
        x0, y0, x1, y1 = self._draw_axes(
            "Histogram of Error Distribution",
            "Outcome (0=Correct, 1=Incorrect)",
            "Frequency",
        )
        recs = self.stats.submit_records()
        correct_n = sum(1 for r in recs if r.correct == 1)
        wrong_n = sum(1 for r in recs if r.correct == 0)
        max_n = max(1, correct_n, wrong_n)

        c = self.chart
        bar_w = (x1 - x0) / 3
        for i, (label, count, color) in enumerate([("0", correct_n, "#2aa84a"), ("1", wrong_n, "#d64545")]):
            bx0 = x0 + (i + 0.5) * bar_w
            bx1 = bx0 + bar_w * 0.8
            height = (y0 - y1) * (count / max_n)
            by0 = y0
            by1 = y0 - height
            c.create_rectangle(bx0, by1, bx1, by0, fill=color, outline="")
            c.create_text((bx0 + bx1) / 2, y0 + 14, text=label, fill="#333")
            c.create_text((bx0 + bx1) / 2, by1 - 10, text=str(count), fill="#111")

    def _draw_response_time_line(self) -> None:
        x0, y0, x1, y1 = self._draw_axes(
            "Line Graph of Response Time Improvement",
            "Attempt number",
            "Response time (s)",
        )
        rts = self.stats.response_time_series()
        if len(rts) < 2:
            self.chart.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="Not enough attempts yet.", fill="#777")
            return

        c = self.chart
        n = len(rts)
        max_rt = max(1, max(rts))
        pts: list[tuple[float, float]] = []
        for i, rt in enumerate(rts, start=1):
            x = x0 + (x1 - x0) * ((i - 1) / (n - 1))
            y = y0 - (y0 - y1) * (rt / max_rt)
            pts.append((x, y))
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            c.create_line(ax, ay, bx, by, fill="#2f6fed", width=2)
        for i, (x, y) in enumerate(pts, start=1):
            c.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#2f6fed", outline="")
            if i == 1 or i == n:
                c.create_text(x, y - 10, text=str(rts[i - 1]), fill="#111")

    def _draw_category_distribution(self) -> None:
        x0, y0, x1, y1 = self._draw_axes(
            "Category Distribution Chart",
            "ICD-10 categories",
            "Count",
        )
        counts = self.stats.category_counts()
        if not counts:
            self.chart.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="No data yet.", fill="#777")
            return

        items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].lower()))
        max_items = 8
        if len(items) > max_items:
            items = items[:max_items]
        max_count = max(1, max(v for _k, v in items))

        c = self.chart
        bar_gap = 8
        total_w = x1 - x0
        bar_w = max(12, int((total_w - bar_gap * (len(items) - 1)) / len(items)))
        for i, (cat, v) in enumerate(items):
            bx0 = x0 + i * (bar_w + bar_gap)
            bx1 = bx0 + bar_w
            height = (y0 - y1) * (v / max_count)
            by1 = y0 - height
            c.create_rectangle(bx0, by1, bx1, y0, fill="#7c4dff", outline="")
            c.create_text((bx0 + bx1) / 2, by1 - 10, text=str(v), fill="#111")
            label = cat if len(cat) <= 10 else cat[:9] + "…"
            c.create_text((bx0 + bx1) / 2, y0 + 14, text=label, fill="#333")

    def _save_session_log(self) -> None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = self.data_dir / "game_logs" / f"session_{ts}.csv"
        try:
            path = self.stats.save_to_csv(out)
            self.controller.stats.log_attempt(
                event="log_saved",
                case_code="",
                case_category="",
                entered_code=str(path),
                correct=False,
                time_remaining_s=self.controller.time_remaining,
                time_limit_s=self.controller.time_limit_s,
                stability=self.controller.stability,
                score=self.controller.score,
            )
        except Exception as e:
            messagebox.showwarning("Save failed", f"Could not save session log:\n{e}")

