from prettytable import PrettyTable


class SymbolData:
    """ Class to hold misc symbol data. used in the  end to populate table"""

    ma_support_comment = None
    def __init__(self, symbol, df, normaldf):
        if df is None:
            return
        self.symbol = symbol
        self.open = df['open'].iloc[0]
        self.close = df['close'].iloc[0]
        self.normal_close = df['normal_close'].iloc[0]
        self.high = df['high'].iloc[0]
        self.low = df['low'].iloc[0]
        self.volume = df['volume'].iloc[0]
        self.timestamp = df['timestamp'].iloc[0]
        self.avol_50 = df['AVOL_50'].iloc[0]
        self.vol_by_50 = format( self.volume / self.avol_50, '.2f')
        self.ema9 = df['EMA9'].iloc[0]
        self.ema21 = df['EMA21'].iloc[0]
        self.ema50 = df['EMA50'].iloc[0]
        self.ma100 = df['SMA100'].iloc[0]
        self.ma200 = df['SMA200'].iloc[0]
        self.rsi14 = format( df['RSI14'].iloc[0], '.2f')
        self.ema_9_21 = format( self.ema9 / self.ema21, '.2f')
        self.EMA_XOver = False
        self.RSI_XOver(df)
        self.Is_EMA_XOver(df)
        self.distance_from_ema_raw = ((self.normal_close - self.ema9) * 100) / self.normal_close
        self.distance_from_ema = format( ((self.normal_close - self.ema9) * 100) / self.normal_close, '.2f')
        self.check_ttm_squeeze(normaldf)
        self.check_bollingerX(df)
        self.checkMA_100_200_Proximity(self.normal_close, self.ma100, self.ma200)
        self.normaldf = normaldf
        # option data
        self.option_iv = None
        self.option_delta = None
        self.option_bid = None
        self.option_ask = None
        self.option_expiry = None
        self.option_strike = None


    def check_ttm_squeeze(self, df):
        self.squeeze_on = False
        if df['squeeze_on'].iloc[0] == True and df['squeeze_on'].iloc[1] == False:
            self.squeeze_on = True


    def checkMA_100_200_Proximity(self, close, ma100, ma200):
        if close > (ma100 * 0.99) and close <= (ma100 * 1.01):
            self.ma_support_comment = "Near MA 100"
        if close > (ma200 * 0.99) and close <= (ma200 * 1.01):
            self.ma_support_comment = "Near MA 200"
        return


    def check_bollingerX(self, df):
        self.bollingerComment = None
        if df['normal_close'].iloc[0] > df['lower_band'].iloc[0] and df['normal_close'].iloc[1] < df['lower_band'].iloc[1]:
            self.bollingerComment = "X above lower"
        elif df['normal_close'].iloc[0] < df['lower_band'].iloc[0] and df['normal_close'].iloc[1] > df['lower_band'].iloc[1]:
            self.bollingerComment = "X below lower"
        elif df['normal_close'].iloc[0] < df['lower_band'].iloc[0]:
            self.bollingerComment = "Near lower"
        elif df['normal_close'].iloc[0] < (df['lower_band'].iloc[0] * 1.01):
            self.bollingerComment = "Near lower"


    def RSI_XOver(self, df):
        """Simply calculates the cross over based on two reference points.
        We can potentially prepare the entire  crossover  points in pandas.. if we want backtesting """
        self.rsix = 0
        if df is None or len(df) < 5:
            return
        if (df['RSI14'].iloc[0] > 30 and df['RSI14'].iloc[1] <= 30) or \
                (df['RSI14'].iloc[0] <= 30 and df['RSI14'].iloc[1] > 30) or \
                (df['RSI14'].iloc[0] > 50 and df['RSI14'].iloc[1] <= 50) or \
                (df['RSI14'].iloc[0] <= 50 and df['RSI14'].iloc[1] > 50) or \
                (df['RSI14'].iloc[0] > 70 and df['RSI14'].iloc[1] <= 70) or \
                (df['RSI14'].iloc[0] <= 70 and df['RSI14'].iloc[1] > 70):
            self.rsix = 1


    def Is_EMA_XOver(self, df):
        if df['normal_close'].iloc[0] > df['EMA9'].iloc[0] and df['normal_close'].iloc[1] < df['EMA9'].iloc[1]:
            self.EMA_XOver = True


    def __str_1__(self):
        if self.smax !=  0:
            return "{0} {1}".format(self.symbol, self.smax)
        return ""


    def __str__(self):
        table = PrettyTable()
        table.field_names = ['Sym', 'timestamp', 'open', 'close', 'high', 'low', 'EMA9', 'EMA21', 'EMA50', 'RSI14']
        table.add_row([self.symbol, self.timestamp, self.open, self.close, self.high, self.low,
                       self.ema9, self.ema21, self.ema50, self.rsi14])
        return str(table)
