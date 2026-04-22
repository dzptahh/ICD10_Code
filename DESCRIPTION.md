# Project Description

## 1. Project Overview

- **Project Name:** ICD10 Code Game

- **Brief Description:**
  ICD10 Code Game is an educational Python-based game that simulates real-world clinical coding scenarios. Players are presented with a patient's symptoms and must identify the correct diagnosis, then submit the corresponding ICD-10 (International Classification of Diseases, 10th Revision) code. The game supports two input methods: typing the code directly from memory, or using a built-in handbook search function that suggests close-matching ICD-10 codes based on keywords or partial input.

  The application also tracks player performance across sessions and presents statistical visualizations — including response time trends, error distributions, and accuracy rates — to help players identify their strengths and areas for improvement.

- **Problem Statement:**
  Learning and memorizing ICD-10 codes is a critical but notoriously difficult skill for medical students, clinical coders, and healthcare workers. Traditional study methods (reading codebooks, flashcards) are passive and do not reflect the pressure of real-world diagnostic decision-making. This project addresses that gap by turning ICD-10 coding practice into an active, gamified experience.

- **Target Users:**
  - Medical and nursing students
  - Clinical coders and health information professionals
  - Healthcare workers preparing for coding assessments
  - Anyone studying the ICD-10 classification system

- **Key Features:**
  - 🩺 Symptom-based diagnostic challenges
  - ⌨️ Direct ICD-10 code input mode
  - 🔍 Handbook search mode with near-match code suggestions
  - 📊 Performance statistics and data visualizations (5 graph types)
  - 📁 Session history recording for progress tracking

- **Screenshots:**

  > 📸 [View all screenshots](screenshots/)

- **Proposal:**
  📄 **Attachment:** [Proposal](./ICD-10_Code_Blue.pdf)

---

## 2. Concept

### 2.1 Background

This project was inspired by real-world experiences with ICD-10 coding. I have a friend studying Medical Records at Mahidol University, and through working alongside him I gained firsthand exposure to how complex and time-consuming ICD-10 coding can be in practice. I also previously did freelance design work for a client who needed ICD-10 and ICD-9 code books formatted as structured tables with code, description, Thai, and English columns.

These experiences showed me that while ICD-10 resources exist, there is little available that makes the learning process engaging or practical for beginners. Coders often have to manually search through hundreds of codes under time pressure, and no interactive tool simulates that experience for learners.

Additionally, I have always had a strong personal interest in biology, which made the clinical and diagnostic side of this project naturally motivating. The combination of a real-world professional need and personal interest made ICD-10 coding the ideal subject for this project.

### 2.2 Objectives

- To create a gamified learning tool that makes ICD-10 coding practice engaging and effective
- To simulate real diagnostic coding scenarios using symptom-based challenges
- To provide two input modes (direct entry and handbook search) that mirror actual clinical workflows
- To record and visualize player performance data so users can track improvement over time
- To lower the barrier to entry for learning ICD-10 coding outside of a formal classroom setting

---

## 3. UML Class Diagram

> 📎 ![UML Diagram](screenshots/uml.png)
>
> The diagram will include:
> - All classes with attributes and methods
> - Relationships such as association and inheritance

---
## 4. Object-Oriented Programming Implementation

The project is organized across **7 Python modules** containing **12 classes** in total. Each class has a single, focused responsibility following object-oriented design principles.

---

### `cases.py`

#### `PatientCase`
A frozen dataclass that represents one game challenge. It holds three pieces of data: the symptom text shown to the player, the correct ICD-10 code the player must enter, and an optional clinical description for additional context. Objects are immutable once created, ensuring that case data cannot be accidentally modified during gameplay. Instances are produced by the `load_cases_csv()` function, which supports both legacy (`symptoms`, `correct_code`) and unified (`code`, `description`, `symptoms`) CSV column formats.

| | |
|---|---|
| **Type** | Frozen dataclass |
| **Attributes** | `symptoms: str`, `correct_code: str`, `description: str` |

---

### `icd_database.py`

#### `ICDEntry`
A frozen dataclass representing a single row from the ICD-10 dataset. It stores the code identifier, its human-readable description, and the medical category it belongs to (e.g., Cardiology, Neurology). Used throughout the game as the fundamental unit of ICD-10 data.

| | |
|---|---|
| **Type** | Frozen dataclass |
| **Attributes** | `code: str`, `description: str`, `category: str` |

#### `ICD_Database`
Loads the ICD-10 CSV file into memory and provides all lookup and search functionality. The search algorithm is built entirely from scratch — no external NLP library is used. It combines exact code matching, prefix matching, substring matching, token coverage scoring, and a custom Levenshtein-distance fuzzy fallback so that even misspelled queries return useful results. Results are ranked by a composite score and returned in relevance order.

| | |
|---|---|
| **Type** | Class |
| **Key attributes** | `entries: list[ICDEntry]`, `_by_code: dict[str, ICDEntry]` |
| **Key methods** | `load_data()`, `get_by_code()`, `search_code()`, `filter_by_category()`, `categories()` |

---

### `patient.py`

#### `Patient`
A frozen dataclass representing the active patient displayed to the player during a round. It holds the symptom text rendered on screen, the correct ICD-10 code the player must match, and the medical category. The companion function `template_symptoms_for_category()` provides pre-written symptom scenarios as a fallback when no CSV case is available for a given category (e.g., Cardiology, Respiratory, Infectious).

| | |
|---|---|
| **Type** | Frozen dataclass |
| **Attributes** | `symptoms_text: str`, `correct_code: str`, `category: str` |

---

### `controller.py`

#### `GameConfig`
A dataclass that holds all tunable game balance parameters in one place. By separating configuration values from game logic, difficulty can be adjusted (e.g., changing time limits or point penalties) without touching any other class. Parameters include base and minimum time limits, difficulty scaling steps, stability penalties for wrong answers and skips, point values, and the fast-answer bonus threshold.

| | |
|---|---|
| **Type** | Dataclass |
| **Key attributes** | `base_seconds_per_case`, `min_seconds_per_case`, `difficulty_step_points`, `difficulty_step_seconds`, `stability_penalty_wrong`, `stability_penalty_skip`, `points_correct`, `points_wrong`, `bonus_fast_threshold_s`, `bonus_fast_points` |

#### `GameState`
A `str`-based `Enum` representing the three possible states of the game at any point in time: `MENU`, `PLAYING`, and `GAME_OVER`. Shared between `GameController` and `UI_Manager` to keep the interface in sync with the engine — the UI checks `GameController.game_state` to decide which screen to display.

| | |
|---|---|
| **Type** | Enum (`str`) |
| **Values** | `MENU`, `PLAYING`, `GAME_OVER` |

#### `GameController`
The central game engine and the most complex class in the project. It manages the entire game lifecycle: starting and ending games, shuffling and advancing through case decks, computing adaptive time limits (difficulty increases every N points), processing player code submissions, applying scoring and stability changes, handling skip logic, and delegating all data logging to `StatsTracker`. It holds direct references to `ICD_Database`, `StatsTracker`, and `GameConfig`, and owns the current `Patient` object for the active round.

| | |
|---|---|
| **Type** | Class |
| **Key attributes** | `game_state`, `score`, `stability`, `time_remaining`, `current_patient`, `_active_correct_code`, `_wrong_streak` |
| **Key methods** | `start_game()`, `submit_code()`, `skip_case()`, `tick()`, `start_case_clock()`, `end_game()`, `load_cases()` |
| **Relationships** | Owns `GameConfig`; uses `ICD_Database` and `StatsTracker`; creates `Patient` from `PatientCase` or fallback |

---

### `stats.py`

#### `AttemptRecord`
A dataclass that captures a complete snapshot of a single game event — whether a submission, skip, case start, or game over. Each record stores the UTC timestamp, the event type, the correct and entered codes, correctness flag, response time, keystrokes, keystroke efficiency ratio, time remaining, time limit, current stability, and score. These records form the raw dataset for all statistics and graphs.

| | |
|---|---|
| **Type** | Dataclass |
| **Key attributes** | `ts_utc`, `event`, `case_code`, `case_category`, `entered_code`, `correct`, `response_time_s`, `keystrokes`, `keystroke_efficiency`, `time_remaining_s`, `stability`, `score` |

#### `CategoryStats`
A dataclass that accumulates per-category performance totals across a session: total attempts, number of correct answers, and total time spent on that category. Provides a computed `accuracy` property (correct / attempts) used in the summary table on the statistics screen.

| | |
|---|---|
| **Type** | Dataclass |
| **Attributes** | `attempts: int`, `correct: int`, `total_time_spent_s: int` |
| **Property** | `accuracy: float` |

#### `StatsTracker`
Manages all data recording and analysis for a game session. It records every game event as an `AttemptRecord`, maintains a per-category `CategoryStats` dictionary, runs the per-case response timer using UTC timestamps, and writes data to CSV (both a session-level file and a cumulative global log across all sessions). It also exposes analysis methods consumed by `UI_Manager` to render the five statistics graphs: response time series, accuracy series, category counts, Pearson stress-factor correlation, and mean/standard deviation.

| | |
|---|---|
| **Type** | Class |
| **Key attributes** | `data_records: list[AttemptRecord]`, `category_stats: dict[str, CategoryStats]`, `_global_csv_path` |
| **Key methods** | `log_attempt()`, `start_case_timer()`, `end_case_timer()`, `response_time_s()`, `save_to_csv()`, `response_time_series()`, `accuracy_series()`, `category_counts()`, `stress_factor_correlation()`, `mean_std()`, `summary_rows()` |

---

### `ui.py`

#### `UIStrings`
A small frozen dataclass that holds all user-facing text strings for the application (currently the window title `"ICD-10 Code Blue"`). Centralizing strings this way makes it straightforward to rename or localize the app without hunting through layout code.

| | |
|---|---|
| **Type** | Frozen dataclass |
| **Attributes** | `title: str` |

#### `Palette`
A frozen dataclass that defines the complete color scheme of the application — background, panel, accent, border, and semantic colors (good/warn/bad). All widgets in `UI_Manager` reference this single object, so changing one value in `Palette` updates the entire UI consistently.

| | |
|---|---|
| **Type** | Frozen dataclass |
| **Key attributes** | `bg`, `panel`, `panel_2`, `text`, `muted`, `accent`, `border`, `good`, `warn`, `bad` |

#### `UI_Manager`
Builds and drives the complete Tkinter GUI. Responsible for three main screens: the **main menu** (username entry, play/quit buttons), the **gameplay screen** (symptom panel, ICD-10 code input field, handbook search panel with live results list, countdown timer bar, stability bar, score HUD, and submit/skip buttons), and the **post-game statistics dashboard** (category summary table and the five interactive charts rendered on a `tk.Canvas`). It holds a reference to `GameController` and polls it every second via a `tick()` loop to update the timer and stability bar in real time. It also triggers session CSV saving when a game ends.

| | |
|---|---|
| **Type** | Class |
| **Key attributes** | `root`, `controller`, `db_search`, `stats`, `data_dir`, `p` (Palette), `current_username` |
| **Key methods** | `show_menu()`, `start_game()`, `_build_gameplay_screen()`, `_tick()`, `_on_submit()`, `_on_skip()`, `_show_stats()`, `_draw_response_time_line()`, `_draw_accuracy_pie()`, `_draw_category_distribution()`, `_draw_response_time_box_plot()`, `_save_session_log()` |
| **Relationships** | Uses `GameController`, `StatsTracker`, and `ICD_Database` search; reads `GameState` to switch screens |

---

### Class Relationships Overview

```
app.py (run_app)
  └── wires all components → UI_Manager
        ├── uses ──────────────► GameController
        │                             ├── owns ──► GameConfig
        │                             ├── uses ──► ICD_Database ──loads──► ICDEntry
        │                             ├── uses ──► StatsTracker
        │                             │               ├── stores ──► AttemptRecord
        │                             │               └── stores ──► CategoryStats
        │                             └── creates ──► Patient
        │                                             (from PatientCase or ICD fallback)
        ├── uses ──────────────► StatsTracker (for chart data)
        ├── uses ──────────────► ICD_Database.search_code() (handbook search)
        └── owns ──────────────► Palette · UIStrings

cases.py: load_cases_csv() ──produces──► PatientCase ──fed into──► GameController.load_cases()
```
---

## 5. Statistical Data

### 5.1 Data Recording Method

Each game session records per-attempt data including the player's response time, the submitted code, the correct code, and whether the answer was correct or incorrect. This data is saved to a structured file (e.g., CSV or JSON) at the end of each session for later analysis and visualization.

### 5.2 Data Features

The following five graphs are generated from the recorded session data:

| # | Feature Name | Objective | Graph Type | X-axis | Y-axis |
|---|---|---|---|---|---|
| 1 | **Response Time Improvement** | Show how user speed improves over time | Line Graph | Attempt Number | Response Time (seconds) |
| 2 | **Error Distribution** | Show frequency of incorrect diagnoses | Histogram | Number of Errors per Attempt | Frequency |
| 3 | **Category Frequency** | Show how often each ICD-10 category appears | Bar Chart | ICD-10 Categories | Number of Occurrences |
| 4 | **Accuracy Rate** | Show proportion of correct vs incorrect answers | Pie Chart | Result Type (Correct / Incorrect) | Percentage (%) |
| 5 | **Response Time Distribution** | Show spread of response times across attempts | Box Plot | Attempts | Response Time (seconds) |

---

## 6. External Sources

### Data

- **World Health Organization (1993).** *The ICD-10 classification of mental and behavioural disorders: Diagnostic criteria for research.* World Health Organization.
  Source: [https://www.who.int/classifications/icd/en/](https://www.who.int/classifications/icd/en/)

### Libraries & Frameworks


| Library | Purpose | License |
|---------|---------|---------|
| `tkinter` | GUI framework for all screens and widgets | Python PSF (built-in) |
| `csv` | Reading ICD-10 dataset and writing session logs | Python PSF (built-in) |
| `pathlib` | Cross-platform file path handling | Python PSF (built-in) |
| `dataclasses` | Structured data containers (`Patient`, `ICDEntry`, etc.) | Python PSF (built-in) |
| `enum` | `GameState` enumeration | Python PSF (built-in) |
| `datetime` | UTC timestamps for attempt records and response timing | Python PSF (built-in) |
| `math` | Pearson correlation and standard deviation in `StatsTracker` | Python PSF (built-in) |
| `matplotlib` | Data visualization / statistics graphs | PSF-compatible (BSD) |
