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
    name: python388jvsc74a57bd0ab24a4a540e2ae850f5bb40f3ff926fc8d1a219d7295b7cc8f5b0a1cbda21e76
---

# Dcapy -  First Steps

In this firts section is introduced the basic classes and functions to make Forecast by applying the Arps equations

```python
import os
from dcapy import dca
import numpy as np 
np.seterr(divide='ignore')

```

<!-- #region -->
## Basics Equations

First Section will explore the Arps Declination Analysis equations. 
Starting from Equations used to calculate rate then cumulatives.

The library numpy is used to performed the majority of operations

### Aprs Equations

Arps proposed that the shape of the production rate vs time can be described mathematically by three types of behavior:

+ **Exponential Decline**: Where `b=0`
+ **Harmonic Decline**: Where `b=1`
+ **Hyperbolic Decline**: Where `0 < b < 1` 

$$
 q_{t}=\frac{q_{i}}{(1+bD_{i}t)^{\frac{1}{b}}}
$$


According to the equations the are four properties you have to provide to make a forecast using Arps equations. 


+ *Decline rate* `di`
+ *b coefficient* `b`
+ *Initial Time* `Ti`
+ *Initial rate* `qi`
+ *Times to make Forecast* `t`


<!-- #endregion -->

### Exponential b = 0, Examples

The time array used with this function is relative to a Initial Time which is always 0

Inside the `dcapy.dca` module there are the functions required to estimate the declination given those parameters. 

```python
time1 = np.arange(10)
qi1 = 500
di1 = 0.03
dca.arps_exp_rate(time1,qi1,di1)
```

Cumulative volume can be calculated  for any timestep

```python
dca.arps_exp_cumulative(time1,qi1,di1)

```

You may notice that two important things when reviewing the results. 

1. You have to be aware of the units. As this equations are generic the units must be consistent according you are expecting the results will look like. In other words, here the time units may be days, months, years or whatever you like, hence the declination rate you set is interpreted with respect that unit period of time.
2. As the Arps equations are continious, there is no time discretization (so far) when estimating the cumulative production. As you can see at time 0 the cumulative is also 0. This approach helps to estimate at any time the rate or cumulative very fast as they not depend on previous data. (They are continious)

### Hyperbolic 0<b<1, Examples

Like Exponential case, the Hyperbolic equations works in the same way with the difference you have to set the `b` coefficient

```python
b = 0.5
dca.arps_hyp_rate(time1,qi1,di1,b)
```

```python
dca.arps_hyp_cumulative(time1,qi1,di1,b,ti=0)
```

### Armonic, Examples



```python
b = 1
dca.arps_hyp_rate(time1,qi1,di1,b)
```

```python
dca.arps_arm_cumulative(time1,qi1,di1,b,ti=0)
```

<!-- #region -->
## High-level Functions



Although the above functions are available in the module, they are not expected to be used by the user. These are low-level functions that are wrapped into other high-level functions that provide more functionalities.

`arps_forecast` and `arps_cumulative` are the wrapper functions that independently of the b, It internally uses the appropiate equation. Next are the replicates of the initial example using the high-level functions. 
<!-- #endregion -->



### Exponential

```python
print('Examples Arps Forecast function - Exponential')

time1 = [0,1,2,3,4]
qi1 = 500,
di1 = 0.03
b1 = 0 
f1 = dca.arps_forecast(time1,qi1,di1,b1)
print(f1)

```

### Armonic

```python
print('Examples Arps Forecast function - Armonic')

time1 = [0,1,2,3,4]
qi1 = 500,
di1 = 0.03
b1 = 1
f1 = dca.arps_forecast(time1,qi1,di1,b1)
print(f1)
```

### Exponential, Armonic & Hyperbolic 

One of the advantages of this function is the ability to accept multiple values of any of the parameters to create multiple scenarios of the forecast. Next we want to estimate the forecast with three different `b` parameter

```python
print('Examples Arps Forecast function - Exponential, Armonic & Hyperbolic')

time1 = [0,1,2,3,4]
qi1 = 500,
di1 = 0.03
b1 = [0,0.5,1]
f1 = dca.arps_forecast(time1,qi1,di1,b1)
print(f1)
```

The result is a 2D numpy array containing three different forecast scenarios (Due to the three `b` values passed). 


The feature to make multiple forecast also applies to the other perameters. 

Note: If there are more than one parameters with multiple values, the number of scenarios must be consistent with a numpy broadcast shape. That means if you provide three values for `b` you need to provide either one or three values for the others to excecute the function.

```python
print('Examples Arps Forecast function - More than one Parameters with multiple values')

time1 = np.arange(10)
qi1 = [1500,1000,500, 250],
di1 = 0.03
b1 = [0,0.25,0.75,1]
f1 = dca.arps_forecast(time1,qi1,di1,b1)
print(f1)
```

Here, there were provided four values for `qi` and `b`. The result is a 2D numpy array with 10 rows (Time) and 4 columns (scenarios). 

Here function excecute the operation like an 'element-wise' for the multiple values. 

+ The first column uses the 1500 as `qi` & 0 as `b`
+ The second column uses the 1000 as `qi` & 0.25 as `b`
+ The thrid column uses the 500 as `qi` & 0.75 as `b`
+ The fourth column uses the 250 as `qi` & 1 as `b`.

They all share the declination parameter 0.3 as `di`


### Multiple initial time values

There is also the posibility to set multiple initial values, which means the forecast would start at different times in the array. 

When you set a time array like all the examples above, you really are setting a delta time array with respect to a **Initial Time** which is by default 0. 

In this case you can define a time delta different from 0 or provide different time arrays. 

The next example defines two scenarios in the time array which the forecast would start at different times.


```python
print('Examples Arps Forecast function - Multiple time arrays')

time1 = [[0,1,2,3,4,5,6,7,8,9,10],[None,None,None,None,None,0,1,2,3,4,5]]
qi1 = 500,
di1 = 0.03
b1 = 0 
f1 = dca.arps_forecast(time1,qi1,di1,b1)
print(f1)
```

The last result can be also achieve by setting two values for `ti` property.

```python
print('Examples Arps Forecast function -  Multiple Ti values')

time1 = [0,1,2,3,4,5,6,7,8,9,10]
qi1 = 500,
di1 = 0.03
b1 = 0 
f1 = dca.arps_forecast(time1,qi1,di1,b1,ti=[0,5])
print(f1)
```

### Arps Cumulative Function

In the same way the `arps_forecast` function works the `arps_cumulative` Function does.

```python
print('Examples Arps Cumulative function - Single values')

time1 = np.arange(10)
qi1 = 1000,
di1 = 0.03
b1 = 0
f1 = dca.arps_cumulative(time1,qi1,di1,b1)
print(f1)
```

```python
print('Examples Arps Cumulative function - More than one Parameters with multiple values')

time1 = np.arange(10)
qi1 = [1500,1000,500, 250],
di1 = 0.03
b1 = [0,0.25,0.75,1]
f1 = dca.arps_cumulative(time1,qi1,di1,b1)
print(f1)
```

```python
print('Examples Arps Cumulative function -  Multiple Ti values')

time1 = [0,1,2,3,4,5,6,7,8,9,10]
qi1 = 500,
di1 = 0.03
b1 = 0 
f1 = dca.arps_cumulative(time1,qi1,di1,b1,ti=[0,5])
print(f1)
```

An additional and usefull function to estimate the time at which the forecast reaches certain rate is also included.

Let's define an Arps forecast

```python
print('Examples Arps Forecast function -  Multiple Ti values')

time1 = [0,1,2,3,4,5,6,7,8,9,10]
qi1 = 500,
di1 = 0.03
b1 = 0 
f1 = dca.arps_forecast(time1,qi1,di1,b1)
print(f1)

print('Estimate the time when the rate is 400')
time_limit = dca.arps_rate_time(qi1,di1,b1,400)
print(time_limit)
```
