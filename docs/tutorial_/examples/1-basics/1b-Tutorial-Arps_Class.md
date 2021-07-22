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

# Dcapy -  Arps Class

This section introduces the `Arps` class which is a *'wrapper'* for the Arps Function seen in the previous section. It add certain functionalities to the forecast estimation, like dates, plots, cumulatives, water calculation.  

By taking advantage of python Object-Oriented functionalities it is very convinient to define a class with the required properties to make an Arps declination analysis. With the class are defined methods that help to make the forecast in a very flexible way. That means you can make different kind of forecast from the same Arps declination parameters. 

```python
import os
from dcapy import dca
import numpy as np 
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import seaborn as sns 
from scipy import stats
np.seterr(divide='ignore')
```

## Arps Class

As seen in the previous section to define an Arps declination object you must have a *Decline rate* `di`, *b coefficient* `b`, *Initial Time* `Ti`, *Initial rate* `qi`. With these properties you can create a simple Arps Class. The time array to make a forecast can vary depending on the horizon time, frequency or rates limits. In that way you can estimate multiple forecast from the same class depending on the needs. 

Let's define a simple Aprs class by providing the same properties we have been seen. 
We can add a property we had not seen so far which is useful when we incorporates different time units. The units of the declination rate `di`. So far we can handle three periods of time. Days, Months and years.

```python
# Define a Simple Arps Class

a1 = dca.Arps(
    ti = 0,
    di = 0.03,
    qi = 1500,
    b = 0,
    freq_di='M'
)

print(a1)

```

We have defined a Arps class with a nominal declination rate of 0.03 monthly. This is usefull if you want to make a forecast on differnt time basis. You can get forecast on daily, monthly or annual basis from the same Arps Class

### Time basis 

When the time is defined with integers, they can represent any of the periods available (days, months or years). For example you can define forecast on daily basis each day or on daily basis each month. Next are the different ways you can create forecast

By calling the method `forecast` and providing either a time array or the start and end, and the frequencies of the output it returns a pandas DataFrame with the forecast with some useful metadata

```python
print('Calculate Daily Basis each day')

fr = a1.forecast(start=0,end=1095,freq_input='D',freq_output='D')
print(fr)
```

Let's Plot it instead

```python
print('Calculate Daily Basis each day - Plot')

fr = a1.plot(start=0,end=1095,freq_input='D',freq_output='D')
```

Generate forecast with more periods alternatives

```python
print('Calculate Daily Basis each Month')

fr = a1.forecast(start=0,end=1096,freq_input='D',freq_output='M')
print(fr)

a1.plot(start=0,end=1096,freq_input='D',freq_output='M',rate_kw=dict(palette=['darkgreen'],linestyle='-',linewidth=5))
```

```python
print('Calculate Daily Basis each Year')

fr = a1.forecast(start=0,end=1096,freq_input='D',freq_output='A')
print(fr)

#Assign to a matplotlib axes
fig, ax = plt.subplots(figsize=(10,7))

a1.plot(start=0,end=1096,freq_input='D',freq_output='A',cum=True,rate_kw = {'palette':['green']}, ax=ax)
ax.set_title('Arps Forecast on Daily Basis each year', fontsize=14)
ax.set_xlabel('Time [days]', fontsize=10)
ax.set_ylabel('Oil Rate [bbl/d]', fontsize=10)
```

```python
print('Calculate Monthly Basis each Month')

fr = a1.forecast(start=0,end=37,freq_input='M',freq_output='M')
print(fr)

fig, ax = plt.subplots()
a1.plot(start=0,end=37,freq_input='M',freq_output='M',rate_kw=dict(palette=['darkgreen'],linestyle='-.',linewidth=2))
ax.set_title('Arps Forecast on Month Basis each month', fontsize=14)
ax.set_xlabel('Time [months]', fontsize=10)
ax.set_ylabel('Oil Rate [bbl/d]', fontsize=10)

```

```python
print('Calculate Monthly Basis each Year')

fr = a1.forecast(start=0,end=37,freq_input='M',freq_output='A')
print(fr)

fig, ax = plt.subplots()
a1.plot(start=0,end=37,freq_input='M',freq_output='A',rate_kw=dict(palette=['darkgreen'],linestyle='-.',linewidth=2))
ax.set_title('Arps Forecast on Month Basis each year', fontsize=14)
ax.set_xlabel('Time [months]', fontsize=10)
ax.set_ylabel('Oil Rate [bbl/d]', fontsize=10)
```

```python
print('Calculate Annual Basis each Year')

fr = a1.forecast(start=0,end=4,freq_input='A',freq_output='A')
print(fr)

fig, ax = plt.subplots()
a1.plot(start=0,end=4,freq_input='A',freq_output='A',rate_kw=dict(palette=['darkgreen'],linestyle='-.',linewidth=2))
ax.set_title('Arps Forecast on Annual Basis each year', fontsize=14)
ax.set_xlabel('Time [Years]', fontsize=10)
ax.set_ylabel('Oil Rate [bbl/d]', fontsize=10)
```

## Multiple Values 

You may have noticed that the pandas dataframe returned with the forecast has a column name *iteration*. As we have defined so far a singles parameters for the Arps class it is created only one iteration. 

You can declare Multiple values for any of the Arps parameters and they will result on Multiple iteration on the pandas dataframe.


```python
# Define an Arps Class with multiple values

a2 = dca.Arps(
    ti = 0,
    di = 0.03,
    qi = [1500,1000,500],
    b = 0,
    freq_di='M'
)

print(a2)
```

```python
print('Calculate Monthly Basis each month - Multiple parameters')

fr = a2.forecast(start=0,end=12,freq_input='M',freq_output='M')
print(fr)

fig, ax = plt.subplots()
a2.plot(start=0,end=12,freq_input='M',freq_output='M')

```

### Estimate Water Rate.

You can add water columns for the returning forecast by providing either a fluid rate or water cut. When any of them is provided the function assumes they are constant and the water estimation are simple substraction.



```python
# Define an Arps Class with multiple values - Fluid rate

a3 = dca.Arps(
    ti = 0,
    di = 0.03,
    qi = [1500,1450],
    b = [0,1],
    freq_di='M', 
    fluid_rate = 2000
)

fr = a3.forecast(start=0,end=12,freq_input='M',freq_output='M')
print(fr)
```

```python
a4 = dca.Arps(
    ti = 0,
    di = 0.03,
    qi = [1500,1450],
    b = [0,1],
    freq_di='M', 
    bsw = 0.6
)

fr = a4.forecast(start=0,end=12,freq_input='M',freq_output='M')
print(fr)
```

Remember you can pass a time list with a custom time distribution

```python
fr = a4.forecast(time_list=[0,2,3,4,6,8,12],freq_input='M',freq_output='M')
print(fr)
```

### Using Arps class with dates

You can also define the Arps class with dates. Like before, the output frequency approach also works

```python
a5 = dca.Arps(
    ti = date(2021,1,1),
    di = [0.03,0.05],
    qi = 1500,
    b = 0,
    freq_di='M', 
    fluid_rate = 2000
)
print(a5)
```

```python
fr = a5.forecast(start=date(2021,1,1),end=date(2021,1,10),freq_output='D')
print(fr)
```

```python
fr = a5.forecast(start=date(2021,1,1),end=date(2022,1,1),freq_output='M')
print(fr)
```

```python
fr = a5.forecast(start=date(2021,1,1),end=date(2026,1,1),freq_output='A')
print(fr)
```

Plot them

```python
a5.plot(start=date(2021,1,1),end=date(2022,1,1),freq_output='M')

```
