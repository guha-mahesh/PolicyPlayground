# packages used so far + some new for today
from hdi import download_hdi_data
import math
from sklearn.model_selection import train_test_split
import plotly.express as px
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup
import requests
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


hdi_df = download_hdi_data()

hdi_df.head()
