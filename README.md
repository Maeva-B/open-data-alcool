# 🥂 Alcohol, Economy & Healthy Life Expectancy in Europe — What Correlation?

## 🎯 Topic

**Across Europe, how does alcohol consumption vary with GDP per capita, and what impact does this consumption have on healthy life years?**

This project investigates potential correlations between three public-health and macro-economic dimensions for European countries (2014 & 2019):

- Frequency of alcohol consumption  
- Real GDP per capita  
- Healthy life years at birth

---

## 🔗 Data Sources (Eurostat)

| Dimension | Eurostat dataset | API endpoint |
|-----------|------------------|--------------|
| Alcohol-consumption frequencies | `hlth_ehis_al1b` | <https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_ehis_al1b> |
| Real GDP per capita (PPS) | `tipsna40` | <https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tipsna40> |
| Healthy life years at birth | `hlth_hlye` | <https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_hlye> |

---

## ✅ FAIR-Principle Compliance

### 🔍 Findable
- Unique, persistent identifiers and rich metadata provided by Eurostat.  
- Dataset archived on Zenodo with DOI (see badge above).

### 📥 Accessible
- Fully open access via Eurostat’s REST API (no auth required).  
- Repository and Zenodo release include raw data, scripts & FAIR metadata.

### 🔗 Interoperable
- Standard, machine-readable formats (CSV + JSON; SDMX compatible).  
- Common European classifiers (ISO-2 country codes, PPS, etc.).

### 🔁 Reusable
- Licensed under **CC BY 4.0** (Eurostat licence).   
- Reproducible build pipeline (`main.py`, `cleaner.py`).

---

## 🚀 Quick Start

```bash
git clone https://github.com/Maeva-B/open-data-alcool.git
cd open-data-alcool
python main.py        # download + merge 
python cleaner.py   # deduplicate + rounding



## 📌 Authors

- Julie Dornat
- Maëva Burillo
- Julien Marty
- Matthieu Nanfack Kemtsop
- David Kalala Kabambi
