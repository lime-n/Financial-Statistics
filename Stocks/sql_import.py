from sqlalchemy import create_engine
import re
from numpy import float64, int64
import numpy as np
import pandas as pd
import re
from collections import defaultdict
import pyodbc

user = 'btcxxx'
passw = 'Exxx'
host =  'bitcoinxxx.database.windows.net'  # either localhost or ip e.g. '172.17.0.2' or hostname address 
port = 1433 
database = 'coiner'

engine = create_engine(
    'mssql+pyodbc://' + 
    user + ':' + 
    passw + '@' + 
    host + ':' + 
    str(port) + '/' + 
    database +f'?driver=ODBC+Driver+18+for+SQL+Server' , 
    echo=False,
    connect_args={"timeout":30},
                       pool_pre_ping=True, fast_executemany = True)


#load python script that batch loads pandas df to sql

sql_dataframe = pd.read_json('stocks.jl', lines=True)

#store the columns and data types as a dictionary
sql_data = defaultdict(list)

for keys, values in zip(sql_dataframe.columns, sql_dataframe.dtypes):
    if values == object:
        sql_data[keys].append("nchar(n)")
    elif values == float64:
        sql_data[keys].append('FLOAT')
    elif values == int64:
        sql_data[keys].append('BIGINT')

#store the columns and datatypes into one string for querying
ddl = ""
ddi = ""
dds = ""
VALUES = ['%s']*23
for columns, types in sql_data.items():
    for val in types:
        ddl += "`{}` `{}`,".format(columns,val)
        ddi += "`{}`,".format(columns)
for values in VALUES:
    dds += "{},".format(values)

#INSERT an SQL TABLE data
sql_insert = "INSERT INTO `{}` ({}) VALUES ({})".format(
    'StocksRealTime', ddi, dds
    )
sql_insert = re.sub(r'`','',sql_insert)

reg_comma = ['(?<=^.{234}).{1}', ',(?=[^,]*$)']
sql_insert_clean=[]

for comma in reg_comma:
    x=re.compile("(%s|%s)" % (reg_comma[0],reg_comma[1])).sub('',sql_insert)
    sql_insert_clean.append(x)

float_cols = sql_dataframe.select_dtypes(include=['float64']).columns
str_cols = sql_dataframe.select_dtypes(include=['object']).columns
int_cols = sql_dataframe.select_dtypes(include=['int64']).columns

sql_dataframe.loc[:, float_cols] = sql_dataframe.loc[:, float_cols].fillna(0)
sql_dataframe.loc[:, str_cols] = sql_dataframe.loc[:, str_cols].fillna('')
sql_dataframe.loc[:, int_cols] = sql_dataframe.loc[:, int_cols].fillna(0)

conn = engine.connect()
sql_dataframe.to_sql('StocksRealTime', con=engine,index=False, if_exists='append')

