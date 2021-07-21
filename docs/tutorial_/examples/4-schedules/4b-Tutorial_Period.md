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

# Forecast Scheduling - Period Class

As described before on the Introduction, the `Period` class is the one that contains all the parameters to define the forecast models for the rest of the Wrappers (`Scenario`, `Well`, `WellsGroup`). 

```python
from dcapy import dca
from dcapy.schedule import Period

import numpy as np 
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import seaborn as sns 
from scipy import stats
import seaborn as sns
```

## Create a dca Model

```python
dec_model = dca.Arps(
    ti = date(2021,1,1),
    di = 0.3,
    freq_di = 'A',
    qi = [80,100],
    b = 0,
    fluid_rate = 250
)

#Create forecast
print(dec_model.forecast(start = date(2021,1,1), end=date(2021,6,1), freq_output='M'))
```

## Create a `Period` Instance

To create a `Period` Intance you have to provide a ``dca` model (either `Arps` or `Wor`), range dates and frequency output. These parameters are the same you would provide to generate a forecast by using only the dca model only. However, later in the notebook and next pages is shown what additional parameters can be defined when creating Period Instance.

The first way to create an instance is by providing the right key arguments. `Pydantic` is used to validate the input user.


### Example. Create instance

```python
p1 = Period(
    name = 'Period-1',
    dca = dec_model,
    start = date(2021,1,1),
    end = date(2021,6,1),
    freq_output='M'
)

print(type(p1))
```

```python
print(p1.json(exclude_unset=True, indent=2))
```

### Wrong input passed

```python

try:
    p1 = Period(
        name = 'Period-1',
        dca = 'string',
        start = date(2021,1,1),
        end = date(2021,6,1),
        freq_output='BM'
    )
except Exception as e:
    print(e)

```

<!-- #region -->
The wrong user input trigger the Pydantic validation error indicating the `dna` is not valid neither does `freq output`


Pydantic allows to create instances by passing a dictionary and it will validate even the deeper instances, for example the dca model
<!-- #endregion -->

### Example create Period by passing dictionary

```python
p1_dict = {
    'name':'Period-1',
    'dca': {
        'ti':'2021-01-01',
        'di':0.3,
        'freq_di':'A',
        'qi':[80,100],
        'b':0,
        'fluid_rate':250
    },
    'start':'2021-01-01',
    'end':'2022-01-01',
    'freq_output':'M'
}

p1 = Period(**p1_dict)

print(p1)
```

It automatically validates dates even they are strings, floats and deeper instances like dca.Arps

If an input error is made on dca model the validator will also detect where is the mistake.


To generate the forecast of the period just call the method `generate_forecast`

```python
print(p1.generate_forecast())
```

### Add Rate limit

```python
p1_dict = {
    'name':'Period-1',
    'dca': {
        'ti':'2021-01-01',
        'di':0.3,
        'freq_di':'A',
        'qi':[80,100],
        'b':0,
        'fluid_rate':250
    },
    'start':'2021-01-01',
    'end':'2022-01-01',
    'freq_output':'M',
    'rate_limit': 70
}

p1 = Period(**p1_dict)

print(p1.generate_forecast())
```

```python
### Probabilistic Variables

```

```python
p1_dict = {
    'name':'Period-1',
    'dca': {
        'ti':'2021-01-01',
        'di':0.3,
        'freq_di':'A',
        'qi':{'dist':'norm','kw':{'loc':90, 'scale':10}},
        'b':0,
        'fluid_rate':250
    },
    'start':'2021-01-01',
    'end':'2022-01-01',
    'freq_output':'M',
    'rate_limit': 70,
    'iter':20
}

p1 = Period(**p1_dict)

prob_forecast = p1.generate_forecast()

fig, ax = plt.subplots(2,1, figsize=(7,10))
sns.lineplot(data=prob_forecast, x = prob_forecast.index.to_timestamp(), y='oil_rate', ax=ax[0])
sns.lineplot(data=prob_forecast, x = prob_forecast.index.to_timestamp(), y='oil_rate',hue='iteration', ax=ax[1])
```

## Add Cashflow Parameters

Adding Cashflow parameters is allowed with the purpose of creating a cashflow model for the period. 

The `Period` instance receive a list of `CashFlowParams` instances. That means you can add as many parameters as you want. 

To define a basic cashflow parameter you have to provide the next key-arguments:

1. Name for the cashflow
2. Value (single value, list of values, date-value pair, probabilistic variable or a Wiener Proccess)
3. Target (It defines if the resulting cashflow is income, capex or opex)
3. Multiply (It defines if the value must be multiplied by a given column of the forecast)

Let's define some cashflow parameters when creating a period:


```python
p1cash_dict = {
    'name':'Period-1',
    'dca': {
        'ti':'2021-01-01',
        'di':0.3,
        'freq_di':'A',
        'qi':800,
        'b':0,
        'fluid_rate':250
    },
    'start':'2021-01-01',
    'end':'2022-01-01',
    'freq_output':'M',
    'rate_limit': 70,

    #Cashflow params keyword. It accept a list
    'cashflow_params':[
            {
                'name':'fix_opex',
                'value':-5000,       #Fix opex of U$ 5000 monthly
                'target':'opex',     #The cashflow generated is going to be an Opex in the cashflow model
                'freq_value':'M'     #The frequency of the value is in Months
            },
            {
                'name':'var_opex',
                'value':-12,    #Variable Opex 12 USD/bbl of oil
                'target':'opex', #The cashflow generated is going to be an Opex in the cashflow model
                'multiply':'oil_volume'  #Multiply the 12 USD/bbl by the oil_volume Column which is the monthly cumulative oil
            },
            {
                'name':'income',
                'value':60,             #Oil price 60 usd/bbl
                'target':'income',      #The cashflow generated is going to be an Income in the cashflow model
                'multiply':'oil_volume',  # Multiply the 60 USD/bbl by the oil_volume column
                'wi':0.9, #working Interest. In this case represent 10% royalties 
            },
            {
                'name':'capex_drill',
                'value':-3000000,             # 3 Million dollar of capex
                'target':'capex',      #The cashflow generated is going to be aCapex in the cashflow model
                'periods':1,  # repeat the value only one period
            }
        ]

}

p1_cash = Period(**p1cash_dict)
```

### Generate forecast

??? note
    Default working interest for a `CashFlowParameters` is 1

```python
forecast = p1_cash.generate_forecast()
print(forecast)
```

### Generate a cashflow

When calling the `generate_cashflow` method it return a list of `CashFlowModel`

```python
cf_model = p1_cash.generate_cashflow()

for i in cf_model:
    print(type(i))
```

```python
print(cf_model[0].fcf())
```

# Make a plot of the Cashflow Model

```python
fig, ax= plt.subplots(figsize=(15,7))

cf_model[0].plot(cum=True, ax=ax)
```

```python
## Estimate the NPV and IRR
```

```python
p1_cash.npv([0.1,0.15], freq_rate='A', freq_cashflow='M')
```

```python
p1_cash.irr()
```

## Cashflow with Multiple Iterations

Whether you define multiple or Probabilistic variables when cashflow parameters are defined for the `Period` the same amount of cash flow models are generated as forecast iterations are.



```python
p2cash_dict = {
    'name':'Period-1',
    'dca': {
        'ti':'2021-01-01',
        'di':0.3,
        'freq_di':'A',
        'qi':[800,700,500],
        'b':[0,0.5,1],
        'fluid_rate':250
    },
    'start':'2021-01-01',
    'end':'2022-01-01',
    'freq_output':'M',
    'rate_limit': 70,

    #Cashflow params keyword. It accept a list
    'cashflow_params':[
            {
                'name':'fix_opex',
                'value':-5000,       #Fix opex of U$ 5000 monthly
                'target':'opex',     #The cashflow generated is going to be an Opex in the cashflow model
                'freq_value':'M'     #The frequency of the value is in Months
            },
            {
                'name':'var_opex',
                'value':-12,    #Variable Opex 12 USD/bbl of oil
                'target':'opex', #The cashflow generated is going to be an Opex in the cashflow model
                'multiply':'oil_volume'  #Multiply the 12 USD/bbl by the oil_volume Column which is the monthly cumulative oil
            },
            {
                'name':'income',
                'value':60,             #Oil price 60 usd/bbl
                'target':'income',      #The cashflow generated is going to be an Income in the cashflow model
                'multiply':'oil_volume',  # Multiply the 60 USD/bbl by the oil_volume column
                'wi':0.9, #working Interest. In this case represent 10% royalties 
            },
            {
                'name':'capex_drill',
                'value':-3000000,             # 3 Million dollar of capex
                'target':'capex',      #The cashflow generated is going to be aCapex in the cashflow model
                'periods':1,  # repeat the value only one period
            }
        ]

}

p2_cash = Period(**p2cash_dict)

p2_forecast = p2_cash.generate_forecast()
p2_cashflow = p2_cash.generate_cashflow()


```

```python
n_cashflows = len(p2_cashflow)

fig, ax= plt.subplots(n_cashflows,2,figsize=(15,7))

for i in range(n_cashflows):
    forecast_iteration = p2_forecast[p2_forecast['iteration']==i] 
    sns.lineplot(data =forecast_iteration, x=forecast_iteration.index.to_timestamp(), y='oil_rate', ax=ax[i,0])
    p2_cashflow[i].plot(cum=True, ax=ax[i,1])
```

```python
p2_cash.npv([0.1,0.17], freq_rate='A', freq_cashflow='M')
```

## Multiple Cashflow Params

Cashflow parameters values can also be evaluated with multiple iterations. 

??? note
    When creating multiple iterations either on dca or cashflow parameters, the number of iterations must be the same in other to create element-wise models. 

```python
p3cash_dict = {
    'name':'Period-1',
    'dca': {
        'ti':'2021-01-01',
        'di':0.3,
        'freq_di':'A',
        'qi':700,
        'b':0,
        'fluid_rate':250
    },
    'start':'2021-01-01',
    'end':'2022-01-01',
    'freq_output':'M',
    'rate_limit': 70,

    #Cashflow params keyword. It accept a list
    'cashflow_params':[
            {
                'name':'fix_opex',
                'value':-5000,       #Fix opex of U$ 5000 monthly
                'target':'opex',     #The cashflow generated is going to be an Opex in the cashflow model
                'freq_value':'M'     #The frequency of the value is in Months
            },
            {
                'name':'var_opex',
                'value':-12,    #Variable Opex 12 USD/bbl of oil
                'target':'opex', #The cashflow generated is going to be an Opex in the cashflow model
                'multiply':'oil_volume'  #Multiply the 12 USD/bbl by the oil_volume Column which is the monthly cumulative oil
            },
            {
                'name':'income',
                'value':[20,30,40,60,80],             #Oil price 60 usd/bbl
                'target':'income',      #The cashflow generated is going to be an Income in the cashflow model
                'multiply':'oil_volume',  # Multiply the 60 USD/bbl by the oil_volume column
                'wi':0.9, #working Interest. In this case represent 10% royalties 
            },
            {
                'name':'capex_drill',
                'value':-3000000,             # 3 Million dollar of capex
                'target':'capex',      #The cashflow generated is going to be aCapex in the cashflow model
                'periods':1,  # repeat the value only one period
            }
        ]

}
p3_cash = Period(**p3cash_dict)

p3_forecast = p3_cash.generate_forecast()
p3_cashflow = p3_cash.generate_cashflow()
```

```python
n_cashflows = len(p3_cashflow)

fig, ax= plt.subplots(n_cashflows,1,figsize=(15,15), gridspec_kw={'hspace':0.4})

for i in range(n_cashflows):
    p3_cashflow[i].plot(cum=True, ax=ax[i])
```

Here, the same forecast was used to create five different cashflow models according with the iterations defined on the Oil price

```python
p3_cash.npv([0.1], freq_rate='A', freq_cashflow='M')
```

## Export the model

All classes in `dcapy` are based on Pydantic, hence they can be directly exported to a dictionary, json and further to yml

#### Export to Dictionary

```python
print(p3_cash.dict(exclude={'forecast','cashflow'}, exclude_unset=True))
```

#### Export to json

```python
print(p3_cash.json(exclude={'forecast','cashflow'}, exclude_unset=True))
```

```python
p3_cash.tree()
```

#### Export to cloud

Dcapy has integrated connection with an API hosted on [Heroku](https://www.heroku.com) that allows to save your models on the cloud. This allows you to create, update and delete your models on a remote database whicgh is accesible throught a single account (with Oauth2 Authentication).

```python
from dcapy.auth import Credential
```

```python
cred = Credential(token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImIyZDQ5NjMyLWM0MzEtNDAzYi04OTEyLTJiZGIyOTA3NTMxNCIsIm5hbWUiOiJTYW50aWFnbyIsImxhc3RfbmFtZSI6IkN1ZXJ2byIsInVzZXJuYW1lIjoic2N1ZXJ2bzkxIiwiZXhwIjoxNjI1MTgxMjcwfQ.AxtaSaN5wotlUj_R5o-nXjCO-NK4S_VYYHY07vbeyoM')
```

```python
p3_cash.insert_db(cred, 'Period-Cash tutorial')
```

```python

```
