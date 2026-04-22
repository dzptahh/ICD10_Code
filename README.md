# ICD10 Code Blue

ICD10 Code Blue is a Python learning game where players diagnose symptom-based cases and submit the correct ICD-10 code.  
It combines timed gameplay with a handbook search tool and a post-game statistics dashboard.

## Features

- Symptom-based patient cases
- Two answering methods:
  - Type ICD-10 code directly
  - Search and select from medical handbook
- Real-time timer/pressure gameplay
- Session logging and post-game analytics charts

## Quick Start

### Prerequisites

- Python 3.10+

### Run

```bash
python main.py
```

## Dependencies

This project currently uses only Python standard library modules.  
For assignment compatibility, dependency notes are kept in [`requirement.txt`](requirement.txt).

## Project Structure

```text
ICD10_Code/
├── icd10_code_blue/
│   ├── app.py
│   ├── cases.py
│   ├── controller.py
│   ├── icd_database.py
│   ├── patient.py
│   ├── stats.py
│   └── ui.py
├── data/
│   ├── icd10_sample.csv
│   └── game_logs/
├── main.py
├── DESCRIPTION.md
├── requirement.txt
├── .gitignore
└── LICENSE
```

## Data

- `data/icd10_sample.csv`: sample ICD-10 dataset used by the game.
- `data/game_logs/`: generated session CSV logs.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE).

