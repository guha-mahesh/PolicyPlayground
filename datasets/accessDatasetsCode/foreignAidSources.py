import pandas as pd
import gzip

url = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/sdg_17_20?format=tsv&compressed=true"

def fetch_foreign_aid_data():
    # Download and read TSV directly from the gzipped file
    df = pd.read_csv(url, compression='gzip', sep='\t')

    # print("Foreign Aid Financial Sources \n", df.tail())

    # print(df["freq,fin_source,unit,geo\TIME_PERIOD"])

    df.columns.values[0] = 'meta'

    # Split the first column by commas
    split_cols = df['meta'].str.split(',', expand=True)

    # Rename the split columns (you can change these names as appropriate)
    split_cols.columns = ['freq', 'fin_source', 'unit', 'geo']


    df = df.drop(columns='meta')

    # Concatenate the new columns with the rest of the DataFrame
    df = pd.concat([split_cols, df], axis=1)

    # output_file = "datasets/raw-datasets/foreign_aid_data.csv"
    # df.to_csv(output_file, index=False)
    # print(f"\nData saved to: {output_file}")

    print(df)
    return(df)
    '''for item in df.columns[0].split(","):
        df[item] = 00

    for index, row in df.iterrows():
        print(row)
        for column in df.columns[25:]:
            df[column] = row['freq,fin_source,unit,geo\TIME_PERIOD'].split(",")[

                list(df.columns).index(column)-25]

    # df = df.drop('freq,fin_source,unit,geo\TIME_PERIOD', axis=1)


    fin_sources = list(dict.fromkeys(df['fin_source'].tolist()))'''

fetch_foreign_aid_data()