
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
    
    print('Examples Wor Object')

    
    bsw = 0.5
    slope = [3.5e-6,3e-6,4e-6]
    ti =  date(2021,1,1)

    w1 = dca.Wor(bsw=bsw,slope=slope,ti=ti)

    print(w1.json())

    data = dict(
    start = date(2021,1,1),
    end = date(2021,1,10),
    fluid_rate = 1000,
    freq_input = 'D',
    freq_output = 'D',

    )
    print(w1.forecast(**data))


if __name__ == '__main__':
    main()