from util.mailer import sendmail
from util.utilities import get_logger
from util.OutputBuilder import add_to_output, add_to_emax, add_to_freefall, get_signal_tables, add_to_bollinger
from config.config import min_depth, Mode

my_logger = get_logger(__name__)
dict_bear_to_bull = {}
dict_bear_to_bull_2days = {}
dict_falling = {}
dict_bollinger = {}

## ttm sqeeze
## https://github.com/hackingthemarkets/ttm-squeeze
## https://github.com/hackingthemarkets/ttm-squeeze/blob/master/squeeze.py


def getFloatValue(val, type, xover):
    try:
        X = ""
        if xover != 0:
            X = "X"
        if "none" in type:
            return "{:.2f}".format(val)
        if "ma" in type:
            fval = float(val)
            if fval >= 1:
                return "GREEN{0} {1}".format(val, X)
            return "RED{0} {1}".format(val,  X)
        if "vol" in type:
            fval = float(val)
            if fval > 1.3 and xover[0] >= min_depth:
                return "{:.2f}XG".format(fval)
            elif fval > 1.3 and xover[1] >= 10:
                return "{:.2f}XG".format(fval)
            return "{:.2f}".format(fval)
        return "{0} {1}".format(val, X)
    except:
        return val


def getCellValue(boolean_input, type, val_to_add = ""):
    if boolean_input:
        return "{0}XG".format(val_to_add) if ("bullish" in type) else "{0}XR".format(val_to_add)
    return " "


def printLists(dict_symbols, symdict, mode):
    my_logger.debug(dict_symbols)
    min_depth = Mode.depth(mode)
    for symbol, symdata in symdict.items():
        bear_reversal_days = dict_bear_to_bull.get(symbol, 0)
        free_falll_days = dict_falling.get( symbol, 0)
        distance_from_ema = "{0}%XG".format(symdata.distance_from_ema) if symdata.distance_from_ema_raw > 0 else "{0}%".format(symdata.distance_from_ema)
        if bear_reversal_days >= min_depth:
            add_to_output([
                symbol,
                getCellValue(bear_reversal_days >= min_depth, "bullish", bear_reversal_days),
                getFloatValue(symdata.vol_by_50, "vol", (bear_reversal_days, free_falll_days)),
                getFloatValue(symdata.normal_close, "none", ""),
                getFloatValue(symdata.ema_9_21, "none", ""),
                distance_from_ema,
                getFloatValue(symdata.rsi14, "rsi", symdata.rsix),
                dict_symbols.get(symbol)
            ])
        if free_falll_days >= min_depth:
            add_to_freefall([
                symbol,
                getCellValue(free_falll_days >= min_depth, "bearish", free_falll_days),
                getFloatValue(symdata.vol_by_50, "vol", (bear_reversal_days, free_falll_days)),
                getFloatValue(symdata.normal_close, "none", ""),
                getFloatValue(symdata.ema_9_21, "none", ""),
                distance_from_ema,
                getFloatValue(symdata.rsi14, "rsi", symdata.rsix),
                dict_symbols.get(symbol)
            ])
        if symdata.bollingerComment:
            add_to_bollinger([
                symbol,
                symdata.bollingerComment,
                getFloatValue(symdata.vol_by_50, "vol", (bear_reversal_days, free_falll_days)),
                getFloatValue(symdata.normal_close, "none", ""),
                getFloatValue(symdata.ema_9_21, "none", ""),
                getFloatValue(symdata.rsi14, "rsi", symdata.rsix),
                dict_symbols.get(symbol)
            ])
        if symdata.ma_support_comment:
            add_to_emax([
                symbol,
                getFloatValue(symdata.vol_by_50, "vol", (bear_reversal_days, free_falll_days)),
                getFloatValue(symdata.normal_close, "none", ""),
                symdata.ma_support_comment,
                getFloatValue(symdata.ma100, "none", ""),
                getFloatValue(symdata.ma200, "none", ""),
                getFloatValue(symdata.rsi14, "rsi", symdata.rsix),
                dict_symbols.get(symbol)
            ])
    signal_list = get_signal_tables()
    print("Sending mail")
    sendmail( signal_list, mode)
    print("TTM Squeeze on ")
    for key, val in dict_bollinger.items():
        print(key)


def scan(symbol, df):
    if len(df) < 5 or len(df) < min_depth + 1:
        return
    BearishToPotentialBullishForXDays(dict_bear_to_bull, symbol, df, min_depth)
    IsFreeFalling(symbol, df, min_depth)


def BearishToPotentialBullish(symdict, symbol, df, depth=min_depth):
    if len(df) < depth + 1:
        return False
    my_depth=0
    for i in range(len(df)):
        ## First one should be green. if red break
        if i == 0:
            if df['open'].iloc[0] > df['close'].iloc[0]:
                break
            continue
        ## Continue until next green after first one
        if df['open'].iloc[i] < df['close'].iloc[i]:
            break
        my_depth = my_depth + 1
    if my_depth >= depth:
        dict_bear_to_bull[symbol] = my_depth


def BearishToPotentialBullishForXDays(result_dict, symbol, df, depth=min_depth):
    if len(df) < depth + 1:
        return
    my_depth=0
    for idx in range(len(df)):
        ## First one should be green. if red break.. index starts with 0 so for bullish_days = 1, i =0
        if idx < 1:
            if df['open'].iloc[idx] > df['close'].iloc[idx]:
                break
            continue
        ## Continue until next green after first one
        if df['open'].iloc[idx] < df['close'].iloc[idx]:
            break
        my_depth = my_depth + 1
    if my_depth >= depth:
        result_dict[symbol] = my_depth


def IsFreeFalling(symbol, df, depth):
    if len(df) < depth+1:
        return False
    red_counts = 0
    for i in range(len(df)):
        if df['open'].iloc[i] > df['close'].iloc[i]:
            red_counts = red_counts +1
        else:
            break
    if red_counts >= depth:
        dict_falling[symbol] = red_counts
