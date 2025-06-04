import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from hdi import download_hdi_data
from foreignAidSources import fetch_foreign_aid_data


hdi_df = download_hdi_data()
foreign_aid_df = fetch_foreign_aid_data()



foreign_aid_df.columns = [col.strip() for col in foreign_aid_df.columns]
print("Cleaned foreign aid columns:", foreign_aid_df.columns.tolist())

# Dictionary for mapping the countries
country_code_mapping = {
    'AT': 'Austria',
    'BE': 'Belgium', 
    'BG': 'Bulgaria',
    'CH': 'Switzerland',
    'CY': 'Cyprus',
    'CZ': 'Czech Republic',
    'DE': 'Germany',
    'DK': 'Denmark',
    'EE': 'Estonia',
    'EL': 'Greece',  # EL is the EU code for Greece
    'ES': 'Spain',
    'FI': 'Finland',
    'FR': 'France',
    'HR': 'Croatia',
    'HU': 'Hungary',
    'IE': 'Ireland',
    'IS': 'Iceland',
    'IT': 'Italy',
    'LT': 'Lithuania',
    'LU': 'Luxembourg',
    'LV': 'Latvia',
    'MT': 'Malta',
    'NL': 'Netherlands',
    'NO': 'Norway',
    'PL': 'Poland',
    'PT': 'Portugal',
    'RO': 'Romania',
    'SE': 'Sweden',
    'SI': 'Slovenia',
    'SK': 'Slovakia',
    'TR': 'Turkey',
    'UK': 'United Kingdom'
}


year_cols_aid = [col for col in foreign_aid_df.columns if col.isdigit()]
print(f"Year columns in foreign aid data: {year_cols_aid}")


hdi_years = ['1990', '2010', '2015', '2020', '2021', '2022', '2023']
print(f"HDI years available: {hdi_years}")


common_years = [year for year in hdi_years if year in year_cols_aid]
print(f"Common years for analysis: {common_years}")

if not common_years:
    print("no overlap")
else:
    # Process HDI data
    hdi_melted = pd.melt(hdi_df, 
                         id_vars=['Country'], 
                         value_vars=common_years,
                         var_name='Year', 
                         value_name='HDI')
    hdi_melted['Year'] = pd.to_numeric(hdi_melted['Year'])
    hdi_melted = hdi_melted.dropna(subset=['HDI'])
    

    
    # Process Foreign Aid data
    # Filter for TOTAL foreign aid
    total_aid_df = foreign_aid_df[foreign_aid_df['fin_source'] == 'TOTAL'].copy()

    
    # Add country mapping
    total_aid_df['Country'] = total_aid_df['geo'].map(country_code_mapping)
    total_aid_df = total_aid_df.dropna(subset=['Country'])
    print(f"After country mapping: {total_aid_df.shape[0]} rows")
    
    # Melt foreign aid data
    aid_melted = pd.melt(total_aid_df, 
                         id_vars=['Country'], 
                         value_vars=common_years,
                         var_name='Year', 
                         value_name='Foreign_Aid')
    
    aid_melted['Year'] = pd.to_numeric(aid_melted['Year'])
    

    aid_melted['Foreign_Aid'] = aid_melted['Foreign_Aid'].replace(':', np.nan)
    aid_melted['Foreign_Aid'] = pd.to_numeric(aid_melted['Foreign_Aid'], errors='coerce')
    aid_melted = aid_melted.dropna(subset=['Foreign_Aid'])
    

    print("Sample aid data:")
    print(aid_melted.head())
    

    merged_data = pd.merge(hdi_melted, 
                          aid_melted[['Country', 'Year', 'Foreign_Aid']], 
                          on=['Country', 'Year'], 
                          how='inner')


    
    if merged_data.shape[0] > 0:
        available_years = sorted(merged_data['Year'].unique())
        print(f"\nCreating individual plots for years: {available_years}")
        
        for year in available_years:
            year_data = merged_data[merged_data['Year'] == year]
            
            if len(year_data) > 0:
                fig = px.scatter(year_data, 
                                x='Foreign_Aid', 
                                y='HDI',
                                color='Country',
                                title=f'Foreign Aid vs HDI - {int(year)}',
                                labels={
                                    'Foreign_Aid': 'Foreign Aid (Million EUR)',
                                    'HDI': 'Human Development Index'
                                },
                                hover_data=['Country'])
                
                fig.update_layout(
                    width=900, 
                    height=600,
                    showlegend=True,
                    title_x=0.5,
                    title_font_size=16
                )
                
                if len(year_data) > 3:
                    corr = year_data['Foreign_Aid'].corr(year_data['HDI'])
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
       
        
    else:
        print("no data")