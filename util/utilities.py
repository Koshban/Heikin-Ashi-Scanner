import os
import pandas as pd
from config.config import dirname
from util.SymbolData import SymbolData
from util.LoggerManager import get_logger

SymbolDataDict = {}
my_logger = get_logger(__name__)


def add_to_list(hadf, normaldf, symbol):
    """ Easier to handle in another  pandas dataframe  for the long run??
    Just  add class object to the list for now. who has time!
    """
    if hadf is None:
        return
    symdata = SymbolData(symbol, hadf, normaldf)
    SymbolDataDict.update({symbol: symdata})
    my_logger.debug("Printing symdata after merging and adding to list")
    my_logger.debug(symdata)


def merge_two_df(ha_df, df):
    return pd.merge(ha_df, df[['timestamp', 'SMA50', 'SMA100', 'EMA13', 'EMA30', 'RSI14']], how='inner', on='timestamp')


def merge_df(ha_df, symbol, is_weekly):
    """ Unfortunately we cannot query alphavantage with  SMA/EMA/RSI in one go, We end up getting multiple csv's.
    Instead bending your head in the  end to merge different values, it is easier to do inner join on pd df.
    """
    if not is_weekly:
        return

    my_logger.debug("merge sma 50")
    df_tmp = _merge(ha_df, symbol, "SMA", "50")
    my_logger.debug("merge sma 200")
    tmp1 = _merge(df_tmp, symbol, "SMA", "200")
    my_logger.debug("merge ema 13")
    tmp2 = _merge(tmp1, symbol, "EMA", "13")
    my_logger.debug("merge ema 30")
    tmp3 = _merge(tmp2, symbol, "EMA", "30")
    my_logger.debug("merge rsi")
    tmp4 = _merge(tmp3, symbol, "RSI", "14")

    #check crossover
    add_to_list(tmp4, symbol)


def _merge(ha_df, symbol, type, range):
    if ha_df is None:
        return
    basename = "{0}_{1}_{2}.csv".format(symbol, type, range)
    filename = os.path.join(dirname, basename)
    #print(filename)
    colName = "{0}{1}".format(type, range)

    df_tmp = pd.read_csv(filename)
    if df_tmp is None:
        my_logger.error("{0} Something wrong... insert  blank column and return".format(symbol))
        return ha_df.insert(0, colName, 0)

    row, column = df_tmp.shape
    if row < 1:
        my_logger.error("{0} Something wrong... insert  blank column and return".format(symbol))
        return ha_df.insert(0, colName, 0)

    df_tmp = df_tmp.rename(columns={'time':'timestamp'})
    my_logger.debug("ha datafram head")
    my_logger.debug(ha_df.head())
    my_logger.debug("tmp dataframe head")
    my_logger.debug(df_tmp.head())
    return pd.merge( ha_df, df_tmp, how='inner', on='timestamp')




