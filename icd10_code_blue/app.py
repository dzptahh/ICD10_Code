from __future__ import annotations

from pathlib import Path

import tkinter as tk
from tkinter import messagebox

from .controller import GameController
from .cases import load_cases_csv
from .icd_database import ICD_Database
from .stats import StatsTracker
from .ui import UI_Manager


def run_app() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    icd_csv = data_dir / "icd10_sample.csv"
    global_csv = data_dir / "game_logs" / "global_attempts.csv"

    db = ICD_Database()
    try:
        db.load_data(icd_csv)
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("ICD-10 data error", f"Could not load ICD-10 data:\n{e}")
        root.destroy()
        raise

    stats = StatsTracker(global_csv_path=global_csv)
    controller = GameController(db=db, stats=stats)
    try:
        # Single-source dataset: game cases are loaded from the same ICD CSV.
        controller.load_cases(load_cases_csv(icd_csv))
    except Exception:
        # Keep the app playable with fallback generated cases if sample cases fail to load.
        pass

    root = tk.Tk()
    UI_Manager(
        root=root,
        controller=controller,
        db_search=lambda q: db.search_code(q, limit=80),
        stats=stats,
        data_dir=data_dir,
    )
    root.mainloop()

