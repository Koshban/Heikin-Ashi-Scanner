import pandas as pd
from io import StringIO
import requests
from requests.exceptions import HTTPError

ARK_LINKS = {
    "ARKK" : "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv",
    "ARKW" : "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.csv",
    "ARKG" : "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_GENOMIC_REVOLUTION_MULTISECTOR_ETF_ARKG_HOLDINGS.csv",
    "ARKF" : "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.csv",
    "PRNT" : "https://ark-funds.com/wp-content/fundsiteliterature/csv/THE_3D_PRINTING_ETF_PRNT_HOLDINGS.csv"
}

def getNamesFromARK(dict_symbols):
    for key, url in ARK_LINKS.items():
        try:
            response = requests.get(url)
            #print(response.text)
            df = pd.read_csv(StringIO(response.text), sep=",")
            df = df[df.ticker.notnull()]
            df = df[['ticker', 'fund', 'weight(%)']]
            print(df)
            for index, row in df.iterrows():
                ark_src = "{0}[{1}]".format(row['fund'], row['weight(%)'])
                old_src = dict_symbols.get(row['ticker'].strip(), None)
                if old_src:
                    ark_src = "{0}, {1}".format(old_src, ark_src)
                dict_symbols[row['ticker'].strip()] = ark_src
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')


if __name__  == '__main__':
    for key, url in ARK_LINKS.items():
        try:
            response = requests.get(url)
            print(response.text)
            df = pd.read_csv(StringIO(response.text), sep=",")
            df = df[df.ticker.notnull()]
            df = df[['ticker', 'fund', 'weight(%)']]
            print(df)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
