import pandas as pd

# Load the generated file
input_file = "../data/europe_alcohol_allfrequencies_2014_2019.csv"
output_file = "../data/europe_alcohol_allfrequencies_2014_2019_CLEAN.csv"

df = pd.read_csv(input_file)

# Identify key columns (excluding value columns)
id_cols = ['geo', 'time', 'sex']
val_cols = [col for col in df.columns if col not in id_cols]

# Remove duplicates
# If numeric values differ for the same triplet (geo, time, sex), take the average (this shouldn't normally happen, but it's a safe approach!)
df_clean = df.groupby(id_cols, as_index=False)[val_cols].mean()

# (Optional) Round percentage values to one decimal place
for col in df_clean.columns:
    if col.startswith('alcohol_') and col.endswith('_pct'):
        df_clean[col] = df_clean[col].round(1)

# Export the clean CSV
df_clean.to_csv(output_file, index=False)
print(f"Clean file successfully generated: {output_file}")
print(f"Final row count: {len(df_clean)}")
