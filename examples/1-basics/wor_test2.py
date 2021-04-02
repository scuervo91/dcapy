
import os
from dcapy import dca
import numpy as np 
import pandas as pd
from datetime import date

def main():
    
    print('Examples Wor Object')

    
    bsw = 0.5
    slope = [3.5e-6,3e-6,4e-6]
    ti =  date(2021,1,1)

    w1 = dca.Wor(bsw=bsw,slope=slope,ti=ti, glr=0.3, fluid_rate = 1000,)

    print(w1.json())

    data = dict(
        start = date(2021,1,1),
        end = date(2021,1,10),
        freq_input = 'D',
        freq_output = 'D',
        rate_limit = 480,
    )
    print(w1.forecast(**data))
    w1.forecast(**data).to_csv('wor_test_2.csv')
    
    


if __name__ == '__main__':
    main()