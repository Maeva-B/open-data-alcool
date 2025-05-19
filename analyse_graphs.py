import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Chargement des données
df = pd.read_csv("europe_alcool_graph_ready.csv")

# On filtre sur une année, par exemple 2019 et sexe "Total" (pour un graphe lisible)
df_plot = df[(df["year"] == 2019) & (df["sex"].str.lower().str.startswith("t"))]

plt.figure(figsize=(13, 9))
sns.set(style="whitegrid")

scatter = sns.scatterplot(
    data=df_plot,
    x="gdp_per_capita",
    y="alcohol_consumption_index",
    size="healthy_life_expectancy",
    sizes=(100, 700),
    hue="abstinence_rate",  # Couleur = taux d'abstinence, plus c'est élevé, plus c'est bleu
    palette="Blues",
    legend="brief"
)

# Annoter chaque point avec le code pays
for i, row in df_plot.iterrows():
    plt.text(
        row["gdp_per_capita"],
        row["alcohol_consumption_index"],
        row["geo"],
        fontsize=10,
        ha='left',
        va='center'
    )

plt.title("Europe 2019 — Indice synthétique d’alcool vs PIB/hab.\n(Taille: années de vie en bonne santé, Couleur: taux d’abstinence)")
plt.xlabel("PIB par habitant (PPS, €)")
plt.ylabel("Indice synthétique de consommation d’alcool")
plt.tight_layout()
plt.legend(title="Taux d'abstinence (%)", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.savefig("explicite_scatter_pib_alcool_abstinence.png", dpi=150)
plt.show()
