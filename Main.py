
import http.client
import pandas as pd
import os
import time

from core.HAScanner import scan, printLists
from config.config import *
from external.AlphaVantageDownloader import download
from util.utilities import merge_df, SymbolDataDict


def heikin_ashi(df):
    heikin_ashi_df = pd.DataFrame(index=df.index.values, columns=['open', 'high', 'low', 'close', 'timestamp'])
    heikin_ashi_df['close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4

    for i in range(len(df)):
        heikin_ashi_df.iat[i, 4] = df['timestamp'].iloc[i]
        if i == 0:
            heikin_ashi_df.iat[0, 0] = df['open'].iloc[0]
        else:
            heikin_ashi_df.iat[i, 0] = (heikin_ashi_df.iat[i - 1, 0] + heikin_ashi_df.iat[i - 1, 3]) / 2

    heikin_ashi_df['high'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['high']).max(axis=1)
    heikin_ashi_df['low'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['low']).min(axis=1)

    heikin_ashi_df['open'] = heikin_ashi_df['open'].apply(lambda x: round(x, 2))
    heikin_ashi_df['close'] = heikin_ashi_df['close'].apply(lambda x: round(x, 2))
    heikin_ashi_df['low'] = heikin_ashi_df['low'].apply(lambda x: round(x, 2))
    heikin_ashi_df['high'] = heikin_ashi_df['high'].apply(lambda x: round(x, 2))

    return heikin_ashi_df


def analyze(symbol, filename, is_weekly):

        df = pd.read_csv(filename).iloc[::-1]
        ha_df = heikin_ashi(df).iloc[::-1]
        print("scanning")
        scan(symbol, ha_df, is_weekly)
        print("merging")
        merge_df(ha_df, symbol, is_weekly)


if __name__  == '__main__':

    symbol_file_dir = os.path.dirname(os.path.abspath(__file__))
    symbol_file = os.path.join(symbol_file_dir, SymbolFileName )
    df = pd.read_csv(symbol_file)

    for index, row in df.iterrows():
        if (".HK" in row['Symbol']):
            continue
        if do_download:
            symbol =  row['Symbol']
            #print("[{0}]".format(symbol))
            download(symbol)
            time.sleep(10)

        if do_analyze:
            symbol = row['Symbol']
            weekly_name = os.path.join(dirname, "{0}_WEEKLY.csv".format(symbol))
            monthly_name = os.path.join(dirname, "{0}_MONTHLY.csv".format(symbol))

            #print(weekly_name)
            #print(monthly_name)
            try:
                print("Analyzing weekly")
                analyze(symbol, weekly_name, True)
                print("Analyzing monthly")
                analyze(symbol, monthly_name, False)
            except Exception as e:
                print(str(e))
                continue
    printLists(df, SymbolDataDict)
    print("Processing Completed")
