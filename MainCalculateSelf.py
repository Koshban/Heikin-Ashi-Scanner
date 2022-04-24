import pandas as pd
import argparse

from core.HAScanner import scan, printLists
from config.config import *
from external.AlphaVantageDownloader import download_daily, doanolad_daily_failed_ones
from util.utilities import SymbolDataDict,  add_to_list
from Main_BaseLineGenerator import prepare_other_data, prepare_weekly, prepare_monthly
from util.LoggerManager import get_logger
from util.GoogleSheetHandler import getNamesFromGoogleSheet
from itertools import tee

mylogger = get_logger(__name__)
symbol_df = None


def merge_two(ha_df,  df):
    daily_df = df[['open',  'high', 'low', 'close']].copy()
    df.rename(columns={'close': 'normal_close'}, inplace=True)
    del df['open']
    del df['high']
    del df['low']
    ha_df['timestamp'] = pd.to_datetime(ha_df['timestamp'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    ha_df = pd.merge(ha_df, df, how='inner', on='timestamp')

    ha_df.rename(columns={'sma50': 'SMA50'}, inplace=True)
    ha_df.rename(columns={'sma200': 'SMA200'}, inplace=True)
    ha_df.rename(columns={'ema13': 'EMA13'}, inplace=True)
    ha_df.rename(columns={'ema30': 'EMA30'}, inplace=True)
    ha_df.rename(columns={'ema21': 'EMA21'}, inplace=True)
    ha_df.rename(columns={'ema50': 'EMA50'}, inplace=True)
    ha_df.rename(columns={'avol_7': 'AVOL_7'}, inplace=True)
    ha_df.rename(columns={'avol_21': 'AVOL_21'}, inplace=True)
    ha_df.rename(columns={'avol_50': 'AVOL_50'}, inplace=True)
    print("call add_to_list")
    add_to_list(ha_df, daily_df,symbol)
    print("merge  end")
    return ha_df


def heikin_ashi(df):
    heikin_ashi_df = pd.DataFrame(index=df.index.values, columns=[ 'open', 'high', 'low', 'close', 'timestamp'])
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


def analyze(symbol, is_weekly):
    daily_name = os.path.join(dirname, "{0}_DAILY.csv".format(symbol))
    #df_tmp = pd.read_csv(daily_name, parse_dates=['timestamp'], index_col=['timestamp']).iloc[::-1]
    df_tmp = pd.read_csv(daily_name).iloc[::-1]
    if is_weekly:
        df_tmp = prepare_weekly(df_tmp)
    else:
        df_tmp = prepare_monthly(df_tmp)
    ha_df = heikin_ashi(df_tmp).iloc[::-1]
    mylogger.debug("preparing other data for {0}".format(symbol))
    df = prepare_other_data(symbol)
    mylogger.debug("merging two data")
    ha_df = merge_two(ha_df, df)
    mylogger.debug("scanning data")
    scan(symbol, ha_df, is_weekly)
    mylogger.debug(ha_df.head())

def getSymbols():

    get_from_google = True
    if get_from_google:
        names = getNamesFromGoogleSheet()
        return names
    else:
        symbol_file_dir = os.path.dirname(os.path.abspath(__file__))
        symbol_file = os.path.join(symbol_file_dir, SymbolFileName )
        symbol_df = pd.read_csv(symbol_file)
        for index, row in symbol_df.iterrows():
            if (".HK" in row['Symbol']):
                continue
            yield row['Name'], row['Symbol']

if __name__  == '__main__':

    parser = argparse.ArgumentParser(description='Process Stock market data.')
    parser.add_argument('-t', '--tab', required=True, help='Name of tab in Google cheet')
    args = parser.parse_args()

    name_syms = getNamesFromGoogleSheet(args.tab)
    name_syms, name_syms_backup = tee(name_syms)
    print(name_syms)
    for name, symbol, consensus, target in name_syms:
        print(symbol)
        if "Ticker" in symbol:
            continue

        if do_download:
            download_daily(symbol)
        if do_analyze:
            try:
                analyze(symbol, True)
                analyze(symbol, False)
            except Exception as e:
                mylogger.error(str(e))
                continue

    printLists(name_syms_backup, SymbolDataDict, args.tab)
    mylogger.debug("Processing Completed")