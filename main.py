import pandas as pd
import requests
from pyjstat import pyjstat
import matplotlib.pyplot as plt


# URL des datasets (format JSON-stat 2.0) - Chargement des données Eurostat
url_alcool = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_ehis_al1b?format=JSON'
url_pib = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tipsna40?format=JSON'
url_sante = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_hlye?format=JSON'


# Consommation d'alcool (non traité ici pour l’instant)
response_alcool = requests.get(url_alcool)
dataset_alcool = pyjstat.Dataset.read(response_alcool.text)
df_alcool = dataset_alcool.write('dataframe')

# PIB réel par habitant
response_pib = requests.get(url_pib)
dataset_pib = pyjstat.Dataset.read(response_pib.text)
df_pib = dataset_pib.write('dataframe')

# Années de vie en bonne santé (non traité ici pour l’instant)
response_sante = requests.get(url_sante)
dataset_sante = pyjstat.Dataset.read(response_sante.text)
df_sante = dataset_sante.write('dataframe')


# --------------------------------------------
# Nettoyage et renommage des colonnes du PIB
# Renommer pour simplifier les traitements
df_pib.columns = ['freq', 'unit', 'indicator', 'geo', 'time', 'value']
# Filtrage : années 2014 & 2019, exclusion TR et CH
df_pib_filtered = df_pib[
    df_pib["time"].isin(["2014", "2019"])
]

# --------------------------------------------
# Nettoyage et renommage des colonnes du Alcool
# Renommage pour simplifier
df_alcool.columns = [
    'freq', 'unit', 'frequency', 'sex', 'age', 'birth_country', 'geo', 'time', 'value'
]
# Filtrage : années 2014 & 2019, exclusion TR (Turquie)
df_alcool_filtered = df_alcool[
    df_alcool["time"].isin(["2014", "2019"]) &
    ~df_alcool["geo"].isin(["Türkiye"])
]

# Nettoyage et renommage des colonnes sante
df_sante.columns = [
    'freq', 'unit', 'sex', 'health_indicator', 'geo', 'time', 'value'
]
df_sante_filtered = df_sante[
    df_sante["time"].isin(["2014", "2019"]) &
    ~df_sante["geo"].isin(["Switzerland"])
]


# 1) Fetch & standardize the three datasets (as you already do) …
#    → yields df_pib_filtered, df_alcool_filtered, df_sante_filtered

# --- select & rename just the columns we need ---
# GDP
df_gdp = ( df_pib_filtered
    .loc[:, ['geo','time','value']]
    .rename(columns={'value':'gdp_per_capita'})
    # convert types
    .assign(time = lambda d: d['time'].astype(int),
            gdp_per_capita = lambda d: pd.to_numeric(d['gdp_per_capita'], errors='coerce'))
)
print("df_gdp : \n", df_gdp.head().to_string(index=False))

# Alcohol (“Every day” / total population)
df_alc_daily_consumption = (df_alcool_filtered
                            .query("frequency == 'Every day' and sex == 'Total' and age == 'Total'")
                            .loc[:, ['geo','time','value']]
                            .rename(columns={'value':'alc_everyday_pct'})
                            .assign(time = lambda d: d['time'].astype(int),
            alc_everyday_pct = lambda d: pd.to_numeric(d['alc_everyday_pct'], errors='coerce'))
                            )
print("df_alc : \n", df_alc_daily_consumption.head().to_string(index=False))

# Healthy life years at birth (total population)
df_healthy_life_years = ( df_sante_filtered
    .query("health_indicator == 'Healthy life years in absolute value at birth' and sex == 'Total'")
    .loc[:, ['geo','time','value']]
    .rename(columns={'value':'hlye_at_birth'})
    .assign(time = lambda d: d['time'].astype(int),
            hlye_at_birth = lambda d: pd.to_numeric(d['hlye_at_birth'], errors='coerce'))
)
print("df_hlye : \n", df_healthy_life_years.head().to_string(index=False))

# 2) Merge them all on country & year
df_master = ( df_gdp
    .merge(df_alc_daily_consumption, on=['geo','time'], how='inner')
    .merge(df_healthy_life_years, on=['geo','time'], how='inner')
)

print("df_master : \n", df_master.head().to_string(index=False))


fig, axes = plt.subplots(2, 2, figsize=(14,6))
ax1, ax2, ax3 = axes[0,0], axes[0,1], axes[1,0]

for yr in df_master['time'].unique():
    sub = df_master[df_master['time'] == yr]
    ax1.scatter(sub['alc_everyday_pct'], sub['gdp_per_capita'], label=str(yr))
    ax2.scatter(sub['alc_everyday_pct'], sub['hlye_at_birth'], label=str(yr))
    ax3.scatter(sub['gdp_per_capita'], sub['hlye_at_birth'], label=str(yr))

ax1.set_xlabel("Daily Alcohol Consumption (%)")
ax1.set_ylabel("GDP per Capita (EUR)")
ax1.set_title("Alcohol vs. GDP")

ax2.set_xlabel("Daily Alcohol Consumption (%)")
ax2.set_ylabel("Healthy Life Expectancy (years)")
ax2.set_title("Alcohol vs. Healthy Life Exp.")

ax3.set_ylabel("GDP per Capita (EUR)")
ax3.set_ylabel("Healthy Life Expectancy (years)")
ax3.set_title("GPD vs. Healthy Life Exp.")

# share the same legend
fig.legend(title="Year", loc='upper right')
fig.tight_layout()
plt.show()
