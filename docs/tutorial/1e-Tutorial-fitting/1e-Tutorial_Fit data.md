# Fitting real data to Arps and Wor Models

Most of the time you have to get the declination parameters by fitting the real data. Both Arps and Wor classes have the method `fit` to excecute the workflow. 


## Fit to Arps 

Import a sample production from a csv file and plot it.


```python
import pandas as pd
import numpy as np
from dcapy import dca
from dcapy.filters import exp_wgh_avg
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date, datetime
np.seterr(divide='ignore')
```




    {'divide': 'warn', 'over': 'warn', 'under': 'ignore', 'invalid': 'warn'}




```python
prod = pd.read_csv('prod.csv')
prod['date'] = pd.to_datetime(prod['date'], format='%Y-%m-%d')
print(prod.head())
print(prod.tail())
print(prod.shape)

```

            date    prod
    0 2015-07-01  338.58
    1 2015-07-02  339.75
    2 2015-07-03  349.65
    3 2015-07-04  357.48
    4 2015-07-05  344.16
              date   prod
    602 2017-02-27  97.47
    603 2017-02-28  97.56
    604 2017-03-01  97.65
    605 2017-03-02  97.74
    606 2017-03-03  97.92
    (607, 2)


It is highly recommended to convert the date data to a datetime pandas format before pass it to the `fit` method


```python
fig, ax = plt.subplots(figsize=(10,7))
prod.plot(x='date',y='prod', kind='scatter',ax=ax)
```




    <AxesSubplot:xlabel='date', ylabel='prod'>




    
![svg](output_5_1.svg)
    


You can create an empty `Arps` instance and just define the frequency of the decline rate. As the input data format is a datetime, the `freq_di` is set on 'D'

By calling `fit` method with the dataframe containing the production information you have to indicate the columns name containing the time and rate.


```python
d1 = dca.Arps(freq_di='D')
d1.fit(df=prod,time='date',rate='prod')
d1
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/filters/filters.py:63: RuntimeWarning: invalid value encountered in true_divide
      y = np.nan_to_num(yw / bias_correction)





    Declination 
     Ti: 2015-07-02 
     Qi: 405.9511186841064 bbl/d 
     Di: 0.00618008412058399 D 
     b: 0.9999999999737121



The method tries to fit the data to Arps equation by tunning in this case the parameters `di` and `b`.

Once the data is fitted the instances is populated with those parameters and you can start to make forecast


```python
fig, ax = plt.subplots(figsize=(10,7))

prod.plot(x='date',y='prod', kind='scatter',ax=ax)

d1.plot(ax=ax, start=date(2015,7,1), end=date(2017,2,28))
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:82: RuntimeWarning: invalid value encountered in multiply
      return f*(g-h)



    
![svg](output_9_1.svg)
    


### Fit data with a fix `b` value

If you'd like to fit the data specifically with a certain value of `b` parameter, you can declare it in the `fit`  method


```python
d2 = dca.Arps(freq_di='D')
filters = d2.fit(df=prod,time='date',rate='prod', b=1)
print(d2)

fig, ax = plt.subplots(figsize=(10,7))

prod.plot(x='date',y='prod', kind='scatter',ax=ax)

d2.plot(ax=ax, start=date(2015,7,1), end=date(2017,2,28))

```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/filters/filters.py:63: RuntimeWarning: invalid value encountered in true_divide
      y = np.nan_to_num(yw / bias_correction)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:82: RuntimeWarning: invalid value encountered in multiply
      return f*(g-h)
    Declination 
     Ti: 2015-07-02 
     Qi: 405.9511411187894 bbl/d 
     Di: 0.006180084996307258 D 
     b: 1.0



    
![svg](output_11_1.svg)
    


## Data Filtering

When passing data to the `fit` method it automatically filter production greater than zero to used by the fitting function. 




```python
fig, ax = plt.subplots(figsize=(10,7))
prod.plot(x='date',y='prod', kind='scatter',ax=ax)

d2.plot(ax=ax, start=date(2015,7,1), end=date(2017,2,28))
filters.loc[filters['filter']==1].plot(x='time',y='oil_rate', kind='scatter',ax=ax, color='r')
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:82: RuntimeWarning: invalid value encountered in multiply
      return f*(g-h)





    <AxesSubplot:xlabel='time', ylabel='oil_rate'>




    
![svg](output_13_2.svg)
    


If you want to apply another filter to remove possible outliers or anomaly data, you can use the `zscore` filter in the `dcapy.filters` module


```python
from dcapy.filters import zscore
```


```python
d3 = dca.Arps(freq_di='D')
f = d3.fit(df=prod,time='date',rate='prod', filter=zscore)
d3
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/filters/filters.py:63: RuntimeWarning: invalid value encountered in true_divide
      y = np.nan_to_num(yw / bias_correction)





    Declination 
     Ti: 2015-07-02 
     Qi: 405.6180677993501 bbl/d 
     Di: 0.0061525623163733705 D 
     b: 0.9999999999999508




```python
fig, ax = plt.subplots(figsize=(10,7))
prod.plot(x='date',y='prod', kind='scatter',ax=ax)

d3.plot(ax=ax, start=date(2015,7,1), end=date(2017,2,28))
f.loc[f['filter']==1].plot(x='time',y='oil_rate', kind='scatter',ax=ax, color='r')
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:82: RuntimeWarning: invalid value encountered in multiply
      return f*(g-h)





    <AxesSubplot:xlabel='time', ylabel='oil_rate'>




    
![svg](output_17_2.svg)
    



```python
d3 = dca.Arps(freq_di='D')
f = d3.fit(df=prod,time=prod.index.values,rate='prod', filter=zscore)
d3
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/filters/filters.py:63: RuntimeWarning: invalid value encountered in true_divide
      y = np.nan_to_num(yw / bias_correction)





    Declination 
     Ti: 1 
     Qi: 405.6331402648868 bbl/d 
     Di: 0.006143434026879475 D 
     b: 0.9948666436238093



## Fit to WOR

Load the production data and estimate some parameters like Wor and Cumulative oil production



```python
prod_wor = pd.read_csv('prod_wor.csv')
prod_wor['date'] = pd.to_datetime(prod_wor['date'], format='%Y-%m-%d')
prod_wor['fluid'] = prod_wor['oil'] + prod_wor['water']
prod_wor['wor'] = prod_wor['water'] / prod_wor['oil']
prod_wor['np'] = prod_wor['oil'].cumsum()
print(prod_wor.head())
print(prod_wor.tail())
print(prod_wor.shape)
```

            date    oil    water    fluid        wor      np
    0 1990-08-29  52.90  1065.25  1118.15  20.137051   52.90
    1 1990-08-30  66.10  1548.10  1614.20  23.420575  119.00
    2 1990-08-31  85.35  1654.45  1739.80  19.384300  204.35
    3 1990-09-01  79.95  1686.05  1766.00  21.088806  284.30
    4 1990-09-02  84.15  1791.65  1875.80  21.291147  368.45
              date    oil    water    fluid        wor        np
    235 1991-04-21  47.65  2552.65  2600.30  53.570829  19241.25
    236 1991-04-22  47.15  2552.35  2599.50  54.132556  19288.40
    237 1991-04-23  46.30  2554.65  2600.95  55.176026  19334.70
    238 1991-04-24  46.30  2554.65  2600.95  55.176026  19381.00
    239 1991-04-25  45.05  2557.15  2602.20  56.762486  19426.05
    (240, 6)


When plotting you can identify two periods of production when the fluid rate is constant. We can extract the production profile after 1990-12. 


```python
fig, ax = plt.subplots(2,2,figsize=(15,10))
prod_wor.plot(x='date',y='oil', kind='scatter', ax=ax[0,0], color='g')
prod_wor.plot(x='date',y='wor', kind='scatter', ax=ax[0,1], color='b')
prod_wor.plot(x='date',y='np', kind='scatter', ax=ax[1,0], color='darkgreen')
prod_wor.plot(x='date',y='fluid', kind='scatter', ax=ax[1,1], color='grey')

ax[0,1].set_yscale('log')
```


    
![svg](output_22_0.svg)
    



```python
prod_w1 = prod_wor[prod_wor['date']>=pd.Timestamp(1990,12,12)]
print(prod_w1.head())
```

              date    oil    water    fluid        wor        np
    105 1990-12-12  97.70  2508.00  2605.70  25.670420  10121.30
    106 1990-12-13  97.35  2508.65  2606.00  25.769389  10218.65
    107 1990-12-14  96.20  2504.20  2600.40  26.031185  10314.85
    108 1990-12-15  96.20  2506.10  2602.30  26.050936  10411.05
    109 1990-12-16  95.45  2507.30  2602.75  26.268203  10506.50


The Wor fitting workflow is similar to Arps. Create an empty Wor instance, call the `fit` method with with the columns required.


```python
wor_dec = dca.Wor()
wor_dec.fit(df=prod_w1[['date','oil','water']], time='date',oil_rate='oil',water_rate='water')
print(wor_dec)
```

    bsw=0.9600600634231139 slope=8.181985964097696e-05 fluid_rate=2596.3974074074076 ti=datetime.date(1990, 12, 12) seed=None gor=None glr=None


Plot the results


```python
wor_forecast=wor_dec.forecast(start=date(1990,12,12),end=date(1991,4,25), cum_i=10121)
fig, ax = plt.subplots(2,1, figsize=(10,10))

prod_wor.plot(x='date',y='oil', kind='scatter', ax=ax[0], color='g')
sns.lineplot(data=wor_forecast.to_timestamp().reset_index(), x='date',y='oil_rate', ax=ax[0])


prod_wor.plot(x='np',y='wor', kind='scatter', ax=ax[1], color='b')
sns.lineplot(data=wor_forecast.to_timestamp().reset_index(), x='oil_cum',y='wor', ax=ax[1])
ax[1].set_yscale('log')

ax[0].grid()
ax[1].grid()
```


    
![svg](output_27_0.svg)
    



```python

```
