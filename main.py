import pandas as pd
import requests
from pyjstat import pyjstat


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
# --------------------------------------------


# Renommer pour simplifier les traitements
df_pib.columns = ['freq', 'unit', 'indicator', 'geo', 'time', 'value']

# Filtrage : années 2014 & 2019, exclusion TR et CH
df_pib_filtered = df_pib[
    df_pib["time"].isin(["2014", "2019"])
]


# ----

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


# ----

# Nettoyage et renommage des colonnes sante

print("Colonnes disponibles :", df_sante.columns)

df_sante.columns = [
    'freq', 'unit', 'sex', 'health_indicator', 'geo', 'time', 'value'
]

df_sante_filtered = df_sante[
    df_sante["time"].isin(["2014", "2019"]) &
    ~df_sante["geo"].isin(["Switzerland"])
]


# Définition du modèle
class Indicateurs:
    def __init__(self, pib_par_habitant, freq_semaine_alcool, freq_mois_alcool, esperance_bonne_sante):
        self.pib_par_habitant = pib_par_habitant # gdp_per_capita
        self.freq_mois_alcool = freq_mois_alcool
        self.esperance_bonne_sante = esperance_bonne_sante
        pass

class Instances:
    def __init__(self, annee, pays, sexe):
        self.annee = annee
        self.pays = pays
        self.sexe = sexe
        pass

# indice_consommation_global_alcool, taux_abstinence, ratio_sante_pib
class Indicateurs_derives : 
    def __init__(self, indice_consommation_global_alcool, taux_abstinence, ratio_sante_pib):
        self.indice_consommation_global_alcool = indice_consommation_global_alcool
        self.taux_abstinence = taux_abstinence
        self.ratio_sante_pib = ratio_sante_pib
        pass



# TODO


# Pour affichage 
# print(df_pib_filtered.head())
# print(df_alcool_filtered.head())
# print(df_sante_filtered.head())