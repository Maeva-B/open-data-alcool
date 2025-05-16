#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# =============== 1. Chargement des données ===============
df = pd.read_csv("europe_alcool_sante.csv")

# Nettoyage pour les graphes
df_graph = df.copy()
df_graph["year"] = df_graph["time"]

# =============== 2. Graphique 1 : PIB vs Alcool (avec noms) ===============
plt.figure(figsize=(10,7))
sns.scatterplot(data=df_graph, x="gdp_per_capita", y="alcohol_consumption_index", hue="sex", s=100)
for i, row in df_graph.iterrows():
    plt.text(row["gdp_per_capita"], row["alcohol_consumption_index"], str(row["geo"]), fontsize=8, alpha=0.8)
plt.title("PIB par habitant vs Indice de consommation d’alcool (chaque point = un pays)")
plt.xlabel("PIB par habitant (€)")
plt.ylabel("Indice de consommation d’alcool (pondéré)")
plt.legend(title="Sexe")
plt.tight_layout()
plt.savefig("1_pib_vs_alcool_annotated.png")
plt.close()

# =============== 3. Graphique 2 : PIB vs Santé ===============
plt.figure(figsize=(10,7))
sns.scatterplot(data=df_graph, x="gdp_per_capita", y="healthy_life_expectancy", hue="sex", s=100)
for i, row in df_graph.iterrows():
    plt.text(row["gdp_per_capita"], row["healthy_life_expectancy"], str(row["geo"]), fontsize=8, alpha=0.8)
plt.title("PIB par habitant vs Années de vie en bonne santé")
plt.xlabel("PIB par habitant (€)")
plt.ylabel("Années de vie en bonne santé")
plt.legend(title="Sexe")
plt.tight_layout()
plt.savefig("2_pib_vs_vie_saine_annotated.png")
plt.close()

# =============== 4. Graphique 3 : Alcool vs Santé ===============
plt.figure(figsize=(10,7))
sns.scatterplot(data=df_graph, x="alcohol_consumption_index", y="healthy_life_expectancy", hue="sex", s=100)
for i, row in df_graph.iterrows():
    plt.text(row["alcohol_consumption_index"], row["healthy_life_expectancy"], str(row["geo"]), fontsize=8, alpha=0.8)
plt.title("Indice de consommation d’alcool vs Années de vie en bonne santé")
plt.xlabel("Indice de consommation d’alcool")
plt.ylabel("Années de vie en bonne santé")
plt.legend(title="Sexe")
plt.tight_layout()
plt.savefig("3_alcool_vs_vie_saine_annotated.png")
plt.close()

# =============== 5. Graphique 4 : Evolution 2014-2019 par pays (alcool) ===============
diff = df_graph.pivot_table(index=['geo', 'sex'], columns='year', values=['alcohol_consumption_index', 'healthy_life_expectancy', 'gdp_per_capita'])
diff = diff.dropna()  # On garde que les pays/sexes avec les deux années

# Indice d’alcool
if 2014 in diff["alcohol_consumption_index"] and 2019 in diff["alcohol_consumption_index"]:
    evol_alcool = diff["alcohol_consumption_index"][2019] - diff["alcohol_consumption_index"][2014]
    evol_alcool = evol_alcool.sort_values()
    plt.figure(figsize=(12,8))
    evol_alcool.plot(kind="barh", color=np.where(evol_alcool>0, 'g', 'r'))
    plt.title("Évolution de l'indice d’alcool 2014→2019 (par pays et sexe)")
    plt.xlabel("Variation de l'indice (2019 - 2014)")
    plt.ylabel("Pays - Sexe")
    plt.tight_layout()
    plt.savefig("4_evol_alcool_2014_2019.png")
    plt.close()

# Santé
if 2014 in diff["healthy_life_expectancy"] and 2019 in diff["healthy_life_expectancy"]:
    evol_sante = diff["healthy_life_expectancy"][2019] - diff["healthy_life_expectancy"][2014]
    evol_sante = evol_sante.sort_values()
    plt.figure(figsize=(12,8))
    evol_sante.plot(kind="barh", color=np.where(evol_sante>0, 'b', 'orange'))
    plt.title("Évolution des années de vie en bonne santé 2014→2019")
    plt.xlabel("Variation (années)")
    plt.ylabel("Pays - Sexe")
    plt.tight_layout()
    plt.savefig("5_evol_sante_2014_2019.png")
    plt.close()

# =============== 6. Graphique 5 : Top 10 abstinence ===============
abstinence = df_graph.groupby(["geo", "sex"])["abstinence_rate"].mean().reset_index()
top10 = abstinence.sort_values("abstinence_rate", ascending=False).head(10)
plt.figure(figsize=(10,7))
ax = sns.barplot(data=top10, y="geo", x="abstinence_rate", hue="sex", orient="h")
for container in ax.containers:
    ax.bar_label(container, fmt="%.1f")
plt.title("Top 10 pays européens - Taux d’abstinence le plus élevé")
plt.xlabel("Taux d’abstinence (%)")
plt.ylabel("Pays")
plt.tight_layout()
plt.savefig("6_top10_abstinence_horizontal.png")
plt.close()

# =============== 7. Graphe combiné à 3 variables (bulle) ===============
plt.figure(figsize=(12,8))
sizes = (df_graph["healthy_life_expectancy"] - df_graph["healthy_life_expectancy"].min() + 1) * 15
sns.scatterplot(
    data=df_graph, x="gdp_per_capita", y="alcohol_consumption_index",
    size="healthy_life_expectancy", hue="sex", alpha=0.7, sizes=(40, 400), legend="brief"
)
for i, row in df_graph.iterrows():
    plt.text(row["gdp_per_capita"], row["alcohol_consumption_index"], str(row["geo"]), fontsize=8, alpha=0.7)
plt.title("PIB/hab vs Indice d’alcool (taille = années de vie en bonne santé)")
plt.xlabel("PIB par habitant (€)")
plt.ylabel("Indice d’alcool")
plt.tight_layout()
plt.savefig("7_bulle_pib_alcool_sante.png")
plt.close()

# =============== 8. Heatmap pays/année ===============
pivot = df_graph.pivot_table(index="geo", columns="year", values="alcohol_consumption_index")
plt.figure(figsize=(12,10))
sns.heatmap(pivot, annot=True, cmap="coolwarm", fmt=".1f")
plt.title("Indice d’alcool par pays (2014 vs 2019)")
plt.ylabel("Pays")
plt.xlabel("Année")
plt.tight_layout()
plt.savefig("8_heatmap_alcool_pays.png")
plt.close()

# =============== 9. (Optionnel) Carte interactive (Plotly) ===============
try:
    import plotly.express as px
    heatmap_data = df_graph.groupby('geo').agg({'health_per_gdp_ratio':'mean'}).reset_index()
    fig = px.choropleth(
        heatmap_data, locations="geo", color="health_per_gdp_ratio",
        locationmode="ISO-3", color_continuous_scale="Viridis",
        title="Santé ajustée au PIB par pays"
    )
    fig.write_html("9_health_per_gdp_ratio_map.html")
    print("Carte interactive générée : 9_health_per_gdp_ratio_map.html")
except ImportError:
    print("Plotly non installé, carte non générée.")

print("Tous les graphes ont été générés.")

# =============== 10. Génération PDF (avec fpdf) ===============
from fpdf import FPDF

# Liste des images à inclure (adapte si besoin)
images = [
    "1_pib_vs_alcool_annotated.png",
    "2_pib_vs_vie_saine_annotated.png",
    "3_alcool_vs_vie_saine_annotated.png",
    "4_evol_alcool_2014_2019.png",
    "5_evol_sante_2014_2019.png",
    "6_top10_abstinence_horizontal.png",
    "7_bulle_pib_alcool_sante.png",
    "8_heatmap_alcool_pays.png"
    # "9_health_per_gdp_ratio_map.html"  # La carte interactive est en HTML
]

pdf = FPDF(orientation='L', unit='mm', format='A4')
pdf.set_auto_page_break(auto=True, margin=15)

for img in images:
    if os.path.exists(img):
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, img.replace("_", " ").replace(".png", ""), 0, 1, "C")
        pdf.image(img, x=10, y=30, w=270)  # w=270 pour bien occuper la page A4 paysage

pdf.output("rapport_graphes_europe.pdf")
print("PDF généré : rapport_graphes_europe.pdf")
