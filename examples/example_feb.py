import os
path = os.path.abspath(os.path.join('..'))
print(path)
import sys
sys.path.insert(0,path)
from dcapy import dca
import numpy as np 
import pandas as pd



data = {
        'ti':'2021-01-01',
        'di':0.3,
        'freq_di':'A',
        'qi':[800,700],
        'b':0,
        'fluid_rate':1000
}

d1 = dca.Arps(**data)

print(d1)