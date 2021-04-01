
import os
from dcapy import dca
import numpy as np 
import pandas as pd
def main():
    
    print('Examples Wor Forecast function')
    
    print('Example 1. Single Values')
    time1 = np.arange(0,10,1)
    qi1 = 500,
    slope = 3e-6
    bswi = 0.5
    wori = dca.bsw_to_wor(bswi)
    fluid_rate = [5000]*10
    print(f'initial wor {wori}')
    f1 = dca.wor_forecast(time1,fluid_rate,slope,wori, rate_limit=None, wor_limit=None, cum_limit=1e5)
    print('Forecast Example 1')
    print(f1)
    print(f1.shape)
    print(f1['oil_rate'].values)
    
    f1.to_csv('wor_test_1.csv')
    


if __name__ == '__main__':
    main()