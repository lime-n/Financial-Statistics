import re
from numpy import float64
import yaml
import pandas as pd
import pymssql
import re
from collections import defaultdict
# class SqlazurePipeline: set up SQL server
connection = pymssql.connect("xxxt", "xxxr", "xxx2", "xxxr")
cursor = connection.cursor()

#Read the dataframe and store into pandas dataframe
with open('output.txt', 'r') as f:
    data=re.findall(r'\bsymbols:\s*\(\s*{[^{}]*}\s*\)', f.read()) 
    # f.truncate(0)
dt_test=[x.replace('symbols: ', '').replace('(','').replace(')','').replace(';',',').replace('=',':').lstrip().rstrip() for x in data]
result_dict = [yaml.safe_load(x.replace(':', ': ')) for x in dt_test]
sql_dataframe = (pd.DataFrame(result_dict))

#store the columns and data types as a dictionary
sql_data = defaultdict(list)

for keys, values in zip(sql_dataframe.keys(), sql_dataframe.dtypes):
    if values == object:
        sql_data[keys].append("TEXT")
    elif values == float64:
        sql_data[keys].append('FLOAT')

#store the columns and datatypes into one string for querying
ddl = ""
ddi = ""
dds = ""
VALUES = ['%s']*17
for columns, types in sql_data.items():
    for val in types:
        ddl += "`{}` `{}`,".format(columns,val)
        ddi += "`{}`,".format(columns)
for values in VALUES:
    dds += "{},".format(values)

###CREATE an SQL TABLE
# sql_create = "CREATE TABLE `{}` ({})".format('StocksRealTime', ddl)
# sql_create=re.sub(r'`','',sql_create)
# cursor.execute(sql_create)
# connection.commit()

##INSERT an SQL TABLE data
sql_insert = "INSERT INTO `{}` ({}) VALUES ({})".format(
    'StocksRealTime', ddi, dds
    )
sql_insert = re.sub(r'`','',sql_insert)
print(sql_insert)

sql_data = tuple(map(tuple, sql_dataframe.values))
sql_data.to_sql("StocksRealTime", connection)
# for sql_tuple in sql_data:
#     cursor.execute(sql_insert, sql_tuple)
connection.commit()

