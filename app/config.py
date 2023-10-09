import os
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import *
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///../../NONTOCCARE/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAYDAY = 15
    MESE_START = "2021-03"
    MESE_CORRENTE = datetime.now().strftime("%Y-%m")
    MESE_ANTICIPI_START = (datetime.now() + relativedelta(months=+1)).strftime("%Y-%m")
    MESE_ANTICIPI_END = (datetime.now() + relativedelta(months=+4)).strftime("%Y-%m")
    IP_TORNELLO = "192.168.1.100"
    PORT_TORNELLO = 1035
