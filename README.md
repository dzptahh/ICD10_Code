# 🏥 ICD10 Code Game

An educational Python game that challenges players to diagnose patients from symptoms and input the correct **ICD-10 medical code** — either from memory or by searching a built-in code handbook.

---

## 🎮 How to Play

1. A set of **clinical symptoms** is presented to the player.
2. The player determines the most likely **diagnosis**.
3. The player submits the matching **ICD-10 code** by either:
   - **Typing it directly** if they know the code.
   - **Searching the handbook** — a built-in fuzzy/keyword search that suggests close-matching ICD-10 codes.
4. Correct answers earn points. The game tracks your score across rounds.

---

## ✨ Features

- 🩺 Symptom-based diagnostic challenges
- ⌨️ Direct ICD-10 code input mode
- 🔍 Handbook search mode with near-match suggestions
- 📊 Score tracking
  
---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/dzptahh/ICD10_Code.git

# Navigate into the project directory
cd ICD10_Code

# Install dependencies
pip install -r requirements.txt
```

### Run the Game

```bash
python main.py
```

---

## 📁 Project Structure

```
ICD10_Code/
├── icd10_code_blue/
│   ├── app.py
│   ├── cases.py
│   ├── controller.py
│   ├── icd_database.py
│   ├── patient.py
│   ├── stats.py
│   └── ui.py
├── main.py               # Entry point of the game
├── data/
│   └── icd10_sample.csv  # ICD-10 code dataset
├── requirements.txt      # Python dependencies
├── README.md
└── LICENSE
```

> **Note:** File names above are illustrative. Refer to the actual repository structure for exact filenames.

---

## 🔍 Handbook Search

The handbook search feature lets players look up ICD-10 codes by entering a keyword or partial description (e.g., typing `"diabetes"` will return a list of relevant ICD-10 codes to choose from). This mirrors real-world clinical coding workflows.

---

## 📋 Requirements

See [`requirements.txt`](requirements.txt) for the full list of dependencies.

---


## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**dzptahh** — [github.com/dzptahh](https://github.com/dzptahh)
## Data

- `data/icd10_sample.csv`: small sample dataset (you can replace it with your own).

