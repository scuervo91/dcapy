import os
path = os.path.abspath(os.path.join('..'))
print(path)
import sys
sys.path.insert(0,path)
from dcapy import dca
from dcapy.models import CashFlow, ChgPts, CashFlowGroup, CashFlowModel, CashFlowInput, Period

import numpy as np 
import pandas as pd
from cashflows2.timeseries import cashflow
from datetime import date


chgpts1 = ChgPts(time = '2021-07-01', value = -2000)

csh = CashFlow(
    name = 'capex',
    const_value = 0,
    start = '2021-01-01',
    end = '2021-12-01',
    freq = 'M',
    chgpts = [chgpts1]
	)

#print(csh.dict())
#print(csh.cashflow())


chgpts2 = [chgpts1,ChgPts(time = '2022-07-01', value = -4000),ChgPts(time = '2025-07-01', value = -6000)]
csh2 = CashFlow(
    name = 'capex1',
    const_value = 0,
    start = '2021-01-01',
    end = '2028-12-01',
    freq = 'A',
    chgpts = chgpts2
	)

#print(csh2.dict())
#print(csh2.cashflow())


### case
data = {
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
    'cashflow_in':{
    	'capex':-2e6,
    	'oil_var_opex': -10,
    	'fix_opex':-20000,
    	'abandonment':[
            {
    		'time':'2021-04-01',
    		'value':'-4e5'
    	   },
            {
            'time':'2021-06-01',
            'value':'-4.5e5'
           },
        ]
    }

}


p1 = Period(**data)

p1.generate_forecast()
p1.generate_cashflow()

print(p1.forecast)
print(p1.cashflow_out.capex.cashflows[1].cashflow())

#print(cashflow(const_value=[-2000.0]*6, start=date(2021,1,1), freq='M'))


