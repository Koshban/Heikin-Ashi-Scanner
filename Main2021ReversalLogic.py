import pandas as pd
import os
import argparse
from core.HAScanner import scan, printLists
from config.config import *
from external.AlphaVantageDownloader import download_daily, failed_to_download, get_valid_ticker
from util.utilities import SymbolDataDict,  add_to_list
from Main_BaseLineGenerator import prepare_other_data
from util.LoggerManager import get_logger
from util.GoogleSheetHandler import getNamesFromGoogleSheet
from datetime import datetime
import csv
from core.OptionScanner import analyze_options, print_exceptions

mylogger = get_logger(__name__)
symbol_df = None
dict_symbols = {}

def merge_two(ha_df,  df):
    df.rename(columns={'close': 'normal_close'}, inplace=True)
    del df['open']
    del df['high']
    del df['low']
    ha_df['timestamp'] = pd.to_datetime(ha_df['timestamp'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    ha_df = pd.merge(ha_df, df, how='inner', on='timestamp')
    ha_df.rename(columns={'ema9': 'EMA9'}, inplace=True)
    ha_df.rename(columns={'ema50': 'EMA50'}, inplace=True)
    ha_df.rename(columns={'ema21': 'EMA21'}, inplace=True)
    ha_df.rename(columns={'sma100': 'SMA100'}, inplace=True)
    ha_df.rename(columns={'sma200': 'SMA200'}, inplace=True)
    ha_df.rename(columns={'avol_50': 'AVOL_50'}, inplace=True)
    ha_df.rename(columns={'rsi14': 'RSI14'}, inplace=True)
    print("call add_to_list")
    add_to_list(ha_df, df, symbol)
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


def analyze(dict_symbols, symbol):
    daily_name = os.path.join(dirname, "{0}_DAILY.csv".format(symbol))
    df_tmp = pd.read_csv(daily_name).iloc[::-1]
    ha_df = heikin_ashi(df_tmp).iloc[::-1]
    print("preparing other data")
    df = prepare_other_data(symbol)
    print("merging two")
    ha_df = merge_two(ha_df, df)
    print("scan data")
    scan(symbol, ha_df)


def getNamesAndSymbol(mode):
    global dict_symbols
    if use_google_sheet:
        getNamesFromGoogleSheet(mode, dict_symbols)
        return
    with open("symbols.csv") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        current_header = "NA"
        for row in csvreader:
            if len(row) == 0:
                continue
            if row[0].startswith("#"):
                current_header = row[0].replace("##", "").strip()
                continue
            sources = dict_symbols.get(row[0].strip(), None)
            if sources:
                sources = "{0},{1}".format(sources, current_header)
            else:
                sources = current_header
            dict_symbols[row[0].strip()] = sources

def warmup(dict_symbols):
    print("Warm up download")
    for symbol, source in dict_symbols.items():
        print("{0} = {1}".format(symbol, source))
        if "Exclude" in source:
            print("skipping {0} as mark as exclude".format(symbol))
            continue
        download_daily(symbol, args.mode)

def download_and_analyze(dict_symbols):
    for symbol, source in dict_symbols.items():
        print("{0} = {1}".format(symbol, source))
        if "Exclude" in source:
            print("skipping {0} as mark as exclude".format(symbol))
            continue
        download_daily(symbol, args.mode)
        try:
            analyze(dict_symbols, symbol)
            #analyze_options(symbol, SymbolDataDict)
        except Exception as e:
            mylogger.error("Exception in analyze")
            mylogger.error(str(e))
            continue


if __name__  == '__main__':
    parser = argparse.ArgumentParser(description='Arguments to stock scanner')
    parser.add_argument('-m', '--mode', default=Mode.focus, type=Mode.parse, help="india|limited|smallcap|focus|all")
    args = parser.parse_args()
    print(args)
    start_time = datetime.now()
    getNamesAndSymbol(args.mode)
    print(dict_symbols)
    google_time = datetime.now()
    min_depth = Mode.depth(args.mode)
    print("Min Depth = {0}".format(min_depth))
    warmup(dict_symbols)
    for symbol, source in dict_symbols.items():
        print("{0} = {1}".format(symbol, source))
        if "Exclude" in source:
            print("skipping {0} as mark as exclude".format(symbol))
            continue
        download_daily(symbol, args.mode)
        try:
            analyze(dict_symbols, symbol)
            # analyze_options(symbol, SymbolDataDict)
        except Exception as e:
            mylogger.error("Exception in analyze")
            mylogger.error(str(e))
            continue
    download_time =datetime.now()
    printLists( dict_symbols, SymbolDataDict, args.mode)
    scan_time = datetime.now()
    mylogger.debug("Processing Completed")
    if len(failed_to_download) > 0:
        print("Failed to download ones:")
        print("\n".join(failed_to_download))
    print_exceptions()
    print("time to read google sheet = {0}".format( (google_time-start_time).total_seconds() ))
    print("time to download = {0}".format((download_time - start_time).total_seconds() / 60))
    print("time to scan = {0}".format((scan_time - start_time).total_seconds()))
