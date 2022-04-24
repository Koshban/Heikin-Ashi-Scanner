from config.config import *

keys_list = [alphakey_1, alphakey_2, alphakey_3, alphakey_4, alphakey_5,  alphakey_6, alphakey_7, alphakey_8]
prem_key = ""
prem_key = ""  # through mail
last_idx = 0


def get_key():
    #return prem_key
    return get_key_roundrobin()


def get_key_roundrobin():
    global last_idx
    last_idx = last_idx + 1
    if last_idx >= len(keys_list):
        last_idx = 0

    return keys_list[last_idx]

