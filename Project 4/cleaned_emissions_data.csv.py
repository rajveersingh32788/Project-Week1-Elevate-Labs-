import pandas as pd

# 1. Load the dataset directly from Our World in Data (GitHub)
url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
df = pd.read_csv(url)

# 2. Filter for recent years (e.g., 2000-2023) and remove aggregate regions (like 'World')
# We only want actual countries for the map
continents = ['Africa', 'Asia', 'Europe', 'North America', 'South America', 'Oceania', 'Antarctica', 'World', 'European Union (27)']
df_countries = df[~df['country'].isin(continents)].copy()

# 3. Select relevant columns for the objective
cols_to_keep = [
    'country', 'year', 'iso_code', 'population', 'gdp',
    'co2', 'co2_per_capita', 'co2_per_gdp', 
    'coal_co2', 'oil_co2', 'gas_co2', 'cement_co2', 'flaring_co2'
]
df_final = df_countries[cols_to_keep].dropna(subset=['co2'])

# 4. Fill missing sector data with 0 (assuming no emissions if data is absent)
sector_cols = ['coal_co2', 'oil_co2', 'gas_co2', 'cement_co2', 'flaring_co2']
df_final[sector_cols] = df_final[sector_cols].fillna(0)

# 5. Save to CSV for Tableau
df_final.to_csv("cleaned_emissions_data.csv", index=False)
print("File 'cleaned_emissions_data.csv' has been created successfully!")