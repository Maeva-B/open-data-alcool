# 📊 Europe Alcohol–Economy–Health Analysis Toolkit

A suite of three Python scripts to **download**, **clean**, and **visualize** Eurostat data on alcohol-consumption frequencies, GDP per capita, and healthy life expectancy (2014 & 2019).

---

## 🗂 Repository Layout

```
.
├── main.py         # Download & merge raw Eurostat JSON datasets
├── cleaner.py      # Deduplicate, round, and export a “CLEAN” CSV
└── viewer.py       # Filter, plot, and export FAIR-compliant graphs
```

## ✅ Prerequisites

- Python 3.x

Install dependencies:

```bash
pip install pandas requests pyjstat matplotlib seaborn
```

---

## 1️⃣ `main.py` — Download & Merge

### 🎯 Purpose

- Query three Eurostat APIs:
  - `hlth_ehis_al1b`
  - `tipsna40`
  - `hlth_hlye`
- Convert JSON → pandas DataFrame via `pyjstat`
- Rename columns to `geo`, `time`, `sex`, `frequency`, `value` (or `gdp_per_capita`, `healthy_life_expectancy`)
- Filter to years **2014** & **2019**
- Pivot alcohol-frequency levels into separate columns
- Left-merge:
  - Alcohol × GDP on (`geo`, `time`)
  - Result × Health on (`geo`, `time`, `sex`)
- Export:
  - `europe_alcohol_allfrequencies_2014_2019.csv`
  - `europe_alcohol_allfrequencies_2014_2019_metadata.json`

### ▶️ Run

```bash
python main.py
```

---

## 2️⃣ `cleaner.py` — Deduplicate & Round

### 🎯 Purpose

- Load the raw CSV produced by `main.py`
- Group by (`geo`, `time`, `sex`) and average duplicates
- Round all `_pct` columns to one decimal
- Export cleaned dataset:
  - `europe_alcohol_allfrequencies_2014_2019_CLEAN.csv`

### ▶️ Run

```bash
python cleaner.py
```

---

## 3️⃣ `viewer.py` — Filter & Visualize

### 🎯 Purpose

- Load the cleaned CSV
- Print available options for:
  - Sex (Females / Males / Total)
  - Year (2014 / 2019)
  - Alcohol frequency (`alcohol_*_pct` columns)
- User sets three indices:

```python
sex_idx = 2    # 0=Females, 1=Males, 2=Total
time_idx = 1   # 0=2014, 1=2019
alc_idx = 2    # index into the list of alcohol_*_pct columns
```

- Filter DataFrame accordingly
- Generate three high-resolution plots:
  - Scatter: Alcohol consumption vs GDP per capita
  - Scatter: Healthy life expectancy vs Alcohol consumption
  - Heatmap: Correlation matrix (GDP, alcohol, health)
- FAIR export:
  - Save each figure under `graphs/` as `.png` with descriptive filenames (filters & date)
  - Optionally write accompanying `.txt` metadata files

### ▶️ Run

```bash
python viewer.py
```

---

## ⚡ Quick Workflow

1. **Download & merge raw data**

```bash
python main.py
```

2. **Clean & export deduplicated CSV**

```bash
python cleaner.py
```

3. **Filter & generate FAIR-ready graphs**

```bash
python viewer.py
```

---

## 👥 Authors

- Julie Dornat  
- Maëva Burillo  
- Julien Marty  
- Matthieu Nanfack Kemtsop  
- David Kalala Kabambi  

All scripts are designed for reproducibility, open formats, and full FAIR compliance.
