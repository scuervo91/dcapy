# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: 'Python 3.8.8 64-bit (''dcapy'': conda)'
#     name: python3
# ---

# # Forecast Scheduling - Scenario Class
#
# The scenario class is just a wrapper to group multiple periods in order to evaluate their production and optionally the economics. 
#
# It adds a feature of *period dependency*. You can set that one period could start its forecast once another ends. 
#
# A forecast can end mainly by three reasons.
#
# + *By Date*: When defining an `end_date` key argument the forecast will stop unless another condition makes it fishish earlier. In any case, the forecast won't go beyond that date.
#
# + *By Rate Limit*: Set the rate limit of oil. If the oil rate reaches that rate limit it automatically will stop.
#
# + *By Cumulative Limit*: Set the Cumulative limit of oil. If the oil cum reaches that cumulative limit it automatically will stop.
#

# +
import os

from dcapy import dca
from dcapy.schedule import Scenario, Period
from dcapy.cashflow import CashFlowParams

import numpy as np 
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import seaborn as sns 
from scipy import stats
import seaborn as sns
# -

# First. Define at least two periods, in this case using the `dca.Wor` models. On each period is defined a cashflow parameter tageting the *capex*. 

# +
p1_dict = {
    'name':'pdp',
    'dca': {
        'ti':'2021-01-01',
        'bsw':0.3,
        'slope':[2e-5,1e-5],
        'fluid_rate':1000,
        'gor':0.3
    },
    'start':'2021-01-01',
    'end':'2022-01-01',
    'freq_input':'M',
    'freq_output':'M',
    'cashflow_params':[
        {
            'name':'capex',
            'value':{
                'date':['2021-01-01'],
                'value':[-5000000]
                },
            'target':'capex'
        }
    ]
}


p1 = Period(**p1_dict)
p1

# +
p2_dict = {
    'name':'pud',
    'dca': {
        'ti':'2022-01-01',
        'bsw':0.3,
        'slope':[2e-5],
        'fluid_rate':1000,
        'gor':0.3
    },
    'start':'2022-01-01',
    'end':'2023-01-01',
    'freq_input':'M',
    'freq_output':'M',
    'cashflow_params':[
        {
            'name':'capex',
            'value':{
                'date':['2022-01-01'],
                'value':[-450000]},
            'target':'capex'
        }
    ]
}

p2 = Period(**p2_dict)
p2
# -

# If casflow parameters are shared across the periods, you can declare a separate cashflow parameters instance and assign them to the scenario instance directly

cashflow_params = [
            {
                'name':'fix_opex',
                'value':-5000,
                'target':'opex',
            },
            {
                'name':'var_opex',
                'value':-5,
                'target':'opex',
                'multiply':'oil_volume',
            },
            {
                'name':'income',
                'value':60,
                'target':'income',
                'multiply':'oil_volume',
            }]
    

s1 = Scenario(
    name='base', 
    periods=[p1,p2], 
    cashflow_params=cashflow_params
)


# Notice each period forecast will produce different amount of iterations. The first period will produce two and the second one. 

s1_f = s1.generate_forecast(freq_output='M')
print(s1_f)

sns.lineplot(data=s1_f, x=s1_f.index.to_timestamp(), y='oil_rate', hue='iteration', style='period')

# When generating the cashflow an internal operation of broadcasting the iterations to produce, in this case, two cashflow models:
#
# + *cashflow model 1*: **Period_1 Iteration_0** + **Period_2 Iteration_0**
# + *cashflow model 2*: **Period_1 Iteration_1** + **Period_2 Iteration_0**

s1_c = s1.generate_cashflow(freq_output='M')
s1_c[1].fcf()

# +
n_cashflows = len(s1_c)

fig, ax= plt.subplots(n_cashflows,1,figsize=(15,7))

for i in range(n_cashflows):
    s1_c[i].plot(cum=True, ax=ax[i])
# -

# ## Period Dependency
#
# As mentioned above, the period Dependency is set by declaring the `depends` keyword on the period instance whose start date depends on other period. 
#
# The next example shows the definitions of two periods which one of them a probabilistic variable has been set. 

# +
p3_dict = {
    'name':'pdp',
    'dca': {
        'ti':'2021-01-01',
        'di':0.025,
        'freq_di':'M',
        'qi':{'dist':'norm', 'kw':{'loc':1500,'scale':200}}, #[800,1000],
        'b':0,
    },
    'start':'2021-01-01',
    'end':'2027-01-01',
    'freq_output':'A',
    'rate_limit': 300,
    'cashflow_params':[
        {
            'name':'capex',
            'value':{
                'date':['2021-01-01'],
                'value':[-5000000]
                },
            'target':'capex'
        }
    ]
}

p4_dict = {
    'name':'pud',
    'dca': {
        'ti':'2022-01-01',
        'di':0.3,
        'freq_di':'A',
        'qi':3000,
        'b':0,
    },
    'start':'2022-01-01',
    'end':'2027-01-01',
    'freq_output':'A',
    'depends':{'period':'pdp'},
    'cashflow_params':[
        {
            'name':'wo',
            'value':-500000,
            'period':1,
            'target':'capex'
        },
        {
            'name':'abandon',
            'value':-300000,
            'period':-1,
            'target':'capex'
        },
    ]
}
# -

# To create a scenario you can also pass a dictionary well structuted instead of create all classes separately, like Periods.
#
# By declaring the `iter` key with an integer the forecast will iterate this number. Notice that, the Period 4 has neither probabilistic variables nor multiple variables however as it depends on the end date of the first. Consequently the function creates the number of iterations required to reach 10 fully iterations that covers both periods.

s2_dict = {
    'name':'Dependency',
    'periods':[
        p3_dict,
        p4_dict
    ],
    'cashflow_params': cashflow_params,
    'iter':10
}
s2_dict

s2 = Scenario(**s2_dict)
print(type(s2))

# Generate Forecast

s2_f = s2.generate_forecast(iter=10, seed=21)
print(s2_f)

sns.lineplot(data=s2_f,  x=s2_f.index.to_timestamp(), y='oil_rate', hue='iteration',style='period')

# +
s2_c = s2.generate_cashflow(freq_output='A')

print(f'Number of cashflow models {len(s2_c)}')
# -

s2_c[0].fcf()

s2.npv([0.15], freq_rate='A',freq_cashflow='A').reset_index().to_dict()

# +
n_cashflows = len(s2_c)

def cell_ijk(cell_id,nx,ny):
    cell_id +=1
    k=np.ceil(cell_id/(nx*ny)).astype(int)
    j=np.ceil((cell_id-(nx*ny)*(k-1))/nx).astype(int)
    i=np.ceil(cell_id-(nx*ny*(k-1))-nx*(j-1)).astype(int)
    return i-1,j-1,k-1

fig, ax= plt.subplots(5,2,figsize=(20,15))

for idx in range(n_cashflows):

    c = cell_ijk(idx+1,5,2)
    print(idx,c)
    s2_c[idx].plot(cum=True, format='m',ax=ax[c[0]-1,c[1]])
# -

from dcapy.auth import Credential

cred = Credential(token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImIyZDQ5NjMyLWM0MzEtNDAzYi04OTEyLTJiZGIyOTA3NTMxNCIsIm5hbWUiOiJTYW50aWFnbyIsImxhc3RfbmFtZSI6IkN1ZXJ2byIsInVzZXJuYW1lIjoic2N1ZXJ2bzkxIiwiZXhwIjoxNjI1MTgxMjcwfQ.AxtaSaN5wotlUj_R5o-nXjCO-NK4S_VYYHY07vbeyoM')

s2.insert_db(cred, 'Scenario-Cash tutorial')

# +
sd = Scenario()

sd.get_db('f1191ba8-9082-4104-9079-9c3c5747e96c',cred)
# -

sd
