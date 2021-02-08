import os
path = os.path.abspath(os.path.join('..'))
print(path)
import sys
sys.path.insert(0,path)
from dcapy import dca
from dcapy.models import CashFlow, ChgPts, CashFlowModel, CashFlowInput, Period, Scenario

import numpy as np 
import pandas as pd
from datetime import date

### case
period1 = {
	'name':'pdp',
	'dca': {
        'ti':'2021-01-01',
        'di':0.3,
        'freq_di':'A',
        'qi':800,
        'b':0,
        'fluid_rate':1000
    },
    'start':'2021-01-01',
    'end':'2021-06-01',
    'freq_input':'M',
    'freq_output':'M',
    'cashflow_params':{
        'params_list' : [
            {
                'name':'oil_var_opex',
                'const_value':7,
                'multiply':'oil_rate',
                'target':'opex'
            },
            {
                'name':'oil_price',
                'array_values':{
                    'date':['2021-01-01','2021-02-01','2021-03-01','2021-04-01','2021-05-01','2021-06-01'],
                    'value':[38,42,45,50,55,39]
                },
                'multiply':'oil_volume',
                'target':'income'
            }
        ]}
}

### case
period2 = {
    'name':'pud',
    'dca': {
        'ti':'2021-07-01',
        'di':0.3,
        'freq_di':'A',
        'qi':1200,
        'b':0,
        'fluid_rate':1000
    },
    'start':'2021-07-01',
    'end':'2021-12-01',
    'freq_input':'M',
    'freq_output':'M',
    'cashflow_params':{
        'params_list' : [
            {
                'name':'oil_var_opex',
                'const_value':7,
                'multiply':'oil_rate',
                'target':'opex'
            },
            {
                'name':'oil_price',
                'array_values':{
                    'date':['2021-01-01','2021-02-01','2021-03-01','2021-04-01','2021-05-01','2021-06-01'],
                    'value':[38,42,45,50,55,39]
                },
                'multiply':'oil_volume',
                'target':'income'
            }
        ]}
}


scenario = {
    'name':'test_scenario',
    'periods':[period1,period2]
}

s1 = Scenario(**scenario)

print(s1.generate_forecast())


#o1.generate_forecast()


#print(p1.forecast)
#print(p1.generate_cashflow().income[0].get_cashflow(freq_output='M'))

#print(cashflow(const_value=[-2000.0]*6, start=date(2021,1,1), freq='M'))
