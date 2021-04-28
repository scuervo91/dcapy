import os
path = os.path.abspath(os.path.join('..'))
print(path)
import sys
sys.path.insert(0,path)
from dcapy import dca
from dcapy.models import CashFlow, ChgPts, CashFlowModel, Period

import numpy as np 
import pandas as pd
from datetime import date

### case
data = {
	'name':'pdp',
	'dca': {
        'ti':'2021-01-01',
        'bsw':0.3,
        'slope':[1e-5,1e-7],
        'fluid_rate':1000,
        'gor':0.300
    },
    'start':'2021-01-01',
    'end':'2021-06-01',
    'freq_input':'D',
    'freq_output':'M',
    'cashflow_params':
        [
            {
                'name':'oil_var_opex',
                'const_value':7,
                'multiply':'oil_volume',
                'target':'opex'
            },
            {
                'name':'income',
                'array_values':{
                    'date':['2021-01-01','2021-02-01','2021-03-01','2021-04-01','2021-05-01','2021-06-01'],
                    'value':[38,42,45,50,55,39]
                },
                'multiply':'oil_volume',
                'target':'income'
            }
        ]
}


p1 = Period(**data)

p1.generate_forecast()
p1.generate_cashflow()

#p1.forecast.df()[['oil_rate','water_rate','gas_rate']].to_csv('wor_period_forecast1.csv')
#p1.cashflow[0].fcf().to_csv('wor_period_cashflow0.csv')
#p1.cashflow[1].fcf().to_csv('wor_period_cashflow1.csv')

print(p1.forecast.df()['oil_rate'].values)
print(p1.forecast.df()['water_rate'].values)
print(p1.forecast.df()['gas_rate'].values)

print(p1.cashflow[0].fcf()['fcf'].values)
print(p1.cashflow[1].fcf()['fcf'].values)
#print(p1.forecast.df())
#print(p1.generate_cashflow().income[0].get_cashflow(freq_output='A'))

#print(cashflow(const_value=[-2000.0]*6, start=date(2021,1,1), freq='M'))


