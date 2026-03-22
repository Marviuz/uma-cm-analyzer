# Project Roadmap: Umamusume CM Data Analyst (Open Source)

This document outlines the technical requirements for an open-source tool designed to analyze "Mock Run" data. The goal is to identify which stats and skills actually correlate with winning in a specific Champion's Meeting (CM) environment.

---

## 1. Project Objective
To provide a data-driven alternative to "vibe-based" team building. By inputting the results of 50–100 practice races, the tool will identify:
* **Stat Floors:** The minimum stamina/guts required to not "sink" before the finish.
* **Skill ROI:** Which specific gold/white skills are present in the top 3 finishers most consistently.
* **Meta Shifts:** Which strategies (front-runner, pace-chaser, late-surger, end-closer) are over-performing on the current track.

---

## 2. Technical Requirements

### 2.1 Core Features
* **CSV Ingestion:** A standardized parser to read race logs.
* **Skill Frequency Analysis:** Calculates the "Win Rate Contribution" of every skill found in the data.
* **Stat Correlation:** Uses Pearson correlation to see if higher $Wisdom$ or $Power$ actually resulted in better placements for that specific track.
* **Visual Reports:** Generates PNG/HTML charts for easy sharing on Discord or GitHub.

### 2.2 Data Validation
The tool must handle:
* Duplicate Race IDs (to prevent skewing data).
* Missing skill data (some runs might not log every white skill).
* Standardization of Umamusume names (e.g., "Kitasan Black" vs "Kitasan Black (New Year)").

---

## 3. Complete Data Structure (CSV Schema)

To make the analysis effective, the input CSV needs to be granular. Below is the mandatory schema for the open-source project.

### Header Definitions
* **Race_ID:** Unique identifier for the mock session.
* **Uma_Name:** The specific character used.
* **Strategy:** 1 (front-runner), 2 (pace-chaser), 3 (late-surger), 4 (end-closer).
* **Stats:** Integers (1–1600+).
* **Proper_S:** Boolean (1 if Distance/Surface/Track Aptitude is S, 0 if A).
* **Skills_List:** Semicolon-separated string of activated skills.
* **Rank:** Final placement (1–9).

### Sample CSV Content
```csv
Race_ID,Uma_Name,Strategy,Speed,Stamina,Power,Guts,Wisdom,Dist_S,Surface_S,Track_S,Skills_Activated,Rank,Distance_Diff
101,Kitasan Black,front-runner,1500,800,1100,900,1200,1,0,1,Angling_Scheming;Top_Runner;Arc_Maestro;Ahead_of_the_Pack,1,0.0
101,Grass Wonder,late-surger,1450,750,1200,800,1100,1,1,0,Non_Stop_Girl;Ogre;Swift_Sword,4,3.5
101,Mejiro Ardan,pace-chaser,1480,820,1050,850,1150,0,0,0,Speedy_Runner;決意の直滑降,2,1.5
102,Kitasan Black,front-runner,1500,800,1100,900,1200,1,0,1,Angling_Scheming;Top_Runner;Arc_Maestro,3,2.0
102,Rice Shower,end-closer,1400,900,1200,1000,1000,1,0,0,Cool_Down;Shadow_Break;Straight_Shot,1,0.0
```

---

## 4. Analysis Logic (The "Math" Layer)

### Skill Impact Score (SIS)
For each skill, the tool should calculate:
$$SIS = \frac{\text{Average Rank (Without Skill)} - \text{Average Rank (With Skill)}}{\text{Variance}}$$
* **Positive Score:** The skill significantly improves placement.
* **Negative Score:** The skill might be a "trap" or waste of Skill Points (SP) for this specific track.

### Stat Benchmarking
The tool should output a "Success Envelope":
* **Min Speed for Top 3:** $1450$
* **Avg Stamina for Finishers:** $820 \pm 40$

---

## 5. Development Roadmap
1.  **Phase 1:** Build the Python CLI tool that reads the CSV and prints a text summary.
2.  **Phase 2:** Integrate `Matplotlib` for box-plots showing $Rank$ vs. $Strategy$.
3.  **Phase 3:** Create a web-UI (Streamlit) where users drag-and-drop their CSV to get the report.
