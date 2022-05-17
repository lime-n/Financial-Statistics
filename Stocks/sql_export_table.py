from sqlalchemy import create_engine
import re
from numpy import float64, int64
import pandas as pd
import re
from collections import defaultdict
import pyodbc
import pymssql
# class SqlazurePipeline: set up SQL server

connection = pymssql.connect("bitcoinserver.database.windows.net", "btcServer", "EMrizoj.12", "coiner")
cursor = connection.cursor()


sql_dataframe = pd.read_json('stocks.jl', lines=True)

#store the columns and data types as a dictionary
sql_data = defaultdict(list)

for keys, values in zip(sql_dataframe.columns, sql_dataframe.dtypes):
    if values == object:
        sql_data[keys].append("NVARCHAR(255)")
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

##CREATE an SQL TABLE
sql_create = "CREATE TABLE `{}` ({})".format('StocksRealTime', ddl)
sql_create=re.sub(r'`','',sql_create)
print(sql_create)
cursor.execute(sql_create)
connection.commit()
