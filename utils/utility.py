from sqlalchemy import create_engine
import yaml
import datetime
import requests
import os
#%%
def parse_config(path):
    with open(path, 'r') as stream:
        return  yaml.load(stream, Loader=yaml.FullLoader)

#%%
def hexToInt(x):
    return int(x, 16)

def killFile(fpath):
    if os.path.exists(fpath):
        os.remove(fpath)
                
#%%Date & Block Conversions
def getDateFromTimestamp(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp).strftime('%d-%b-%Y')