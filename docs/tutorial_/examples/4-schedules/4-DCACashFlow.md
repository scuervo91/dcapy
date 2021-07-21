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
    name: python388jvsc74a57bd0607220d9aa50002d928e15b68ce75e93a4d790d4e944ca3137991ee1264619da
---

```python
import os
from dcapy import dca
from dcapy.models import CashFlow, ChgPts, CashFlowModel, Period, Scenario, CashFlowParams
from dcapy.weiner import Weiner

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
                'value':-5.000,
                'target':'opex',
            },
            {
                'name':'var_opex',
                'value':-0.005,
                'iter':1,
                'target':'opex',
                'multiply':'oil_volume'
            },
            {
                'name':'income',
                'value':Weiner(initial_condition=60,ti='2021-01-01', generator={'dist':'norm','kw':{'loc':0.0,'scale':0.02}}),   #[0.060,0.045,0.02],
                'iter':5,
                'target':'income',
                'multiply':'oil_volume'
            },
            {
                'name':'capex',
                'value':{'date':['2021-01-01'],'value':[-70000]},
                'target':'capex'
            }
    ]

CashFlowParams(**cashflow_params[2]).get_value(0,steps=10, freq_output='M')
```

```python
cashflow_params[2]
```

```python
p1_dict = {
    'name':'pdp',
    'dca': {
        'ti':'2021-01-01',
        'di':0.15,
        'freq_di':'A',
        'qi':2500, #{'dist':'norm', 'kw':{'loc':2500,'scale':200}}, #[800,1000],
        'b':0,
        'fluid_rate':5000
    },
    'start':'2021-01-01',
    'end':'2030-01-01',
    'freq_input':'A',
    'freq_output':'A',
    'rate_limit': 80,
    'iter':10,
    'cashflow_params':cashflow_params
}
p1 = Period(**p1_dict)
p1
```

```python
fore1 = p1.generate_forecast()
fore1
```

```python
sns.lineplot(data=fore1,  x=fore1.index.to_timestamp(), y='oil_rate', hue='iteration')
```

```python
c1 = p1.generate_cashflow()
```

```python
c1[0].fcf()
```

```python
p1.npv([0.0])
```

```python
p1.irr(freq_output='A')
```

```python
len(c1)
```

```python

```
