import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import plotly.express as px
from sklearn.model_selection import train_test_split
import math

from hdi import download_hdi_data

hdi_df = download_hdi_data()


year_columns = ['1990', '2000', '2010', '2015', '2020', '2021', '2022', '2023']


df_melted = pd.melt(hdi_df, 
                    id_vars=['Country'], 
                    value_vars=year_columns,
                    var_name='Year', 
                    value_name='HDI')


df_melted['Year'] = pd.to_numeric(df_melted['Year'])
df_melted = df_melted.dropna(subset=['HDI'])

fig = px.line(df_melted, 
              x='Year', 
              y='HDI',
              color='Country',
              title='Human Development Index Trends by Country (1990-2023)',
              labels={
                  'HDI': 'Human Development Index',
                  'Year': 'Year',
                  'Country': 'Country'
              })

fig.update_layout(
    width=1000,
    height=600,
    hovermode='x unified',
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.01
    )
)

fig.update_traces(line=dict(width=2))

fig.show()
