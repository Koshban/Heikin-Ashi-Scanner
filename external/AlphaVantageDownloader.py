import urllib.request
import time
import os
import traceback
from config.config import *
from util.KeyGenerator import get_key
from util.LoggerManager import get_logger
import datetime as dt

today = dt.datetime.now().date()
my_weekday = dt.datetime.today().weekday()
maurl_pattern="https://www.alphavantage.co/query?function={0}&symbol={1}&apikey={2}&interval=daily&time_period={3}&series_type=close&datatype=csv"
price_pattern="https://www.alphavantage.co/query?function=TIME_SERIES_{0}_ADJUSTED&symbol={1}&apikey={2}&datatype=csv&outputsize={3}"
my_logger = get_logger(__name__)
failed_to_download=[]


search_sym_pattern="""https://www.alphavantage.co/query?function=SYMBOL_SEARCH&apikey={0}&keywords={1}&datatype=csv"""

def download_ma(type, symbol, apikey, range, retry_count =  0):
    time.sleep(SLEEP_TIME)
    url = maurl_pattern.format(type, symbol, apikey, range)
    filename = "{0}_{1}_{2}.csv".format(symbol, type, range)
    file = os.path.join(dirname, filename)
    with urllib.request.urlopen(url) as testfile, open( file, 'w') as f:
        data = testfile.read().decode("utf-8")

        if "Thank you for using Alpha Vantage" not in data:
            f.write(data.replace('\r\n', '\n').replace(type, "{0}{1}".format(type, range)))
            return
    #coming here means thank you from alphavantage.retry
    retry_count = retry_count + 1
    if retry_count <= 3:
        time.sleep(10)
        download_ma(type, symbol, apikey, range, retry_count)
    else:
        failed_to_download.append(symbol)


def downloaded_today(filename):
    if not os.path.exists(filename):
        return False
    filetime = dt.datetime.fromtimestamp( os.path.getmtime(filename))
    my_logger.debug("filetime.date: %s" % filetime.date())
    my_logger.debug("today: %s" % today)
    if filetime.date() == today:
        my_logger.debug("File {0} downloaded today. skip it".format(filename))
        return True

    days = (today - filetime.date()).days
    my_logger.debug("days = {0} weekday = {1}".format(days, my_weekday))
    if days == 0 or (my_weekday == 0 and days < 2):
        my_logger.debug("File {0} downloaded over weekend. skip it".format(filename))
        return True
    return False


def download_price(type, symbol, apikey, retry_count=0, output_type="compact", mode=None):
    url_symbol = symbol
    #if mode and mode == Mode.india:
        #url_symbol = "BSE:{0}".format(symbol)
    url = price_pattern.format(type, url_symbol, apikey, output_type)
    my_logger.debug("download_price: processing {0}".format(symbol))
    try:
        filename = "{0}_{1}.csv".format(symbol, type)
        file = os.path.join(dirname, filename)
        if downloaded_today(file):
            print("File already downloadded today -- {0}".format(file))
            return
        time.sleep(SLEEP_TIME)
        my_logger.debug("Getting data from url -- {0}".format(url))
        print("Getting data from url -- {0}".format(url))
        with urllib.request.urlopen(url) as testfile:
            my_logger.debug("url read done")
            data = testfile.read().decode("utf-8")
            my_logger.debug("{0}= {1}".format(symbol, len(data)))
            if data and "Thank you for using Alpha Vantage" not in data and len(data) > 1024:
                my_logger.debug("Before open")
                with open(file, 'w') as f:
                    my_logger.debug("file opened.. writing")
                    f.write(data.replace('\r\n', '\n').replace(type, "{0}{1}".format(type, range)))
                    my_logger.debug("file opened.. written data")
                    return
        #coming here means thank you from alphavantage.retry
    except Exception as e:
        my_logger.debug("exception  for {0}".format(symbol))
        my_logger.debug(str(e))
        traceback.print_exc()
    ## Just print message and fall through for retry
    except IOError:
        my_logger.debug("IO  Error")
    retry_count = retry_count + 1
    my_logger.debug("retry count for {0} =  {1}".format(symbol, retry_count))
    if retry_count <= 3:
        time.sleep(10)
        my_logger.debug("retry num {0}  for {1}".format(retry_count, symbol))
        download_price(type, symbol, apikey, retry_count)
    else:
        failed_to_download.append(symbol)


def download(ticker, retry_count = 2):
    if retry_count > 3:
        my_logger.debug("No of retries exceeded limit")
        exit(1)
    try:
        download_price("WEEKLY", ticker, alphakey_6)
        download_ma("EMA", ticker, alphakey_3, 13)
        download_ma("EMA", ticker, alphakey_4, 30)
        download_ma("RSI", ticker, alphakey_5, 14)
    except Exception as e:
        download(ticker, retry_count + 1)
        my_logger.debug(str(e))


def doanolad_daily_failed_ones(symbol):
    filename = "{0}_{1}.csv".format(symbol, "DAILY")
    file = os.path.join(dirname, filename)
    print("Downloading failed ones... {0}".format(file))
    file_stats = os.stat(file)
    filesize_kb = file_stats.st_size / 1024
    if filesize_kb > 1:
        print("File  already  exists")
        return
    download_daily(symbol)


def download_daily(symbol, mode=None):
     download_price("DAILY", symbol, get_key(), 0, "full", mode)


def get_valid_ticker(symbol1, symbol2):
    for symbol in ["{0}.BSE".format(symbol1), "{0}.BSE".format(symbol2)]:
        data = get_ticker_data(symbol)
        if data:
            return data
    print("Unable to find data for {0}".format(symbol1))
    return None, None


def get_ticker_data(symbol):
    import csv
    url = search_sym_pattern.format(get_key(), symbol)
    try:
        time.sleep(SLEEP_TIME)
        my_logger.debug("Getting data from url -- {0}".format(url))
        print("Getting data from url -- {0}".format(url))
        with urllib.request.urlopen(url) as response:
            data = response.read().decode("utf-8")
            if not data:
                return None, None
            datalines = data.splitlines()
            if len(datalines) < 2:
                return None, None
            myline = datalines[1].split(",")
            if len(myline) < 2:
                return None, None
            retval = (myline[0], myline[1])
            print(retval)
            return retval
    except Exception as e:
        my_logger.debug("exception  for {0}".format(symbol))
        my_logger.debug(str(e))
        traceback.print_exc()
        return None, None
