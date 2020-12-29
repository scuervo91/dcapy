
import os
path = os.path.abspath(os.path.join('..'))
print(path)
import sys
sys.path.insert(0,path)
from dcapy import dca
import numpy as np 
import pandas as pd
def main():
    
    print('Examples Arps Forecast function')
    
    print('Example 1. Single Values')
    time1 = [0,2,4,6]
    qi1 = 500,
    di1 = 0.3
    b1 = 0
    print(f' ->Time array {time1}\n ->qi {qi1}\n -> di {di1}\n b {b1}')    
    f1 = dca.arps_forecast(time1,qi1,di1,b1)
    print('Forecast Example 1')
    print(f1)
    print(f1.shape)
    
    
    print('\nExample 2. Multiple values')
    time2 = [0,2,4,6]
    qi2 = [600,500],
    di2 = [0.2,0.3]
    b2 = [0,1]
    print(f' ->Time array {time2}\n ->qi {qi2}\n -> di {di2}\n b {b2}')    
    f2 = dca.arps_forecast(time2,qi2,di2,b2)
    print('Forecast Example 2')
    print(f2)

if __name__ == '__main__':
    main()