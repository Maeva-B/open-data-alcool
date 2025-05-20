import pandas as pd

df = pd.read_csv("../data/europe_alcohol_allfrequencies_2014_2019_CLEAN.csv")

import os
from datetime import date

# Create the output folder if it doesn't exist
output_dir = "../graphs"
os.makedirs(output_dir, exist_ok=True)



# Show available options in your data
print("Available 'sex' options:", df['sex'].unique())
print("Available 'time' (year) options:", df['time'].unique())
alcohol_columns = [col for col in df.columns if 'alcohol_' in col and '_pct' in col]
print("Available 'alcohol_col' options:", alcohol_columns)

# Select the desired option using an index:
sex_idx = 2     # 0 = 'Females', 1 = 'Males', 2 = 'Total'
time_idx = 1    # 0 = 2014, 1 = 2019
alc_idx = 2     # Pick among alcohol_columns

sex_choice = df['sex'].unique()[sex_idx]
time_choice = df['time'].unique()[time_idx]
alcohol_col = alcohol_columns[alc_idx]

# Filter according to your choices
df = df[(df['sex'] == sex_choice) & (df['time'] == time_choice)]

# Useful string for file names
filters_str = f"{sex_choice}_{time_choice}_{alcohol_col}_{date.today()}".replace(" ", "_")

print(f"Filtering: sex = {sex_choice}, year = {time_choice}, alcohol frequency = {alcohol_col}")
print(f"Rows after filtering: {len(df)}")
print(df.head())

import matplotlib.pyplot as plt
import seaborn as sns

# English labels for alcohol consumption frequencies
EN_LABELS = {
    'alcohol_every_day_pct': "Every day",
    'alcohol_every_month_pct': "At least once a month",
    'alcohol_every_week_pct': "At least once a week",
    'alcohol_less_than_once_a_month_pct': "Less than once a month",
    'alcohol_never_or_not_in_the_last_12_months_pct': "Never or not in the last 12 months",
    'alcohol_never_pct': "Never",
    'alcohol_not_in_the_last_12_months_pct': "Not in the last 12 months",
}

# Dynamic display variables
freq_label = EN_LABELS.get(alcohol_col, alcohol_col)
title_year = time_choice
title_sex = {"Females": " (Females)", "Males": " (Males)", "Total": " (Total)"}[sex_choice]

# 1. Scatterplot: Alcohol consumption (%) vs GDP per capita
plt.figure(figsize=(10,7))
sns.regplot(
    data=df,
    x='gdp_per_capita',
    y=alcohol_col,
    scatter_kws={'s':70},
    line_kws={'color':'red'},
    ci=None
)
for i, row in df.iterrows():
    plt.text(row['gdp_per_capita'], row[alcohol_col], row['geo'], fontsize=9, alpha=0.6)

plt.title(f"Alcohol consumption ({freq_label}) vs GDP per capita (Europe, {title_year}){title_sex}")
plt.xlabel("GDP per capita (PPS)")
plt.ylabel(f"Alcohol consumption (% of population, {freq_label})")
plt.tight_layout()
# SAVE FAIR
file1 = os.path.join(output_dir, f"scatter_alcohol_vs_gdp_{filters_str}.png")
plt.savefig(file1, dpi=300)
plt.show()

# 2. Scatterplot: Alcohol consumption (%) vs Healthy life expectancy
plt.figure(figsize=(10,7))
sns.regplot(
    data=df,
    x=alcohol_col,
    y='healthy_life_expectancy',
    scatter_kws={'s':70},
    line_kws={'color':'red'},
    ci=None
)
for i, row in df.iterrows():
    plt.text(row[alcohol_col], row['healthy_life_expectancy'], row['geo'], fontsize=9, alpha=0.6)

plt.title(f"Healthy life expectancy vs Alcohol consumption ({freq_label}) (Europe, {title_year}){title_sex}")
plt.xlabel(f"Alcohol consumption (% of population, {freq_label})")
plt.ylabel("Healthy life expectancy (years)")
plt.tight_layout()
# SAVE FAIR
file2 = os.path.join(output_dir, f"scatter_health_vs_alcohol_{filters_str}.png")
plt.savefig(file2, dpi=300)
plt.show()

# 3. Quick correlation matrix (GDP, alcohol, healthy life expectancy)
plt.figure(figsize=(7,5))
corr = df[['gdp_per_capita', alcohol_col, 'healthy_life_expectancy']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.title(f"Correlation between GDP, alcohol ({freq_label}), and healthy life expectancy")
plt.tight_layout()
# SAVE FAIR
file3 = os.path.join(output_dir, f"correlation_matrix_{filters_str}.png")
plt.savefig(file3, dpi=300)
plt.show()

for filename, description in [
    (file1, "Scatterplot: Alcohol consumption vs GDP per capita"),
    (file2, "Scatterplot: Healthy life expectancy vs Alcohol consumption"),
    (file3, "Correlation matrix (GDP, alcohol, healthy life expectancy)")
]:
    meta_path = filename.replace(".png", ".txt")
    with open(meta_path, "w") as f:
        f.write(f"Title: {description}\n")
        f.write(f"Filters: sex={sex_choice}, year={time_choice}, alcohol_col={alcohol_col}\n")
        f.write(f"Generated on: {date.today()}\n")
        f.write(f"File: {os.path.basename(filename)}\n")
        f.write(f"FAIR Compliance: Open format, descriptive filename, reproducible script.\n")

