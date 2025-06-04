import pandas as pd
import plotly.express as px
import numpy as np


print("="*60)
print("LOADING DATA FILES")
print("="*60)


from hdi import download_hdi_data
hdi_df = download_hdi_data()


    


military_df = pd.read_csv('/Users/bhuvanhospet/FinFluxes/datasets/raw-datasets/API_MS.MIL.XPND.GD.ZS_DS2_en_csv_v2_337778.csv', skiprows=4)  # Skip first 4 rows



if 'Indicator Name' in military_df.columns:
    military_clean = military_df[military_df['Indicator Name'] == 'Military expenditure (% of GDP)'].copy()
    print(f"Military expenditure rows: {military_clean.shape[0]}")
else:
    military_clean = military_df.copy()
    print(f"Using all data as military expenditure: {military_clean.shape[0]} rows")


hdi_years = ['1990', '2010', '2015', '2020', '2021', '2022', '2023']


military_year_cols = [col for col in military_clean.columns if col.isdigit()]



common_years = [year for year in hdi_years if year in military_year_cols]




# Process HDI data
hdi_melted = pd.melt(hdi_df, 
                     id_vars=['Country'], 
                     value_vars=common_years,
                     var_name='Year', 
                     value_name='HDI')
hdi_melted['Year'] = pd.to_numeric(hdi_melted['Year'])
hdi_melted = hdi_melted.dropna(subset=['HDI'])

print(f"HDI data processed: {hdi_melted.shape[0]} rows")
print("HDI countries sample:", hdi_melted['Country'].unique()[:5])

# Process Military data
# Select relevant columns: Country Name and year columns
military_cols = ['Country Name'] + common_years
military_subset = military_clean[military_cols].copy()

# Rename Country Name to Country for merging
military_subset = military_subset.rename(columns={'Country Name': 'Country'})

# Melt military data
military_melted = pd.melt(military_subset, 
                         id_vars=['Country'], 
                         value_vars=common_years,
                         var_name='Year', 
                         value_name='Military_Expenditure')

military_melted['Year'] = pd.to_numeric(military_melted['Year'])

# Clean military expenditure values (handle empty strings)
military_melted['Military_Expenditure'] = military_melted['Military_Expenditure'].replace('', np.nan)
military_melted['Military_Expenditure'] = pd.to_numeric(military_melted['Military_Expenditure'], errors='coerce')
military_melted = military_melted.dropna(subset=['Military_Expenditure'])

print(f"Military data processed: {military_melted.shape[0]} rows")
print("Military countries sample:", military_melted['Country'].unique()[:5])

# Check for country name matching issues
hdi_countries = set(hdi_melted['Country'].unique())
military_countries = set(military_melted['Country'].unique())
common_countries = hdi_countries.intersection(military_countries)

print(f"\nCountry matching:")
print(f"HDI countries: {len(hdi_countries)}")
print(f"Military countries: {len(military_countries)}")
print(f"Common countries: {len(common_countries)}")

if len(common_countries) < 10:
    print("Warning: Few countries match. Sample mismatches:")
    hdi_sample = list(hdi_countries)[:5]
    military_sample = list(military_countries)[:5]
    print("HDI sample:", hdi_sample)
    print("Military sample:", military_sample)

# Merge datasets
merged_data = pd.merge(hdi_melted, 
                      military_melted[['Country', 'Year', 'Military_Expenditure']], 
                      on=['Country', 'Year'], 
                      how='inner')

print(f"\nMerged data: {merged_data.shape[0]} rows")
print(f"Countries in merged data: {merged_data['Country'].nunique()}")
print(f"Years in merged data: {sorted(merged_data['Year'].unique())}")

if merged_data.shape[0] == 0:
    print("ERROR: No data after merging! Check country name matching.")
    exit()

print("Sample merged data:")
print(merged_data.head())

# Create individual scatter plots for each year
available_years = sorted(merged_data['Year'].unique())
print(f"\nCreating {len(available_years)} individual scatter plots for years: {available_years}")

for year in available_years:
    year_data = merged_data[merged_data['Year'] == year]
    
    if len(year_data) > 0:
        print(f"\n{'='*40}")
        print(f"YEAR {int(year)}")
        print(f"{'='*40}")
        
        fig = px.scatter(year_data, 
                        x='Military_Expenditure', 
                        y='HDI',
                        color='Country',
                        title=f'Military Expenditure vs HDI - {int(year)}',
                        labels={
                            'Military_Expenditure': 'Military Expenditure (% of GDP)',
                            'HDI': 'Human Development Index'
                        },
                        hover_data=['Country'])
        
        fig.update_layout(
            width=1000, 
            height=700,
            showlegend=True,
            title_x=0.5,
            title_font_size=16,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.01
            )
        )
        
        # Add correlation and statistics
        if len(year_data) > 3:
            corr = year_data['Military_Expenditure'].corr(year_data['HDI'])
            fig.add_annotation(
                text=f"Correlation: {corr:.3f}<br>Countries: {len(year_data)}",
                x=0.02, y=0.98,
                xref="paper", yref="paper",
                showarrow=False,
                bgcolor="white",
                bordercolor="black",
                borderwidth=1,
                font_size=12
            )
        
        fig.show()
        
        # Print detailed statistics for this year
        print(f"Statistics for {int(year)}:")
        print(f"  Countries: {len(year_data)}")
        print(f"  Military expenditure range: {year_data['Military_Expenditure'].min():.2f}% to {year_data['Military_Expenditure'].max():.2f}%")
        print(f"  Mean military expenditure: {year_data['Military_Expenditure'].mean():.2f}%")
        print(f"  HDI range: {year_data['HDI'].min():.3f} to {year_data['HDI'].max():.3f}")
        print(f"  Mean HDI: {year_data['HDI'].mean():.3f}")
        
        if len(year_data) > 3:
            print(f"  Correlation: {corr:.4f}")
        
        # Show highest military spenders
        print(f"  Highest Military Spenders:")
        top_military = year_data.nlargest(5, 'Military_Expenditure')[['Country', 'Military_Expenditure', 'HDI']]
        for _, row in top_military.iterrows():
            print(f"    {row['Country']}: {row['Military_Expenditure']:.2f}% (HDI: {row['HDI']:.3f})")
        
        # Show highest HDI countries and their military spending
        print(f"  Highest HDI Countries:")
        top_hdi = year_data.nlargest(5, 'HDI')[['Country', 'HDI', 'Military_Expenditure']]
        for _, row in top_hdi.iterrows():
            print(f"    {row['Country']}: HDI {row['HDI']:.3f} (Military: {row['Military_Expenditure']:.2f}%)")

# Overall analysis across all years
print(f"\n{'='*60}")
print("OVERALL ANALYSIS ACROSS ALL YEARS")
print(f"{'='*60}")

overall_corr = merged_data['Military_Expenditure'].corr(merged_data['HDI'])
print(f"Overall correlation between Military Expenditure and HDI: {overall_corr:.4f}")

print(f"\nMilitary Expenditure Statistics (all years):")
print(f"  Range: {merged_data['Military_Expenditure'].min():.2f}% to {merged_data['Military_Expenditure'].max():.2f}%")
print(f"  Mean: {merged_data['Military_Expenditure'].mean():.2f}%")
print(f"  Median: {merged_data['Military_Expenditure'].median():.2f}%")

print(f"\nTop 10 Highest Military Spenders (all years):")
top_spenders = merged_data.nlargest(10, 'Military_Expenditure')[['Country', 'Year', 'Military_Expenditure', 'HDI']]
for _, row in top_spenders.iterrows():
    print(f"  {row['Country']} ({int(row['Year'])}): {row['Military_Expenditure']:.2f}% (HDI: {row['HDI']:.3f})")

print(f"\nCountries with High HDI and Low Military Spending:")
high_hdi_low_military = merged_data[(merged_data['HDI'] > 0.9) & (merged_data['Military_Expenditure'] < 2.0)]
if not high_hdi_low_military.empty:
    efficient_countries = high_hdi_low_military.groupby('Country').agg({
        'HDI': 'mean',
        'Military_Expenditure': 'mean'
    }).sort_values('HDI', ascending=False)
    
    print("  (High development with low military spending)")
    for country, row in efficient_countries.head(10).iterrows():
        print(f"    {country}: HDI {row['HDI']:.3f}, Military {row['Military_Expenditure']:.2f}%")

print(f"\nAnalysis complete! Check the {len(available_years)} individual scatter plots above.")