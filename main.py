#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import requests
from pyjstat import pyjstat
import matplotlib.pyplot as plt
import seaborn as sns
import json

# ==========================
# 1. Chargement des données Eurostat
# ==========================
url_alcool = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_ehis_al1b?format=JSON'
url_pib = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tipsna40?format=JSON'
url_sante = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_hlye?format=JSON'

# Chargement des datasets
df_alcool = pyjstat.Dataset.read(requests.get(url_alcool).text).write('dataframe')
df_pib = pyjstat.Dataset.read(requests.get(url_pib).text).write('dataframe')
df_sante = pyjstat.Dataset.read(requests.get(url_sante).text).write('dataframe')

# Renommage des colonnes pour clarté
df_alcool = df_alcool.rename(columns={
    'Frequency': 'frequency',
    'Sex': 'sex',
    'Age class': 'age',
    'Country/region of birth': 'birth_country',
    'Geopolitical entity (reporting)': 'geo',
    'Time': 'time',
    'value': 'value'
})
df_pib = df_pib.rename(columns={
    'Geopolitical entity (reporting)': 'geo',
    'Time': 'time',
    'value': 'gdp_per_capita'
})
df_sante = df_sante.rename(columns={
    'Sex': 'sex',
    'Health indicator': 'health_indicator',
    'Geopolitical entity (reporting)': 'geo',
    'Time': 'time',
    'value': 'healthy_life_expectancy'
})

# ==========================
# 2. Filtrage & nettoyage des données
# ==========================

# ------ Consommation d'alcool ------
# Utilise les valeurs exactes du dataset !
freq_map = {
    'Every day': 'alcohol_daily_pct',
    'Every week': 'alcohol_weekly_pct',
    'Every month': 'alcohol_monthly_pct',
    'Never': 'alcohol_never_pct'
}
df_alcool_f = df_alcool[
    (df_alcool['age'] == 'Total') &  # population totale
    (df_alcool['birth_country'] == 'Reporting country') &  # natifs
    (df_alcool['frequency'].isin(list(freq_map.keys()))) &
    (df_alcool['time'].isin(['2014', '2019'])) &
    (~df_alcool['geo'].isin(['TR', 'Türkiye']))
].copy()

df_alcool_f['indicator'] = df_alcool_f['frequency'].map(freq_map)
df_alcool_pivot = df_alcool_f.pivot_table(
    index=['geo', 'time', 'sex'],
    columns='indicator',
    values='value'
).reset_index()

# ------ PIB par habitant ------
df_pib_f = df_pib[df_pib['time'].isin(['2014', '2019'])][['geo', 'time', 'gdp_per_capita']]

# ------ Années de vie en bonne santé ------
df_sante_f = df_sante[
    (df_sante['health_indicator'] == 'Healthy life years in absolute value at birth') &
    (df_sante['time'].isin(['2014', '2019'])) &
    (~df_sante['geo'].isin(['CH', 'Switzerland']))
][['geo', 'time', 'sex', 'healthy_life_expectancy']]

# ==========================
# 3. Jointure intelligente
# ==========================
merged = df_alcool_pivot.merge(df_pib_f, on=['geo', 'time'], how='left')
merged = merged.merge(df_sante_f, on=['geo', 'time', 'sex'], how='left')

# ==========================
# 4. Calculs d'indicateurs dérivés
# ==========================
merged['alcohol_consumption_index'] = (
    merged['alcohol_daily_pct'].fillna(0) * 1.0 +
    merged['alcohol_weekly_pct'].fillna(0) * 0.75 +
    merged['alcohol_monthly_pct'].fillna(0) * 0.5
)
merged['abstinence_rate'] = merged['alcohol_never_pct']
merged['health_per_gdp_ratio'] = merged['healthy_life_expectancy'] / merged['gdp_per_capita']

# Met les NaN en null pour le CSV (format FAIR)
merged = merged.where(pd.notnull(merged), None)

# ==========================
# 5. Export CSV propre
# ==========================
csv_name = "europe_alcool_sante.csv"
merged.to_csv(csv_name, index=False)
print(f"Fichier CSV généré avec succès : {csv_name}")

# ==========================
# 6. Visualisations (optionnelles)
# ==========================
def plot_scatter_gdp_vs_alcohol(df):
    plt.figure(figsize=(8,6))
    sns.scatterplot(data=df, x='gdp_per_capita', y='alcohol_consumption_index', hue='geo', style='sex')
    plt.title("Indice de consommation d'alcool vs PIB par habitant (Europe)")
    plt.xlabel("PIB par habitant (PPS)")
    plt.ylabel("Indice de consommation d'alcool")
    plt.tight_layout()
    plt.show()

def plot_scatter_alcohol_vs_health(df):
    plt.figure(figsize=(8,6))
    sns.scatterplot(data=df, x='alcohol_consumption_index', y='healthy_life_expectancy', hue='geo', style='sex')
    plt.title("Espérance de vie en bonne santé vs Indice de consommation d'alcool (Europe)")
    plt.xlabel("Indice de consommation d'alcool")
    plt.ylabel("Espérance de vie en bonne santé (années)")
    plt.tight_layout()
    plt.show()

def plot_heatmap_correlation(df):
    plt.figure(figsize=(8,6))
    corr = df[['gdp_per_capita','alcohol_consumption_index','healthy_life_expectancy']].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    plt.title("Corrélation entre PIB, consommation d'alcool et espérance de vie en bonne santé")
    plt.tight_layout()
    plt.show()

# ==========================
# 7. Génération des métadonnées FAIR
# ==========================
metadata = {
    "title": "Europe - Consommation d'alcool, PIB par habitant, et Espérance de vie en bonne santé (2014 & 2019)",
    "description": (
        "Analyse croisée entre la consommation d’alcool (population totale), le PIB par habitant (PPS) "
        "et les années de vie en bonne santé à la naissance, pour les pays européens, années 2014 & 2019. "
        "Données issues d’Eurostat. 1 ligne par pays, année, sexe."
    ),
    "sources": {
        "alcool": url_alcool,
        "pib": url_pib,
        "sante": url_sante
    },
    "columns": {
        "geo": "Code ISO du pays",
        "time": "Année (2014 ou 2019)",
        "sex": "Sexe (M = hommes, F = femmes, T = total)",
        "alcohol_daily_pct": "% de personnes buvant tous les jours (population totale, natifs)",
        "alcohol_weekly_pct": "% buvant au moins une fois par semaine",
        "alcohol_monthly_pct": "% buvant au moins une fois par mois",
        "alcohol_never_pct": "% ne buvant jamais",
        "gdp_per_capita": "PIB réel/habitant en parité de pouvoir d'achat (PPS)",
        "healthy_life_expectancy": "Nombre moyen d'années de vie en bonne santé à la naissance",
        "alcohol_consumption_index": "Indice synthétique (1× daily + 0,75× weekly + 0,5× monthly)",
        "abstinence_rate": "% de non-buveurs (identique à alcohol_never_pct)",
        "health_per_gdp_ratio": "Années de vie en bonne santé / PIB par habitant"
    },
    "license": "CC BY 4.0 (Eurostat - https://creativecommons.org/licenses/by/4.0/)",
    "exclusions": {
        "Turquie": "exclue du dataset alcool",
        "Suisse": "exclue du dataset santé"
    },
    "missing_values": "null (jamais 0 si valeur absente)",
    "reproducibility": "Extraction via le script Python fourni, totalement reproductible.",
    "date_generated": pd.Timestamp.today().strftime('%Y-%m-%d')
}
with open("europe_alcool_sante_metadata.json", "w", encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)
print("Fichier de métadonnées généré avec succès : europe_alcool_sante_metadata.json")

# ==========================
# 8. Utilisation des graphiques
# ==========================
# df = pd.read_csv(csv_name)
# plot_scatter_gdp_vs_alcohol(df)
# plot_scatter_alcohol_vs_health(df)
# plot_heatmap_correlation(df)
