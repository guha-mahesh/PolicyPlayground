import pandas as pd

url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml"
df = pd.read_xml(url)
print(df.shape)
