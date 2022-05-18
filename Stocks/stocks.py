import re
from numpy import float64, int64, nan
import yaml
from pprint import pprint

from subprocess import STDOUT, check_call as x
import os
import pandas as pd
import time

from multiprocessing import Process
import re
import jsonlines
from sqlalchemy import create_engine
from collections import defaultdict
import pyodbc

"""
Extract real-time stock prices for the IOS app StockSpy.
Steps:
1. Execute programme and store the output into a txt file.
2. Filter the data with Regex and extract the required information.
3. Store the data into SQL database.
"""

user = 'bxxx'
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


cmd = [r'/Applications/StockSpy Realtime Stocks Quote.app/Contents/MacOS/StockSpy Realtime Stocks Quote']
text_file = ['bitcoin1.txt','bitcoin2.txt','bitcoin3.txt','bitcoin4.txt']

#set a global variable
global running  
running = True

def append_output_executable(cmd):
    #place the function in a loop for muiltiprocessing
    while running:
        i = '1234'
        for num in i:
            try: #append the .exe output to multiple files 
                with open(os.devnull, 'rb') as DEVNULL, open('bitcoin{}.txt'.format(num), 'ab') as f:
                    data=x(cmd,  stdout=f, stderr=STDOUT, timeout=3600)
            except:
                pass


def write_truncate_output(text):
    while running:
        #run the function after 1 hour and 1 minute
        time.sleep(3660)
        with open(text, 'r+') as f:
            data=f.read() 
            f.truncate(0)
        #regex to extract just the dict-like objects
        stocks = re.findall(r'\bsymbols:\s*\(\s*{[^{}]*}\s*\)', data)
        #clean the data
        dt_test=[x.replace('symbols: ', '').replace('(','').replace(')','').replace(';',',').replace('=',':').lstrip().rstrip() for x in stocks]
        #safely load the dict-like object into an actual pyton dictionary
        result_dict = [yaml.safe_load(x.replace(':', ': ')) for x in dt_test]
        sql_dataframe = (pd.DataFrame(result_dict))

        #write the file for additional storage
        json_data = "stocks2.jl"
        with jsonlines.open(json_data, 'a') as f:
            f.write(sql_dataframe)

        #store the columns and data types as a dictionary
        sql_data = defaultdict(list)
        #dafely convert the data types into SQL types
        for keys, values in zip(sql_dataframe.columns, sql_dataframe.dtypes):
            if values == object:
                sql_data[keys].append("TEXT")
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


        #INSERT a SQL TABLE data
        sql_insert = "INSERT INTO `{}` ({}) VALUES ({})".format(
            'StocksRealTime', ddi, dds
            )
        sql_insert = re.sub(r'`','',sql_insert)

        reg_comma = ['(?<=^.{234}).{1}', ',(?=[^,]*$)']
        sql_insert_clean=[]

        #clean the data
        for comma in reg_comma:
            x=re.compile("(%s|%s)" % (reg_comma[0],reg_comma[1])).sub('',sql_insert)
            sql_insert_clean.append(x)

        float_cols = sql_dataframe.select_dtypes(include=['float64']).columns
        str_cols = sql_dataframe.select_dtypes(include=['object']).columns
        int_cols = sql_dataframe.select_dtypes(include=['int64']).columns

        sql_dataframe.loc[:, float_cols] = sql_dataframe.loc[:, float_cols].fillna(0)
        sql_dataframe.loc[:, str_cols] = sql_dataframe.loc[:, str_cols].fillna('')
        sql_dataframe.loc[:, int_cols] = sql_dataframe.loc[:, int_cols].fillna('')

        #store into SQL
        sql_dataframe.to_sql('StocksRealTime', con=engine,index=False, if_exists='append')


if __name__ == '__main__':

    execute_process = Process(target = append_output_executable, args=(cmd[0],))
    
    for text in text_file:

        output_process = Process(target = write_truncate_output, args=(text,))
        
        output_process.start()
        
    execute_process.start()
    
    execute_process.join()
    output_process.join()
        

