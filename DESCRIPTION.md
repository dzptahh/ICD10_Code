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

  > 📸 *(Add your screenshots here — place image files in a `screenshots/` folder in the repo)*
  >
  > ```markdown
  > ![Gameplay Screenshot](screenshots/gameplay.png)
  > ![Statistics Dashboard](screenshots/stats_dashboard.png)
  > ```

- **Proposal:**
  📄 [View Project Proposal (PDF)](proposal.pdf)

- **YouTube Presentation:**
  🎥 *(Add your YouTube link here — approx. 7 minutes)*

  > The presentation covers:
  > 1. A short intro and full demonstration of the game and statistics features
  > 2. An explanation of the class design and its usage
  > 3. An explanation of the statistics and data visualizations

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

> 📎 *(UML Class Diagram will be added here)*
>
> The diagram will include:
> - All classes with attributes and methods
> - Relationships such as association and inheritance
>
> **Attachment:** [UML Class Diagram (PDF)](uml_class_diagram.pdf)

---

## 4. Object-Oriented Programming Implementation

> *(Placeholders — update with your actual class names and descriptions from your code)*

| Class | Description |
|-------|-------------|
| `Game` | Core game controller. Manages game flow, rounds, and scoring. |
| `Question` | Represents a single symptom-based challenge with its correct ICD-10 answer. |
| `Player` | Stores player name, current score, and session history. |
| `Handbook` | Handles the ICD-10 code dataset and provides search/lookup functionality. |
| `Statistics` | Processes recorded session data and generates performance graphs. |

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

## 6. Changed Proposed Features

> *(Skip for now — fill in here if any features differ from the original proposal)*

---

## 7. External Sources

### Data

- **World Health Organization (1993).** *The ICD-10 classification of mental and behavioural disorders: Diagnostic criteria for research.* World Health Organization.
  Source: [https://www.who.int/classifications/icd/en/](https://www.who.int/classifications/icd/en/)

### Libraries & Frameworks

> *(Update or remove rows based on the libraries you actually import)*

| Library | Purpose | License |
|---------|---------|---------|
| `rapidfuzz` | Fuzzy string matching for handbook search | MIT |
| `pandas` | Data handling and session recording | BSD-3-Clause |
| `matplotlib` | Data visualization / graphs | PSF |
| `rich` | Terminal UI and styled output | MIT |
| `colorama` | Cross-platform terminal color support | BSD |

### Other Assets

> *(Add any music, images, or artwork used here, with author name, source link, and license)*