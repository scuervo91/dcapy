# Dcapy -  First Steps

In this firts section is introduced the basic classes and functions to make Forecast by applying the Arps equations


```python
import os
from dcapy import dca
import numpy as np 

```



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



### Exponential b = 0, Examples

The time array used with this function is relative to a Initial Time which is always 0

Inside the `dcapy.dca` module there are the functions required to estimate the declination given those parameters. 


```python
time1 = np.arange(10)
qi1 = 500
di1 = 0.03
dca.arps_exp_rate(time1,qi1,di1)
```




    array([500.        , 485.22276677, 470.88226679, 456.96559264,
           443.46021836, 430.35398821, 417.63510571, 405.29212299,
           393.31393053, 381.68974717])



Cumulative volume can be calculated  for any timestep


```python
dca.arps_exp_cumulative(time1,qi1,di1)

```




    array([   0.        ,  492.57444086,  970.59110693, 1434.48024548,
           1884.65938805, 2321.53372625, 2745.49647648, 3156.92923383,
           3556.20231556, 3943.67509439])



You may notice that two important things when reviewing the results. 

1. You have to be aware of the units. As this equations are generic the units must be consistent according you are expecting the results will look like. In other words, here the time units may be days, months, years or whatever you like, hence the declination rate you set is interpreted with respect that unit period of time.
2. As the Arps equations are continious, there is no time discretization (so far) when estimating the cumulative production. As you can see at time 0 the cumulative is also 0. This approach helps to estimate at any time the rate or cumulative very fast as they not depend on previous data. (They are continious)

### Hyperbolic 0<b<1, Examples

Like Exponential case, the Hyperbolic equations works in the same way with the difference you have to set the `b` coefficient


```python
b = 0.5
dca.arps_hyp_rate(time1,qi1,di1,b)
```




    array([500.        , 485.33087432, 471.29795457, 457.86497562,
           444.99822001, 432.66630611, 420.83999663, 409.49202514,
           398.59693878, 388.13095538])




```python
dca.arps_hyp_cumulative(time1,qi1,di1,b,ti=0)
```




    array([  -0.        ,  492.61083744,  970.87378641, 1435.40669856,
           1886.79245283, 2325.58139535, 2752.29357798, 3167.42081448,
           3571.42857143, 3964.75770925])



### Armonic, Examples




```python
b = 1
dca.arps_hyp_rate(time1,qi1,di1,b)
```




    array([500.        , 485.4368932 , 471.69811321, 458.71559633,
           446.42857143, 434.7826087 , 423.72881356, 413.2231405 ,
           403.22580645, 393.7007874 ])




```python
dca.arps_arm_cumulative(time1,qi1,di1,b,ti=0)
```




    array([   0.        ,  492.64670403,  971.14846873, 1436.29493735,
           1888.81142178, 2329.36570625, 2758.57397463, 3177.00599348,
           3585.18966028, 3983.61500784])



## High-level Functions



Although the above functions are available in the module, they are not expected to be used by the user. These are low-level functions that are wrapped into other high-level functions that provide more functionalities.

`arps_forecast` and `arps_cumulative` are the wrapper functions that independently of the b, It internally uses the appropiate equation. Next are the replicates of the initial example using the high-level functions. 



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

    Examples Arps Forecast function - Exponential
    [500.         485.22276677 470.88226679 456.96559264 443.46021836]


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

    Examples Arps Forecast function - Armonic
    [500.         485.4368932  471.69811321 458.71559633 446.42857143]


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

    Examples Arps Forecast function - Exponential, Armonic & Hyperbolic
    [[500.         500.         500.        ]
     [485.22276677 485.33087432 485.4368932 ]
     [470.88226679 471.29795457 471.69811321]
     [456.96559264 457.86497562 458.71559633]
     [443.46021836 444.99822001 446.42857143]]


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

    Examples Arps Forecast function - More than one Parameters with multiple values
    [[1500.         1000.          500.          250.        ]
     [1455.66830032  970.55417193  485.38414057  242.7184466 ]
     [1412.64680038  942.18423029  471.49991315  235.8490566 ]
     [1370.89677791  914.84334525  458.29609778  229.35779817]
     [1330.38065508  888.48704792  445.72604011  223.21428571]
     [1291.06196464  863.07309523  433.74716057  217.39130435]
     [1252.90531712  838.56134359  422.32052508  211.86440678]
     [1215.87636896  814.91363042  411.4104683   206.61157025]
     [1179.9417916   792.09366324  400.98426232  201.61290323]
     [1145.06924151  770.06691564  391.01182445  196.8503937 ]]


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

    Examples Arps Forecast function - Multiple time arrays
    [[500.                  nan]
     [485.22276677          nan]
     [470.88226679          nan]
     [456.96559264          nan]
     [443.46021836          nan]
     [430.35398821 500.        ]
     [417.63510571 485.22276677]
     [405.29212299 470.88226679]
     [393.31393053 456.96559264]
     [381.68974717 443.46021836]
     [370.40911034 430.35398821]]


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

    Examples Arps Forecast function -  Multiple Ti values
    [[500.                  nan]
     [485.22276677          nan]
     [470.88226679          nan]
     [456.96559264          nan]
     [443.46021836          nan]
     [430.35398821 500.        ]
     [417.63510571 485.22276677]
     [405.29212299 470.88226679]
     [393.31393053 456.96559264]
     [381.68974717 443.46021836]
     [370.40911034 430.35398821]]


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

    Examples Arps Cumulative function - Single values
    [   0.          985.14888172 1941.18221386 2868.96049096 3769.31877609
     4643.0674525  5490.99295296 6313.85846766 7112.40463111 7887.35018877]



```python
print('Examples Arps Cumulative function - More than one Parameters with multiple values')

time1 = np.arange(10)
qi1 = [1500,1000,500, 250],
di1 = 0.03
b1 = [0,0.25,0.75,1]
f1 = dca.arps_cumulative(time1,qi1,di1,b1)
print(f1)
```

    Examples Arps Cumulative function - More than one Parameters with multiple values
    [[    0.            -0.            -0.             0.        ]
     [ 1477.72332257   985.18541255   492.62883611   246.32335201]
     [ 2911.77332079  1941.46694484   971.0121016    485.57423437]
     [ 4303.44073644  2869.89686578  1435.85541579   718.14746868]
     [ 5653.97816414  3771.48180653  1887.81550453   944.40571089]
     [ 6964.60117875  4647.18505318  2327.50451494  1164.68285313]
     [ 8236.48942944  5497.92870867  2755.49387077  1379.28698731]
     [ 9470.78770149  6324.59573242  3172.31772543  1588.50299674]
     [10668.60694667  7128.03186523  3578.47606162  1792.59483014]
     [11831.02528316  7909.04744689  3974.43747962  1991.80750392]]



```python
print('Examples Arps Cumulative function -  Multiple Ti values')

time1 = [0,1,2,3,4,5,6,7,8,9,10]
qi1 = 500,
di1 = 0.03
b1 = 0 
f1 = dca.arps_cumulative(time1,qi1,di1,b1,ti=[0,5])
print(f1)
```

    Examples Arps Cumulative function -  Multiple Ti values
    [[   0.                   nan]
     [ 492.57444086           nan]
     [ 970.59110693           nan]
     [1434.48024548           nan]
     [1884.65938805           nan]
     [2321.53372625    0.        ]
     [2745.49647648  492.57444086]
     [3156.92923383  970.59110693]
     [3556.20231556 1434.48024548]
     [3943.67509439 1884.65938805]
     [4319.69632197 2321.53372625]]


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

    Examples Arps Forecast function -  Multiple Ti values
    [500.         485.22276677 470.88226679 456.96559264 443.46021836
     430.35398821 417.63510571 405.29212299 393.31393053 381.68974717
     370.40911034]
    Estimate the time when the rate is 400
    [7]

