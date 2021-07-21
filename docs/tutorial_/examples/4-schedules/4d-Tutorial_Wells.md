---
jupyter:
  jupytext:
    comment_magics: true
    split_at_heading: true
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.11.4
  kernelspec:
    display_name: 'Python 3.8.8 64-bit (''dcapy'': conda)'
    name: python3
---

# Forecast Scheduling - Wells and WellsGroup Classes

To take advantage of the scheduling capabilities of covering Wells, Scenarios and peroduction periods, two additional classes must be introduced. Like `Scenario` class they are simple wrappers that allows to group multiple scenarios instances on a `Well` instances and multiple `Wells` into a `WellsGroup` Instance. 


```python
import os

from dcapy import dca
from dcapy.schedule import Scenario, Period, Well, WellsGroup
from dcapy.cashflow import CashFlowParams

import numpy as np 
import pandas as pd
from datetime import date, timedelta
import matplotlib.pyplot as plt
import seaborn as sns 
from scipy import stats
import seaborn as sns
```

Create two scenarios by changing simple parameters that can be denominated as decision variables

```python
#First Period First Scenario

p1a_dict = {
    'name':'pdp',
    'dca': {
        'ti':'2021-01-01',
        'di':0.025,
        'freq_di':'M',
        'qi':1500,
        'b':0,
    },
    'start':'2021-01-01',
    'end':'2040-01-01',
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

#Second Period First Scenario

p2a_dict = {
    'name':'pud',
    'dca': {
        'ti':'2022-01-01',
        'di':0.3,
        'freq_di':'A',
        'qi':3000,
        'b':0,
    },
    'start':'2022-01-01',
    'end':'2040-01-01',
    'freq_output':'A',
    'rate_limit': 100,
    'depends':{'period':'pdp'},
    'cashflow_params':[
        {
            'name':'wo',
            'value':-500000,
            'periods':1,
            'target':'capex'
        },
        {
            'name':'abandon',
            'value':-300000,
            'periods':-1,
            'target':'capex'
        },
    ]
}
s1_dict = {
    'name':'first',
    'periods':[
        p1a_dict,
        p2a_dict
    ],
}
s1 = Scenario(**s1_dict)
```

```python
#First Period Second Scenario

p1b_dict = {
    'name':'pdp',
    'dca': {
        'ti':'2021-01-01',
        'di':0.025,
        'freq_di':'M',
        'qi':1500,
        'b':0,
    },
    'start':'2021-01-01',
    'end':'2040-01-01',
    'freq_output':'A',
    'rate_limit': 700,
    'cashflow_params':[
        {
            'name':'capex',
            'value':{
                'date':['2021-01-01'],
                'value':[-6500000]
                },
            'target':'capex'
        }
    ]
}

#Second Period Second Escenario

p2b_dict = {
    'name':'pud',
    'dca': {
        'ti':'2022-01-01',
        'di':0.3,
        'freq_di':'A',
        'qi':3000,
        'b':0,
    },
    'start':'2022-01-01',
    'end':'2040-01-01',
    'freq_output':'A',
    'rate_limit': 100,
    'depends':{'period':'pdp'},
    'cashflow_params':[
        {
            'name':'wo',
            'value':-50000,
            'periods':1,
            'target':'capex'
        },
        {
            'name':'abandon',
            'value':-300000,
            'periods':-1,
            'target':'capex'
        },
    ]
}

s2_dict = {
    'name':'second',
    'periods':[
        p1b_dict,
        p2b_dict
    ],
}
s2 = Scenario(**s2_dict)
```

There have been created two scenarios with more than one period where the dependency option have been set. 

There are capex and rate limit differences between the scenarios.

As seen, there are different ways of creating the instances due to the versatility that Pydantic gives to not only to create but validate them. In this case, the cashflow parameters that applies for all the scenarios can be set once when creating the `Well` instance and passing a list `CashflowParams` directly.

```python
well_1 = Well(
    name = 'well_1',
    scenarios = [s1,s2],
    cashflow_params = [
        CashFlowParams(
            name = 'fix_opex',
            value = -5000,   # 5 KUSD per well per month
            freq_value = 'M',
            target = 'opex',
        ),
        CashFlowParams(
            name = 'var_opex',
            value = -10,     # 10 USD per barrel of oil
            multiply = 'oil_volume',
            target = 'opex',
        ),
        CashFlowParams(
            name = 'Sells',
            value = 50,     # 50 USD per barrel of oil
            multiply = 'oil_volume',
            target = 'income',
            wi = 0.94,
        )
    ]
)

print(type(well_1))
```

Generate Forecast and plot it!

```python
well1_forecast = well_1.generate_forecast(freq_output='A')

#Plot results by scenario
sns.lineplot(data=well1_forecast, x=well1_forecast.index.to_timestamp(), y='oil_rate', hue='scenario')
```

Generate Cashflows

```python
well1_cashflow = well_1.generate_cashflow(freq_output='A')
print(len(well1_cashflow))
```

```python
print(well1_cashflow[0].fcf())
```

```python

fig, ax = plt.subplots(2,1, figsize=(10,15))

well1_cashflow[0].plot(ax=ax[0])
well1_cashflow[1].plot(ax=ax[1])

ax[0].set_title('First Scenario')
ax[0].set_title('Second Scenario')
```

```python
well_1.npv([0.1], freq_rate='A', freq_cashflow='A')
```

```python
well_1.npv([0.1], freq_rate='A', freq_cashflow='A').reset_index().to_dict()

```

```python
from dcapy.auth import Credential
```

```python
cred = Credential(token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImIyZDQ5NjMyLWM0MzEtNDAzYi04OTEyLTJiZGIyOTA3NTMxNCIsIm5hbWUiOiJTYW50aWFnbyIsImxhc3RfbmFtZSI6IkN1ZXJ2byIsInVzZXJuYW1lIjoic2N1ZXJ2bzkxIiwiZXhwIjoxNjI2ODM1OTY1fQ.GN6-UQIHM0OSRt3hlGTYIQObUVqGl7m6Kh1JczUwf_w')
```

```python
well_2 = Well(
    name = 'well_1',
    scenarios = [s1,s2],
    cashflow_params = [
        CashFlowParams(
            name = 'fix_opex',
            value = -5000,   # 5 KUSD per well per month
            freq_value = 'M',
            target = 'opex',
        ),
        CashFlowParams(
            name = 'var_opex',
            value = -10,     # 10 USD per barrel of oil
            multiply = 'oil_volume',
            target = 'opex',
        ),
        CashFlowParams(
            name = 'Sells',
            value = 50,     # 50 USD per barrel of oil
            multiply = 'oil_volume',
            target = 'income',
            wi = 0.94,
        )
    ]
)
well_2.insert_db(cred, 'well-Cash tutorial')
```

```python
well_2.generate_forecast()
well_2.generate_cashflow()
```

```python
well_2.update_db(cred, description='well-Cash tutorial_update')
```

```python
wd = Well()

wd.get_db('c6e698a3-cc55-4805-ad38-1027f4001951',cred)
```

```python

```
