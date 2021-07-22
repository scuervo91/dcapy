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
    display_name: dcapy
    language: python
    name: dcapy
---

```python
import os
from dcapy import dca
from dcapy.models import CashFlow, ChgPts, CashFlowModel, Period, Scenario

import numpy as np 
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import seaborn as sns 
from scipy import stats
import seaborn as sns
```

```python
cashflow_params = [
            {
                'name':'fix_opex',
                'const_value':-5.000,
                'target':'opex',
            },
            {
                'name':'var_opex',
                'const_value':-0.005,
                'target':'opex',
                'multiply':'oil_volume'
            },
            {
                'name':'income',
                'const_value':0.045,
                'target':'income',
                'multiply':'oil_volume'
            },
            {
                'name':'capex',
                'array_values':{'date':[1],'value':[-70000]},
                'target':'capex'
            }
    ]
```

```python
p1_dict = {
    'name':'pdp',
    'dca': {
        'ti':0,
        'di':0.15,
        'freq_di':'A',
        'qi':[2000,1300],#{'dist':'norm', 'kw':{'loc':2500,'scale':200}}, #[800,1000],
        'b':0,
        'fluid_rate':5000
    },
    'start':0,
    'end':20,
    'freq_input':'A',
    'freq_output':'A',
    'rate_limit': 700,
    'iter':10,
    'cashflow_params':cashflow_params
}
p1 = Period(**p1_dict)
p1
```

```python
dca.arps_forecast([0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,8.,9.],800,0.15,0,[0,2])
```

```python
fore1 = p1.generate_forecast()
fore1
```

```python
sns.lineplot(data=fore1,  x=fore1.index, y='oil_rate', hue='iteration')
```

```python
c1 = p1.generate_cashflow()
```

```python
c1[0].fcf()
```

```python
p1.npv([0.10])
```

```python
p1.irr(freq_output='A')
```

# Add another period

```python
p1.get_end_dates()
```

```python
p2_dict = {
    'name':'pdnp',
    'dca': {
        'ti':7,
        'di':0.2,
        'freq_di':'A',
        'qi':1000,#{'dist':'norm', 'kw':{'loc':3500,'scale':200}}, #[800,1000],
        'b':0,
        'fluid_rate':5000
    },
    'start':0,
    'end':20,
    'freq_input':'A',
    'freq_output':'A',
    'rate_limit': 80,
    'iter':14,
    'cashflow_params':cashflow_params,
    'depends':{'period':'pdp'}
}
p2 = Period(**p2_dict)
p2
```

```python
#s1 = Scenario(name='base', periods=[p1,p2])
s1 = Scenario(**{
    'name':'base',
    'periods':[
        p1_dict,
        p2_dict
    ]
})
s1
```

```python
sf1 = s1.generate_forecast(iter=3)
sf1
```

```python
sns.lineplot(data=sf1, x=sf1.index, y='oil_rate', hue='iteration', style='period')
```

```python
s1.forecast.df()
```
