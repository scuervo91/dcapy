import os
path = os.path.abspath(os.path.join('..'))
print(path)
import sys
sys.path.insert(0,path)
from dcapy import dca
import numpy as np 
import pandas as pd
from datetime import date
def main():
    
    print('Example Arps Class')
    #print(dca.time_converter_matrix)
    qi = 5000
    di = 0.3
    b = 0
    ti = 0
    di_f = 'A'
    print(f' ->qi {qi}\n -> di {di}\n b {b}\n ->di_freq {di_f}')  
    dc = dca.Arps(qi,di,b,ti,freq_di=di_f)
    
    print('Calculate Daily Basis each day')
    print(dc.forecast(start=0,end=31,freq_input='D',freq_output='D'))

    print('Calculate Daily Basis each Month')
    print(dc.forecast(start=0,end=360,freq_input='D',freq_output='M'))
    
    print('Calculate Daily Basis each Year')
    print(dc.forecast(start=0,end=1000,freq_input='D',freq_output='A'))
    
    print('Calculate Monthly Basis each Month')
    print(dc.forecast(start=0,end=12,freq_input='M',freq_output='M'))

    print('Calculate Monthly Basis each Year')
    print(dc.forecast(start=0,end=36,freq_input='M',freq_output='A'))
    
    print('Calculate Monthly Basis each Year')
    print(dc.forecast(start=0,end=36,freq_input='M',freq_output='A'))
    
    print('Calculate Year Basis each Year')
    print(dc.forecast(start=0,end=15,freq_input='A',freq_output='A'))
    
    print('Calculate Year Basis each Year - Rate Limit')
    print(dc.forecast(start=0,end=15,freq_input='A',freq_output='A',rate_limit=500))
    
if __name__ == '__main__':
    main()