import re
from numpy import float64
import yaml
from subprocess import STDOUT, check_call as x
import os
import pandas as pd
import time
import pymssql
from multiprocessing import Process
import re
import jsonlines

cmd = [r'/Applications/StockSpy Realtime Stocks Quote.app/Contents/MacOS/StockSpy Realtime Stocks Quote']
text_file = ['bitcoin1.txt','bitcoin2.txt','bitcoin3.txt','bitcoin4.txt']

def append_output_executable(cmd):
    global running  
    running = True
    while running:
        i = '1234'
        for num in i:
            try: #append the .exe output to multiple files 
                with open(os.devnull, 'rb') as DEVNULL, open('bitcoin{}.txt'.format(num), 'ab') as f:
                    data=x(cmd,  stdout=f, stderr=STDOUT, timeout=2)
            except:
                pass


def write_truncate_output(text):
    global running  
    running = True
    while running:
        time.sleep(10)
        with open(text, 'r+') as f:
            data=f.read() 
            f.truncate(0)
        stocks = re.findall(r'\bsymbols:\s*\(\s*{[^{}]*}\s*\)', data)
        dt_test=[x.replace('symbols: ', '').replace('(','').replace(')','').replace(';',',').replace('=',':').lstrip().rstrip() for x in stocks]
        result_dict = [yaml.safe_load(x.replace(':', ': ')) for x in dt_test]
        print(result_dict)
        jl_file = "stocks.jl"
        with jsonlines.open(jl_file, mode='a') as writer:
            [writer.write(x) for x in result_dict]


        

if __name__ == '__main__':

    execute_process = Process(target = append_output_executable, args=(cmd[0],))
    
    for text in text_file:

        output_process = Process(target = write_truncate_output, args=(text,))
        
        output_process.start()
        
    execute_process.start()
    
    execute_process.join()
    output_process.join()
        

