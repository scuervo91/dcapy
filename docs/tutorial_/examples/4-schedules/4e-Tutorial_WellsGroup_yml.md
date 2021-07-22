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
    display_name: Python 3
    language: python
    name: python3
---

# Forecast Scheduling - WellsGroup Classes

`WellsGroup` class in the one on top of the others. You can specify a group of `Well` instances that, as seen before, each of them can be groups of scenarios and periods. 

`WellsGroup` has different functionality when evaluating it. Each `Well` part of this have n scenarios which are independent to each other, so if you would like to evaluate all scenarios in all wells you would have to sample one scenario per well and build all the possible combinations. To do this, `Dcapy` uses the functions of [PyDOE2](https://github.com/clicumu/pyDOE2) to generate factorial designs either full-factorial (fullfact) or Generalized Subset Designs (gds). 

On the other hand, in this notebook is applied another convinient way of creating a dca model, which is by providing a yml file. 



```python
import pandas as pd 
import numpy as np 
from dcapy import dca
from dcapy.schedule import Well, Period, Scenario, WellsGroup,  model_from_dict
from dcapy.cashflow import CashFlowParams, CashFlow
from dcapy.wiener import Brownian, GeometricBrownian, MeanReversion
from dcapy.auth import Credential
import seaborn as sns 
from datetime import date
import matplotlib.pyplot as plt
import copy
import yaml
import json
from scipy import stats
```

```python
cred = Credential(token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImIyZDQ5NjMyLWM0MzEtNDAzYi04OTEyLTJiZGIyOTA3NTMxNCIsIm5hbWUiOiJTYW50aWFnbyIsImxhc3RfbmFtZSI6IkN1ZXJ2byIsInVzZXJuYW1lIjoic2N1ZXJ2bzkxIiwiZXhwIjoxNjI2OTI2NTk3fQ.n3HuheJvoQKF9RNKTC9gEstC449EWd2qsrWR7f30V2U')
```

In a file called `YML_example1.yml` is a WellsGroup case where are defined 6 wells. Four of them have one scenario and others two have two scenarios with two Periods. 


```yaml
name: fdp_field
wells:
  DC2:
    name: DC2
    scenarios:
      base:
        name: base
        periods:
          pdp:
            dca:
              bsw: 0.9783
              fluid_rate: 5192.343117182031
              slope: 3.986053847389352e-05
              ti: '2021-04-01'
            end: '2030-12-31'
            freq_input: D
            freq_output: D
            name: pdp
            start: '2021-04-01'
            rate_limit: 50
            cashflow_params:
            - name: capex_abandon
              periods: -1
              target: capex
              value: -200000.0
  DC3:
    name: DC3
    scenarios:
      base:
        name: base
        periods:
          pdp:
            dca:
              bsw: 0.8935
              fluid_rate: 3101.6068269182692
              slope: 1.1341265851141962e-05
              ti: '2021-04-01'
            end: '2030-12-31'
            freq_input: D
            freq_output: D
            name: pdp
            start: '2021-04-01'
            rate_limit: 50
            cashflow_params:
            - name: capex_abandon
              periods: -1
              target: capex
              value: -200000.0
  DC4:
    name: DC4
    scenarios:
      base:
        name: base
        periods:
          pdp:
            dca:
              bsw: 0.9863
              fluid_rate: 7304.560639994402
              slope: 4.086888672335466e-05
              ti: '2021-04-01'
            end: '2030-12-31'
            freq_input: D
            freq_output: D
            name: pdp
            start: '2021-04-01'
            rate_limit: 50
            cashflow_params:
            - name: capex_abandon
              periods: -1
              target: capex
              value: -200000.0
  DC5:
    name: DC5
    scenarios:
      base:
        name: base
        periods:
          pdp:
            dca:
              bsw: 0.9648
              fluid_rate: 5710.712047244095
              slope: 1.9260822570459275e-05
              ti: '2021-04-01'
            end: '2030-12-31'
            freq_input: D
            freq_output: D
            name: pdp
            start: '2020-04-01'
            rate_limit: 50
            cashflow_params:
            - name: capex_abandon
              periods: -1
              target: capex
              value: -200000.0
  well-1:
    name: well-1
    scenarios:
      highfr:
        name: highfr
        periods:
          fm1:
            cashflow_params:
            - name: capex
              periods: 1
              target: capex
              value: -4000000.0
            dca:
              bsw:
                dist: uniform
                kw:
                  loc: 0.4
                  scale: 0.4
              fluid_rate: 6500.0
              slope:
              - 3.0e-05
              ti: '2022-01-01'
            end: '2027-01-01'
            name: fm1
            rate_limit: 200.0
            start: '2022-01-01'
          fm2:
            cashflow_params:
            - name: capex_wo
              periods: 1
              target: capex
              value: -600000.0
            - name: capex_abandon
              periods: -1
              target: capex
              value: -200000.0
            dca:
              bsw:
                dist: uniform
                kw:
                  loc: 0.4
                  scale: 0.4
              fluid_rate: 6500.0
              slope:
              - 5.0e-05
              ti: '2022-01-01'
            depends:
              period: fm1
            end: '2030-01-01'
            name: fm2
            start: '2022-01-01'
      mediumfr:
        name: mediumfr
        periods:
          fm1:
            cashflow_params:
            - name: capex_drill
              periods: 1
              target: capex
              value: -4000000.0
            dca:
              bsw:
                dist: uniform
                kw:
                  loc: 0.4
                  scale: 0.4
              fluid_rate: 3500.0
              slope:
              - 3.0e-06
              ti: '2022-01-01'
            end: '2030-01-01'
            name: fm1
            rate_limit: 200.0
            start: '2022-01-01'
          fm2:
            cashflow_params:
            - name: capex_wo
              periods: 1
              target: capex
              value: -600000.0
            - name: capex_abandon
              periods: -1
              target: capex
              value: -200000.0
            dca:
              bsw:
                dist: uniform
                kw:
                  loc: 0.4
                  scale: 0.4
              fluid_rate: 2500.0
              slope:
              - 5.0e-06
              ti: '2022-01-01'
            depends:
              period: fm1
            end: '2030-01-01'
            name: fm2
            start: '2022-01-01'
  well-2:
    name: well-2
    scenarios:
      highfr:
        name: highfr
        periods:
          fm2:
            cashflow_params:
            - name: capex_drill
              periods: 1
              target: capex
              value: -4000000.0
            dca:
              bsw:
                dist: uniform
                kw:
                  loc: 0.4
                  scale: 0.4
              fluid_rate: 6500.0
              slope:
              - 5.0e-05
              ti: '2022-01-01'
            end: '2030-01-01'
            name: fm2
            rate_limit: 200.0
            start: '2022-01-01'
          fm1:
            cashflow_params:
            - name: capex_wo
              periods: 1
              target: capex
              value: -600000.0
            - name: capex_abandon
              periods: -1
              target: capex
              value: -200000.0
            dca:
              bsw:
                dist: uniform
                kw:
                  loc: 0.4
                  scale: 0.4
              fluid_rate: 6500.0
              slope:
              - 3.0e-05
              ti: '2022-01-01'
            depends:
              period: fm2
            end: '2030-01-01'
            name: fm1
            start: '2022-01-01'
      mediumfr:
        name: mediumfr
        periods:
          fm2:
            cashflow_params:
            - name: capex_drill
              periods: 1
              target: capex
              value: -4000000.0
            dca:
              bsw:
                dist: uniform
                kw:
                  loc: 0.4
                  scale: 0.4
              fluid_rate: 2500.0
              slope:
              - 5.0e-06
              ti: '2022-01-01'
            end: '2030-01-01'
            name: fm2
            rate_limit: 200.0
            start: '2022-01-01'
          fm1:
            cashflow_params:
            - name: capex_wo
              periods: 1
              target: capex
              value: -600000.0
            - name: capex_abandon
              periods: -1
              target: capex
              value: -200000.0
            dca:
              bsw:
                dist: uniform
                kw:
                  loc: 0.4
                  scale: 0.4
              fluid_rate: 3500.0
              slope:
              - 3.0e-06
              ti: '2022-01-01'
            depends:
              period: fm2
            end: '2030-01-01'
            name: fm1
            start: '2022-01-01'
cashflow_params:
- name: fix_opex
  target: opex
  value: -11000.
  freq_value: 'M'
- iter: 1
  multiply: oil_volume
  name: var_opex
  target: opex
  value: -8.0
- multiply: oil_volume
  name: income
  target: income
  value: 
    initial_condition: 60 
    ti: '2021-04-01'
    steps: 11
    generator:
      dist: norm
      kw:
        loc: 0.
        scale: 13.13
    m: 46.77
    eta: 0.112653 
    freq_input: A
  wi: 0.92
- name: buy
  periods: 1
  target: capex
  value: -15500000
  general: True
seed: 21
```


By using a YML parser like [PyYAML](https://pyyaml.org/]) you can convery a *.yml file into a python dictionary.

```python
with open('YML_example1.yml','r') as file:
    case_dict = yaml.load(file)
```

The resulting dictionary, if it has valid values for key arguments, can be passed to a `WellsGroup` directly as made before on the others Schedule Classes

```python
case = WellsGroup(**case_dict)

print(type(case))
```

`WellsGroup` has a method to make the all the factorial combinations of wells scenarios. By calling it with no arguments it creates a full-factorial combinations.

```python
case.insert_db(cred, description='Wellsgroup2')
```

```python
case.update_db(cred, description='Tutorial-Wellsgroup')
```

```python
cased = WellsGroup()

cased.get_db("5f625d24-517d-4890-8067-f8e4da41f779",cred)
```

```python
type(cased)
```

### Get the tree Schema

```python
case.tree()
```

```python
sc = case.scenarios_maker()
sc
```

When the reduced key argument is set, it triggers the Generalized Subset Designed (GSD) (Well explained on [PyDOE2](https://github.com/clicumu/pyDOE2) Documentation).  

### Generate Forecast. 

Those scenarios are a list of dictionary ready to be passed to `generate_forecast` method.

```python
fwn= case.generate_forecast(wells=sc[3],freq_output='A',iter=50, seed=21)

#fwn
sns.lineplot(data=fwn, x=fwn.index.to_timestamp(), y='oil_rate', hue='well',style='scenario',palette='crest')

```

### Generate Cashflow

Once a forecast is generated the `generate_cashflow` method can be called

```python
#cwn= lp.generate_cashflow(wells={'well-1':['mediumfr'],'well-2':['mediumfr']},freq_output='A')
cwn= case.generate_cashflow(wells=sc[3],freq_output='A')
print(len(cwn))
```

Notice that the resulting cashflow for the third scenario is a list of 50 `CashflowModel` due to the `iter` key argument was set with this number. What it does is to generate 50 samples of the probabilistic varibales if they exist in the scenarios and broadcast results with the scenarios that does not have any probabilistic variables. 

Let's see the first cashflow model

```python
fcf_0= cwn[30].fcf()

#Show cashflows in Millons of dollars
print(fcf_0.multiply(1e-6).round(2))
```

Here there are two additional features in the Cashflow Parameter definition. 

1. If you want to assign an additional Capex to the project that does not assigned to a single well but the case itself, for example a Purchase price, infraestructure investment, etc..., you can declare a `CashFlowParam` with the key argument `general` set to **True**. What it does is not to pass the cashflow parameter to each well instead make a *general* cashflow for the model. 

```python
case.cashflow_params[3]
```

2. The income cashflow_param is a Wiener Class, especifically a `MeanReversion` instance. In this case the Oil Price is modeled by the Mean Reversion Model which gives a different time series on each of the 50 iterations.

```python
case.cashflow_params[2]
```

The next plot shows what could be the oil price iterations for the 50 cases

```python
oil_price_model = MeanReversion(
    initial_condition = 66,
    ti = date(2021,1,1),
    generator = {'dist':'norm','kw':{'loc':0,'scale':5.13}},
    m=46.77,
    eta=0.112652,
    freq_input = 'A'
)
oil_price = oil_price_model.generate(12,50, freq_output='A', seed=21)

oil_price.plot(legend=False)
```

Get the Net present value for the 50 cases. Plot the distribution of the scenarios

```python
npv = case.npv([0.15], freq_rate='A', freq_cashflow='A')/1e6

print(npv['npv'].quantile([0.1,0.5,0.9]))

sns.displot(npv['npv'].values, kde=True)
```

Plot any of the cases

```python
cwn[38].plot(cum=True,format='m')
```

```python
with open('YML_example1.yml','r') as file:
    case_dict = yaml.load(file)

lp = WellsGroup(**case_dict)
```

```python
fwn= lp.generate_forecast(wells=sc[3],freq_output='A',iter=2, seed=21)

cwn= lp.generate_cashflow(wells=sc[3],freq_output='A')
```

```python
cwn[0].fcf()['cum_fcf'].values
```

```python
npv_list = []
for i,s in enumerate(sc):

    fwn = case.generate_forecast(wells=s,freq_output='A',iter=50, seed=21)
    cwn = case.generate_cashflow(wells=s,freq_output='A')

    npv = case.npv([0.15], freq_rate='A', freq_cashflow='A')/1e6
    npv['sc'] = i
    npv_list.append(npv)

    npv_df = pd.concat(npv_list, axis=0)
    print(npv['npv'].quantile([0.1,0.5,0.9]))
sns.displot(npv_df, x='npv', hue='sc', multiple="stack")



```

```python

```
