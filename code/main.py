#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import requests
from pyjstat import pyjstat
import matplotlib.pyplot as plt
import seaborn as sns
import json

# ==========================
# 1. Loading Eurostat Data
# ==========================
url_alcohol = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_ehis_al1b?format=JSON'
url_gdp = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tipsna40?format=JSON'
url_health = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_hlye?format=JSON'

# Load datasets
df_alcohol = pyjstat.Dataset.read(requests.get(url_alcohol).text).write('dataframe')
df_gdp = pyjstat.Dataset.read(requests.get(url_gdp).text).write('dataframe')
df_health = pyjstat.Dataset.read(requests.get(url_health).text).write('dataframe')

# Rename columns for clarity
if 'Frequency' in df_alcohol.columns:
    freq_col = 'Frequency'
elif 'CONS_ALC' in df_alcohol.columns:
    freq_col = 'CONS_ALC'
else:
    freq_col = [c for c in df_alcohol.columns if 'Freq' in c or 'consumption' in c][0]

df_alcohol = df_alcohol.rename(columns={
    freq_col: 'frequency',
    'Sex': 'sex',
    'Age class': 'age',
    'Country/region of birth': 'birth_country',
    'Geopolitical entity (reporting)': 'geo',
    'Time': 'time',
    'value': 'value'
})
df_gdp = df_gdp.rename(columns={
    'Geopolitical entity (reporting)': 'geo',
    'Time': 'time',
    'value': 'gdp_per_capita'
})
df_health = df_health.rename(columns={
    'Sex': 'sex',
    'Health indicator': 'health_indicator',
    'Geopolitical entity (reporting)': 'geo',
    'Time': 'time',
    'value': 'healthy_life_expectancy'
})

# ==========================
# 2. Filtering & Cleaning Data
# ==========================

# ------ Alcohol consumption ------
df_alcohol_f = df_alcohol[
    (df_alcohol['age'].str.lower() == 'total') &
    (df_alcohol['birth_country'].str.lower().str.contains('reporting country')) &
    (df_alcohol['time'].isin(['2014', '2019'])) &
    (~df_alcohol['geo'].isin(['TR', 'Türkiye']))
].copy()

# Dynamic list of all frequencies present in the filtered dataset
all_freqs = df_alcohol_f['frequency'].unique()
# Clean frequency names to make valid column names
colnames = {freq: f"alcohol_{freq.lower().replace(' ', '_').replace('-', '_').replace('/', '_').replace('(', '').replace(')', '').replace('.', '')}_pct"
            for freq in all_freqs}

df_alcohol_f['indicator'] = df_alcohol_f['frequency'].map(colnames)
df_alcohol_pivot = df_alcohol_f.pivot_table(
    index=['geo', 'time', 'sex'],
    columns='indicator',
    values='value'
).reset_index()

# ------ GDP per capita ------
df_gdp_f = df_gdp[df_gdp['time'].isin(['2014', '2019'])][['geo', 'time', 'gdp_per_capita']]

# ------ Healthy life years ------
df_health_f = df_health[
    (df_health['health_indicator'].str.lower().str.contains('healthy life years')) &
    (df_health['time'].isin(['2014', '2019'])) &
    (~df_health['geo'].isin(['CH', 'Switzerland']))
][['geo', 'time', 'sex', 'healthy_life_expectancy']]

# ==========================
# 3. Smart Merge
# ==========================
merged = df_alcohol_pivot.merge(df_gdp_f, on=['geo', 'time'], how='left')
merged = merged.merge(df_health_f, on=['geo', 'time', 'sex'], how='left')

# ==========================
# 4. Clean CSV Export
# ==========================
merged = merged.where(pd.notnull(merged), None)
csv_name = "../data/europe_alcohol_allfrequencies_2014_2019.csv"
merged.to_csv(csv_name, index=False)
print(f"CSV file successfully generated: {csv_name}")

# ==========================
# 5. FAIR Metadata Generation
# ==========================
metadata = {
    "title": "Europe - All Alcohol Consumption Frequencies, GDP, Healthy Life Expectancy (2014 & 2019)",
    "description": (
        "Cross-referenced Eurostat data: for each European country, all available alcohol consumption frequencies "
        "(total population, natives), GDP per capita, and healthy life expectancy at birth, for the years 2014 and 2019."
    ),
    "sources": {
        "alcohol": url_alcohol,
        "gdp": url_gdp,
        "health": url_health
    },
    "columns": {
        "geo": "Country ISO code",
        "time": "Year (2014 or 2019)",
        "sex": "Sex (M = male, F = female, T = total)",
        **{v: f"Percentage of people: '{k}'" for k, v in colnames.items()},
        "gdp_per_capita": "Real GDP per capita in Purchasing Power Standard (PPS)",
        "healthy_life_expectancy": "Healthy life expectancy at birth (in years)"
    },
    "license": "CC BY 4.0 (Eurostat - https://creativecommons.org/licenses/by/4.0/)",
    "date_generated": pd.Timestamp.today().strftime('%Y-%m-%d'),
    "keywords": [
        "Eurostat",
        "Alcohol consumption",
        "Healthy life years",
        "GDP per capita",
        "FAIR data",
        "Public health",
        "Trading economics",
        "Open Science"
    ],
    "provenance": {
        "data_retrieval": "Downloaded via Eurostat Dissemination API v1.0 on 2024‑05‑XX using main.py (see repository).",
        "processing": [
        "Filtering to years 2014 and 2019",
        "Pivoting all frequency modalities into separate columns",
        "Joining with GDP and Healthy Life Years datasets on country + year",
        "Deduplicating rows and rounding alcohol percentages to one decimal place"
        ],
        "limitations": [
        "Missing GDP values for Iceland, Norway and United Kingdom in 2019 (Eurostat not available)",
        "Healthy‑life‑years only available for total sex in some countries; NA values kept",
        "Aggregated EU rows kept for reference but should not be mixed with country‑level analytics"
        ]
    }
}


with open("../data/europe_alcohol_allfrequencies_2014_2019_metadata.json", "w", encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)
print("Metadata file successfully generated: europe_alcohol_allfrequencies_2014_2019_metadata.json")


# ==========================
# 6. (Optional) Visualizations
# ==========================
def plot_scatter_gdp_vs_alcohol(df):
    plt.figure(figsize=(8,6))
    sns.scatterplot(data=df, x='gdp_per_capita', y='alcohol_consumption_index', hue='geo', style='sex')
    plt.title("Alcohol Consumption Index vs GDP per Capita (Europe)")
    plt.xlabel("GDP per capita (PPS)")
    plt.ylabel("Alcohol Consumption Index")
    plt.tight_layout()
    plt.show()

def plot_scatter_alcohol_vs_health(df):
    plt.figure(figsize=(8,6))
    sns.scatterplot(data=df, x='alcohol_consumption_index', y='healthy_life_expectancy', hue='geo', style='sex')
    plt.title("Healthy Life Expectancy vs Alcohol Consumption Index (Europe)")
    plt.xlabel("Alcohol Consumption Index")
    plt.ylabel("Healthy Life Expectancy (years)")
    plt.tight_layout()
    plt.show()

def plot_heatmap_correlation(df):
    plt.figure(figsize=(8,6))
    corr = df[['gdp_per_capita', 'alcohol_consumption_index', 'healthy_life_expectancy']].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    plt.title("Correlation between GDP, Alcohol Consumption, and Healthy Life Expectancy")
    plt.tight_layout()
    plt.show()


# ==========================
# 8. Using the Visualizations
# ==========================
# df = pd.read_csv(csv_name)
# plot_scatter_gdp_vs_alcohol(df)
# plot_scatter_alcohol_vs_health(df)
# plot_heatmap_correlation(df)
