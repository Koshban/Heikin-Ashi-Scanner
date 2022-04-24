import numpy as np
from wallstreet import Stock, Call, Put

exception_list = []
next_expiry = '18-06-2021'


def update_option_data(symbol, symdata):
    stk = Stock(symbol)
    print(stk.price)
    c = Call(symbol, 18, 6, 2021)
    print("\n----------------------------------------------")
    print(symbol)
    print(c.strikes)
    closest_strike, idx = closest(c.strikes, symdata.close)
    print( f" close price = {symdata.close}, closest strike = {closest_strike}, index = {idx}")
    c = Put(symbol, 18, 6, 2021, closest_strike)
    print( f"strike = {closest_strike} vol = {c.implied_volatility()} delta = {c.delta()} bid = {c.bid} ask = {c.ask}" )
    symdata.option_iv = c.implied_volatility()
    symdata.option_delta = c.delta()
    symdata.option_strike = closest_strike
    symdata.option_bid = c.bid
    symdata.option_ask = c.ask
    symdata.option_expiry = c.next_expiry


def analyze_options(symbol, symbols_data_details):
    print("")
    print("----------------------Wallstreet analysis")
    symdata = symbols_data_details.get(symbol)
    try:
        update_option_data(symbol, symdata)
    except Exception as e:
        print(f"Unable to extract options for {symbol}")
        exception_list.append(symbol)


def print_exceptions():
    print("Unable to extract option details for below symbols")
    print("\n".join(exception_list))


def closest(lst, K):
    lst = np.asarray(lst)
    idx = (np.abs(lst - K)).argmin()
    return lst[idx], idx

