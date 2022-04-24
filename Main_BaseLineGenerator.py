import pandas as pd
from stockstats import StockDataFrame as Sdf
from ta.volume import MFIIndicator
from config.config import *

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 1000)
logic = {
    'open'  : 'first',
    'high'  : 'max',
    'low'   : 'min',
    'close' : 'last',
    'adjusted_close' : 'last',
    'volume': 'sum',
    'dividend_amount': 'sum',
    'split_coefficient': 'sum',
    'timestamp': 'last'
}

def prepare_weekly(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['key'] = df['timestamp'].map(lambda x: 100*x.year + x.week)
    df2 = df.groupby('key').agg(logic)
    return df2

def prepare_sma(df, my_span):
    column_name="SMA{0}".format(my_span)
    df[column_name] = df.close.rolling(my_span).mean()

def prepare_vol_sma(df, my_span):
    column_name="AVOL_{0}".format(my_span)
    df[column_name] = df.volume.rolling(my_span).mean()

def in_squeeze(df):
    return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

def prepareBollingerAndSqueeze(df):
    df['20sma'] = df.close.rolling(window=20).mean()
    df['stddev'] = df.close.rolling(window=20).std()
    df['lower_band'] = df['20sma'] - (2 * df['stddev'])
    df['upper_band'] = df['20sma'] + (2 * df['stddev'])
    df['TR'] = abs(df['high'] - df['low'])
    df['ATR'] = df['TR'].rolling(window=20).mean()
    df['lower_keltner'] = df['20sma'] - (df['ATR'] * 1.5)
    df['upper_keltner'] = df['20sma'] + (df['ATR'] * 1.5)
    df['squeeze_on'] = df.apply(in_squeeze, axis=1)
    del df['20sma']
    del df['stddev']
    del df['TR']
    del df['ATR']
    del df['lower_keltner']
    del df['upper_keltner']


def prepare_ema(df, my_span):
    """ Alphavantage is calculating EMA and SMA based on close it seems.
    Ideally we should be using adjusted_close..  so let's do it ourselves"""

    column_name="EMA{0}".format(my_span)
    df[column_name] = df.close.ewm(span=my_span, adjust=False).mean()


def prepare_rsi(df):
    stock_df = Sdf.retype(df)
    df['RSI14'] =  stock_df['rsi_14']
    del df['close_-1_s']
    del df['close_-1_d']
    del df['rs_14']
    del df['rsi_14']
    del df['closepm']
    del df['closenm']
    del df['closepm_14_smma']
    del df['closenm_14_smma']


def prepare_MFI(df):
    print("before mfi")
    mfi_ind = MFIIndicator(high=df['high'], low=df['low'],close= df['close'], volume=df['volume'], n=14, fillna=True)
    df['mfi'] = mfi_ind.money_flow_index()
    print( df.tail())


def prepare_other_data(symbol):
    daily_name = os.path.join(dirname, "{0}_DAILY.csv".format(symbol))
    df = pd.read_csv(daily_name).iloc[::-1]
    prepare_vol_sma(df, 50)
    prepare_ema(df, 9)
    prepare_ema(df, 21)
    prepare_ema(df, 50)
    prepare_sma(df, 100)
    prepare_sma(df, 200)
    prepare_rsi(df)
    prepareBollingerAndSqueeze(df)
    df['pct_change'] = df.close.pct_change()
    return df.iloc[::-1]


if __name__  == '__main__':

    symbol =  "AAPL"
    print("Processing completed")
