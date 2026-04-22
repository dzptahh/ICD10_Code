# ICD-10 Code Blue (Tkinter)

Medical simulation / learning game for practicing ICD-10 coding under time pressure.

## Run

```bash
python3 main.py
```

## What’s inside

- `Patient`: one randomly generated patient case (symptoms + correct ICD-10).
- `ICD_Database`: loads ICD-10 data from CSV and supports search + category filtering.
- `GameController`: manages game state, score, timer, stability, and case progression.
- `StatsTracker`: logs every attempt to CSV and computes per-category performance.
- `UI_Manager`: Tkinter UI (menu, game screen, handbook search, analytics screen).

## Data

- `data/icd10_sample.csv`: small sample dataset (you can replace it with your own).
- `data/game_logs/`: session logs saved as CSV (created automatically).

