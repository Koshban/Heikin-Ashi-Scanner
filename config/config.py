""" Configuration files to setup Logging, email, API Keys for login etc
Use your own email IDs and passwords. If using gmail, then enable third part low auth and use Google Generated App (Python)
Passwords. There are many articles that can help provide details, e.g.
https://towardsdatascience.com/automate-sending-emails-with-gmail-in-python-449cc0c3c317
We are using AlphaVantage Stock APIs, you need to use your own AlphaVantage Free API Keys here
"""

import logging
import os
from datetime import datetime
import subprocess
import sys
SymbolFileName = "symbols.csv"

min_depth = 4
receiver = ["xyz@gmail.com"]
message_to = "xyz@gmail.com"

if os.name == 'nt':
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(PROJECT_ROOT)
    log_file = f"{BASE_DIR}\\logfile.txt"
    dirname = f"{BASE_DIR}"
    receiver = ["xyz@gmail.com"]
    message_to = "xyz@gmail.com"
else:
    dirname = "/home/stockscan/scanroot/cache"
    log_dir = "/home/stockscan/scanroot/logs"
    log_file = "/home/stockscan/scanroot/logs/logfile.txt"
    my_sub_process1 = subprocess.run(f"mkdir -p {dirname}", shell=True, text=True, capture_output=True)
    my_sub_process2 = subprocess.run(f"mkdir -p {log_dir}", shell=True, text=True, capture_output=True)
    if my_sub_process2.returncode != 0 or my_sub_process1.returncode != 0:
        print(f'Unable to create Directories for logging, please check : {dirname} and/or {log_dir}')
        sys.exit()


mail_receiver = ["xyz@gmail.com"]  # Use requisite mail ID
mail_message_to = "xyz@gmail.com"

message_from = "myexample@gmail.com"  # Your email id, if using gmail
port = 587  # For starttls, change port if you require
smtp_server = "smtp.gmail.com"
password = ""
sender = "myexample@gmail.com"

round_robin = True
SLEEP_TIME = 0
if round_robin:
    SLEEP_TIME = 4
use_google_sheet = True

## Logging configuration
log_level = logging.DEBUG

""" We are using AlphaVantage Stock APIs, you need to use your own AlphaVantage Free API Keys here"""
alphakey_1 = ""

alphakey_2 = ""

alphakey_3 = ""

alphakey_4 = ""

alphakey_5 = ""

alphakey_6 = ""

alphakey_7 = ""

alphakey_8 = ""


class Mode:
    india = 0
    limited = 1
    smallcap = 2
    focus = 3
    all = 4

    @staticmethod
    def name(s):
        return {
            Mode.india: "india",
            Mode.limited: "limited",
            Mode.smallcap: "smallcap",
            Mode.focus: "focus",
            Mode.all: "all"
        }[s]

    @staticmethod
    def parse(s):
        return {
            "india": Mode.india,
            "limited": Mode.limited,
            "smallcap": Mode.smallcap,
            "focus": Mode.focus,
            "all": Mode.all
        }[s]

    @staticmethod
    def subject(s):
        return {
            Mode.india: "India Focused Scans : {0}".format(datetime.now().strftime("%d-%m-%Y")),
            Mode.limited: "US scans : {0}".format(datetime.now().strftime("%d-%m-%Y")),
            Mode.smallcap: "US SmallCap Scans : {0}".format(datetime.now().strftime("%d-%m-%Y")),
            Mode.focus: "US Focused Scans : {0}".format(datetime.now().strftime("%d-%m-%Y")),
            Mode.all: "US Scans : {0}".format(datetime.now().strftime("%d-%m-%Y"))
        }[s]

    @staticmethod
    def message_to(s):
        return {
            Mode.india: "xyz@gmail.com",
            Mode.all: "xyz@gmail.com"
        }[s]

    @staticmethod
    def depth(s):
        return {
            Mode.india: 7,
            Mode.limited: 7,
            Mode.smallcap: 7,
            Mode.focus: 7,
            Mode.all: 7
        }[s]