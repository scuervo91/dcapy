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

    <class 'dcapy.schedule.schedule.Well'>


Generate Forecast and plot it!


```python
well1_forecast = well_1.generate_forecast(freq_output='A')

#Plot results by scenario
sns.lineplot(data=well1_forecast, x=well1_forecast.index.to_timestamp(), y='oil_rate', hue='scenario')
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)





    <AxesSubplot:xlabel='date', ylabel='oil_rate'>




    
![png](output_8_2.png)
    


Generate Cashflows


```python
well1_cashflow = well_1.generate_cashflow(freq_output='A')
print(len(well1_cashflow))
```

    2



```python
print(well1_cashflow[0].fcf())
```

          Sells_well_1-first-pdp  Sells_well_1-first-pud  total_income  \
    2021            2.218737e+07            0.000000e+00  2.218737e+07   
    2022            1.927792e+07            0.000000e+00  1.927792e+07   
    2023            1.422205e+07            0.000000e+00  1.422205e+07   
    2024            1.050258e+07            0.000000e+00  1.050258e+07   
    2025            7.748154e+06            0.000000e+00  7.748154e+06   
    2026            6.566778e+06            2.223132e+07  2.879810e+07   
    2027            0.000000e+00            3.870068e+07  3.870068e+07   
    2028            0.000000e+00            2.869882e+07  2.869882e+07   
    2029            0.000000e+00            2.126061e+07  2.126061e+07   
    2030            0.000000e+00            1.572160e+07  1.572160e+07   
    2031            0.000000e+00            1.164684e+07  1.164684e+07   
    2032            0.000000e+00            8.636817e+06  8.636817e+06   
    2033            0.000000e+00            6.398312e+06  6.398312e+06   
    2034            0.000000e+00            4.731363e+06  4.731363e+06   
    2035            0.000000e+00            3.505080e+06  3.505080e+06   
    2036            0.000000e+00            2.599222e+06  2.599222e+06   
    2037            0.000000e+00            2.215218e+06  2.215218e+06   
    
          fix_opex_well_1-first-pdp  var_opex_well_1-first-pdp  \
    2021                   -60000.0              -4.720718e+06   
    2022                   -60000.0              -4.101685e+06   
    2023                   -60000.0              -3.025969e+06   
    2024                   -60000.0              -2.234592e+06   
    2025                   -60000.0              -1.648543e+06   
    2026                   -60000.0              -1.397187e+06   
    2027                        0.0               0.000000e+00   
    2028                        0.0               0.000000e+00   
    2029                        0.0               0.000000e+00   
    2030                        0.0               0.000000e+00   
    2031                        0.0               0.000000e+00   
    2032                        0.0               0.000000e+00   
    2033                        0.0               0.000000e+00   
    2034                        0.0               0.000000e+00   
    2035                        0.0               0.000000e+00   
    2036                        0.0               0.000000e+00   
    2037                        0.0               0.000000e+00   
    
          fix_opex_well_1-first-pud  var_opex_well_1-first-pud    total_opex  \
    2021                        0.0               0.000000e+00 -4.780718e+06   
    2022                        0.0               0.000000e+00 -4.161685e+06   
    2023                        0.0               0.000000e+00 -3.085969e+06   
    2024                        0.0               0.000000e+00 -2.294592e+06   
    2025                        0.0               0.000000e+00 -1.708543e+06   
    2026                   -60000.0              -4.730067e+06 -6.247254e+06   
    2027                   -60000.0              -8.234188e+06 -8.294188e+06   
    2028                   -60000.0              -6.106132e+06 -6.166132e+06   
    2029                   -60000.0              -4.523534e+06 -4.583534e+06   
    2030                   -60000.0              -3.345020e+06 -3.405020e+06   
    2031                   -60000.0              -2.478052e+06 -2.538052e+06   
    2032                   -60000.0              -1.837621e+06 -1.897621e+06   
    2033                   -60000.0              -1.361343e+06 -1.421343e+06   
    2034                   -60000.0              -1.006673e+06 -1.066673e+06   
    2035                   -60000.0              -7.457617e+05 -8.057617e+05   
    2036                   -60000.0              -5.530260e+05 -6.130260e+05   
    2037                   -60000.0              -4.713230e+05 -5.313230e+05   
    
          capex_well_1-first-pdp  wo_well_1-first-pud  abandon_well_1-first-pud  \
    2021              -5000000.0                  0.0                       0.0   
    2022                     0.0                  0.0                       0.0   
    2023                     0.0                  0.0                       0.0   
    2024                     0.0                  0.0                       0.0   
    2025                     0.0                  0.0                       0.0   
    2026                     0.0            -500000.0                       0.0   
    2027                     0.0                  0.0                       0.0   
    2028                     0.0                  0.0                       0.0   
    2029                     0.0                  0.0                       0.0   
    2030                     0.0                  0.0                       0.0   
    2031                     0.0                  0.0                       0.0   
    2032                     0.0                  0.0                       0.0   
    2033                     0.0                  0.0                       0.0   
    2034                     0.0                  0.0                       0.0   
    2035                     0.0                  0.0                       0.0   
    2036                     0.0                  0.0                       0.0   
    2037                     0.0                  0.0                 -300000.0   
    
          total_capex           fcf       cum_fcf  
    2021   -5000000.0  1.240666e+07  1.240666e+07  
    2022          0.0  1.511623e+07  2.752289e+07  
    2023          0.0  1.113608e+07  3.865897e+07  
    2024          0.0  8.207992e+06  4.686697e+07  
    2025          0.0  6.039611e+06  5.290658e+07  
    2026    -500000.0  2.205084e+07  7.495742e+07  
    2027          0.0  3.040649e+07  1.053639e+08  
    2028          0.0  2.253269e+07  1.278966e+08  
    2029          0.0  1.667708e+07  1.445737e+08  
    2030          0.0  1.231658e+07  1.568903e+08  
    2031          0.0  9.108793e+06  1.659990e+08  
    2032          0.0  6.739197e+06  1.727382e+08  
    2033          0.0  4.976969e+06  1.777152e+08  
    2034          0.0  3.664690e+06  1.813799e+08  
    2035          0.0  2.699318e+06  1.840792e+08  
    2036          0.0  1.986196e+06  1.860654e+08  
    2037    -300000.0  1.383895e+06  1.874493e+08  



```python

fig, ax = plt.subplots(2,1, figsize=(10,15))

well1_cashflow[0].plot(ax=ax[0])
well1_cashflow[1].plot(ax=ax[1])

ax[0].set_title('First Scenario')
ax[0].set_title('Second Scenario')
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])





    Text(0.5, 1.0, 'Second Scenario')




    
![png](output_12_2.png)
    



```python
well_1.npv([0.1], freq_rate='A', freq_cashflow='A')
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>npv</th>
      <th>iteration</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0.1</th>
      <td>1.110744e+08</td>
      <td>0</td>
    </tr>
    <tr>
      <th>0.1</th>
      <td>1.184897e+08</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>




```python
well_1.npv([0.1], freq_rate='A', freq_cashflow='A').reset_index().to_dict()

```




    {'index': {0: 0.10000000000000009, 1: 0.10000000000000009},
     'npv': {0: 111074433.96223314, 1: 118489715.93003416},
     'iteration': {0: 0, 1: 1}}




```python
from dcapy.auth import Credential
```


```python
cred = Credential(token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImIyZDQ5NjMyLWM0MzEtNDAzYi04OTEyLTJiZGIyOTA3NTMxNCIsIm5hbWUiOiJTYW50aWFnbyIsImxhc3RfbmFtZSI6IkN1ZXJ2byIsInVzZXJuYW1lIjoic2N1ZXJ2bzkxIiwiZXhwIjoxNjI2OTI2NTk3fQ.n3HuheJvoQKF9RNKTC9gEstC449EWd2qsrWR7f30V2U')
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
well_2.insert_db(cred, 'well-Cash tutorial1')
```




    '1b1ecf58-e252-4ea0-9ac3-66bee10cc050'




```python
_ = well_2.generate_forecast()
_ = well_2.generate_cashflow()
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)



```python
well_2.update_db(cred, description='well-Cash tutorial_update1')
```




    '1b1ecf58-e252-4ea0-9ac3-66bee10cc050'




```python
wd = Well()

wd.get_db('1b1ecf58-e252-4ea0-9ac3-66bee10cc050',cred)
```


```python
type(wd)
```




    dcapy.schedule.schedule.Well




```python

```
