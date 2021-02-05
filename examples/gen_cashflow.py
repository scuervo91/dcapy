import os
path = os.path.abspath(os.path.join('..'))
print(path)
import sys
sys.path.insert(0,path)
from dcapy import dca
from dcapy.models import CashFlow, ChgPts
import numpy as np 
import pandas as pd
from datetime import date


chg_data = {
	'date':['2021-01-01','2021-04-01','2021-07-01','2021-10-01','2022-01-01','2022-04-01','2022-07-01','2022-10-01'],
	'value': [100,500,477,336,855,44,488,414]
}


print('Cashflow with dates')

cash_data = {
	'name':'capex_test',
	'start':'2021-01-01',
	'end':'2022-12-01',
	'freq':'M',
	'chgpts':chg_data
}


print(CashFlow(**cash_data).json())
print(CashFlow(**cash_data).get_cashflow(freq_output = 'A'))

chg_data2 = {
	'date':[2,4,6,8,10,11,13,17],
	'value': [100,500,477,336,855,44,488,414]
}


print('Cashflow with int')

cash_data2 = {
	'name':'capex_test2',
	'start':0,
	'end':20,
	'freq':'M',
	'chgpts':chg_data2
}


print(CashFlow(**cash_data2).json())
print(CashFlow(**cash_data2).get_cashflow())
