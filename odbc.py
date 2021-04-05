import pyodbc

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


server = '10.10.10.18,33440'
db = 'BPRPA'
user = 'kap_assetm'
pwd = 'bprpaapp#2018'

class Kapodbc:

    def __init__(self, server=server, db=db, user=user, pwd=pwd):
        self.server = server
        self.db = db
        self.user = user
        self.pwd = pwd

    def connect(self):

        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + self.server + ';DATABASE=' + self.db + ';UID=' + self.user + ';PWD=' + self.pwd)
        cursor = conn.cursor()

        return conn, cursor
