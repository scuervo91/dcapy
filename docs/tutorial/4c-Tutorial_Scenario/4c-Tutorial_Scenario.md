# Forecast Scheduling - Scenario Class

The scenario class is just a wrapper to group multiple periods in order to evaluate their production and optionally the economics. 

It adds a feature of *period dependency*. You can set that one period could start its forecast once another ends. 

A forecast can end mainly by three reasons.

+ *By Date*: When defining an `end_date` key argument the forecast will stop unless another condition makes it fishish earlier. In any case, the forecast won't go beyond that date.

+ *By Rate Limit*: Set the rate limit of oil. If the oil rate reaches that rate limit it automatically will stop.

+ *By Cumulative Limit*: Set the Cumulative limit of oil. If the oil cum reaches that cumulative limit it automatically will stop.



```python
import os

from dcapy import dca
from dcapy.schedule import Scenario, Period
from dcapy.cashflow import CashFlowParams

import numpy as np 
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import seaborn as sns 
from scipy import stats
import seaborn as sns
```

First. Define at least two periods, in this case using the `dca.Wor` models. On each period is defined a cashflow parameter tageting the *capex*. 


```python
p1_dict = {
    'name':'pdp',
    'dca': {
        'ti':'2021-01-01',
        'bsw':0.3,
        'slope':[2e-5,1e-5],
        'fluid_rate':1000,
        'gor':0.3
    },
    'start':'2021-01-01',
    'end':'2022-01-01',
    'freq_input':'M',
    'freq_output':'M',
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


p1 = Period(**p1_dict)
p1
```




    Period(name='pdp', cashflow_params=[CashFlowParams(name='capex', wi=1.0, periods=None, value=ChgPts(date=[datetime.date(2021, 1, 1)], value=[-5000000.0]), target=<TargetEnum.capex: 'capex'>, multiply=None, agg='mean', depends=False, iter=1, general=False, freq_value=None)], cashflow=None, forecast=None, seed=None, iter=1, ppf=None, description=None, id=None, dca=Wor(bsw=0.3, slope=[2e-05, 1e-05], fluid_rate=1000.0, ti=datetime.date(2021, 1, 1), seed=None, gor=0.3, glr=None), start=datetime.date(2021, 1, 1), end=datetime.date(2022, 1, 1), time_list=None, freq_input=<FreqEnum.M: 'M'>, freq_output=<FreqEnum.M: 'M'>, rate_limit=None, cum_limit=None, depends=None, type=<SchemasEnum.period: 'period'>)




```python
p2_dict = {
    'name':'pud',
    'dca': {
        'ti':'2022-01-01',
        'bsw':0.3,
        'slope':[2e-5],
        'fluid_rate':1000,
        'gor':0.3
    },
    'start':'2022-01-01',
    'end':'2023-01-01',
    'freq_input':'M',
    'freq_output':'M',
    'cashflow_params':[
        {
            'name':'capex',
            'value':{
                'date':['2022-01-01'],
                'value':[-450000]},
            'target':'capex'
        }
    ]
}

p2 = Period(**p2_dict)
p2
```




    Period(name='pud', cashflow_params=[CashFlowParams(name='capex', wi=1.0, periods=None, value=ChgPts(date=[datetime.date(2022, 1, 1)], value=[-450000.0]), target=<TargetEnum.capex: 'capex'>, multiply=None, agg='mean', depends=False, iter=1, general=False, freq_value=None)], cashflow=None, forecast=None, seed=None, iter=1, ppf=None, description=None, id=None, dca=Wor(bsw=0.3, slope=[2e-05], fluid_rate=1000.0, ti=datetime.date(2022, 1, 1), seed=None, gor=0.3, glr=None), start=datetime.date(2022, 1, 1), end=datetime.date(2023, 1, 1), time_list=None, freq_input=<FreqEnum.M: 'M'>, freq_output=<FreqEnum.M: 'M'>, rate_limit=None, cum_limit=None, depends=None, type=<SchemasEnum.period: 'period'>)



If casflow parameters are shared across the periods, you can declare a separate cashflow parameters instance and assign them to the scenario instance directly


```python
cashflow_params = [
            {
                'name':'fix_opex',
                'value':-5000,
                'target':'opex',
            },
            {
                'name':'var_opex',
                'value':-5,
                'target':'opex',
                'multiply':'oil_volume',
            },
            {
                'name':'income',
                'value':60,
                'target':'income',
                'multiply':'oil_volume',
            }]
    
```


```python
s1 = Scenario(
    name='base', 
    periods=[p1,p2], 
    cashflow_params=cashflow_params
)

```

Notice each period forecast will produce different amount of iterations. The first period will produce two and the second one. 


```python
s1_f = s1.generate_forecast(freq_output='M')
print(s1_f)
```

             iteration    oil_rate  water_rate        oil_cum    gas_rate  \
    date                                                                    
    2021-01          0  655.596404  344.403596   20323.488531  196.678921   
    2021-01          1  677.822890  322.177110   21012.509598  203.346867   
    2021-02          0  570.189855  429.810145   36288.804475  171.056957   
    2021-02          1  634.191986  365.808014   38769.885213  190.257596   
    2021-03          0  492.473724  507.526276   51555.489924  147.742117   
    2021-03          1  591.337678  408.662322   57101.353244  177.401304   
    2021-04          0  423.296192  576.703808   64254.375683  126.988858   
    2021-04          1  548.741612  451.258388   73563.601594  164.622484   
    2021-05          0  365.930746  634.069254   75598.228821  109.779224   
    2021-05          1  508.583792  491.416208   89329.699161  152.575138   
    2021-06          0  318.932312  681.067688   85166.198172   95.679694   
    2021-06          1  471.241328  528.758672  103466.939006  141.372398   
    2021-07          0  280.603871  719.396129   93864.918158   84.181161   
    2021-07          1  436.919472  563.080528  117011.442627  131.075841   
    2021-08          0  248.692374  751.307626  101574.381744   74.607712   
    2021-08          1  405.104841  594.895159  129569.692696  121.531452   
    2021-09          0  222.779776  777.220224  108257.775023   66.833933   
    2021-09          1  376.705969  623.294031  140870.871765  113.011791   
    2021-10          0  201.191650  798.808350  114494.716172   60.357495   
    2021-10          1  351.020360  648.979640  151752.502920  105.306108   
    2021-11          0  182.997778  817.002222  119984.649499   54.899333   
    2021-11          1  327.798148  672.201852  161586.447357   98.339444   
    2021-12          0  167.547576  832.452424  125178.624349   50.264273   
    2021-12          1  306.832786  693.167214  171098.263710   92.049836   
    2022-01          0  160.262718  839.737282  125338.887067   48.078815   
    2022-01          1  296.570066  703.429934  171394.833776   88.971020   
    2022-01          0  655.596404  344.403596   20323.488531  196.678921   
    2022-02          0  570.189855  429.810145   36288.804475  171.056957   
    2022-03          0  492.473724  507.526276   51555.489924  147.742117   
    2022-04          0  423.296192  576.703808   64254.375683  126.988858   
    2022-05          0  365.930746  634.069254   75598.228821  109.779224   
    2022-06          0  318.932312  681.067688   85166.198172   95.679694   
    2022-07          0  280.603871  719.396129   93864.918158   84.181161   
    2022-08          0  248.692374  751.307626  101574.381744   74.607712   
    2022-09          0  222.779776  777.220224  108257.775023   66.833933   
    2022-10          0  201.191650  798.808350  114494.716172   60.357495   
    2022-11          0  182.997778  817.002222  119984.649499   54.899333   
    2022-12          0  167.547576  832.452424  125178.624349   50.264273   
    2023-01          0  160.262718  839.737282  125338.887067   48.078815   
    
                 water_cum       bsw       wor     wor_1  delta_time  fluid_rate  \
    date                                                                           
    2021-01   10676.511469  0.344404  0.527821  1.527821         1.0      1000.0   
    2021-01    9987.490402  0.322177  0.475875  1.475875         1.0      1000.0   
    2021-02   22711.195525  0.429810  0.756560  1.756560         1.0      1000.0   
    2021-02   20230.114787  0.365808  0.577364  1.577364         1.0      1000.0   
    2021-03   38444.510076  0.507526  1.034639  2.034639         1.0      1000.0   
    2021-03   32898.646756  0.408662  0.691873  1.691873         1.0      1000.0   
    2021-04   55745.624317  0.576704  1.366647  2.366647         1.0      1000.0   
    2021-04   46436.398406  0.451258  0.823190  1.823190         1.0      1000.0   
    2021-05   75401.771179  0.634069  1.737483  2.737483         1.0      1000.0   
    2021-05   61670.300839  0.491416  0.967229  1.967229         1.0      1000.0   
    2021-06   95833.801828  0.681068  2.139911  3.139911         1.0      1000.0   
    2021-06   77533.060994  0.528759  1.123044  2.123044         1.0      1000.0   
    2021-07  118135.081842  0.719396  2.568406  3.568406         1.0      1000.0   
    2021-07   94988.557373  0.563081  1.289862  2.289862         1.0      1000.0   
    2021-08  141425.618256  0.751308  3.025539  4.025539         1.0      1000.0   
    2021-08  113430.307304  0.594895  1.469646  2.469646         1.0      1000.0   
    2021-09  164742.224977  0.777220  3.492783  4.492783         1.0      1000.0   
    2021-09  132129.128235  0.623294  1.655689  2.655689         1.0      1000.0   
    2021-10  189505.283828  0.798808  3.974506  4.974506         1.0      1000.0   
    2021-10  152247.497080  0.648980  1.850023  2.850023         1.0      1000.0   
    2021-11  214015.350501  0.817002  4.468218  5.468218         1.0      1000.0   
    2021-11  172413.552643  0.672202  2.051770  3.051770         1.0      1000.0   
    2021-12  239821.375651  0.832452  4.972179  5.972179         1.0      1000.0   
    2021-12  193901.736290  0.693167  2.260286  3.260286         1.0      1000.0   
    2022-01  240661.112933  0.839737  5.239754  6.239754         1.0      1000.0   
    2022-01  194605.166224  0.703430  2.371884  3.371884         1.0      1000.0   
    2022-01   10676.511469  0.344404  0.527821  1.527821         1.0      1000.0   
    2022-02   22711.195525  0.429810  0.756560  1.756560         1.0      1000.0   
    2022-03   38444.510076  0.507526  1.034639  2.034639         1.0      1000.0   
    2022-04   55745.624317  0.576704  1.366647  2.366647         1.0      1000.0   
    2022-05   75401.771179  0.634069  1.737483  2.737483         1.0      1000.0   
    2022-06   95833.801828  0.681068  2.139911  3.139911         1.0      1000.0   
    2022-07  118135.081842  0.719396  2.568406  3.568406         1.0      1000.0   
    2022-08  141425.618256  0.751308  3.025539  4.025539         1.0      1000.0   
    2022-09  164742.224977  0.777220  3.492783  4.492783         1.0      1000.0   
    2022-10  189505.283828  0.798808  3.974506  4.974506         1.0      1000.0   
    2022-11  214015.350501  0.817002  4.468218  5.468218         1.0      1000.0   
    2022-12  239821.375651  0.832452  4.972179  5.972179         1.0      1000.0   
    2023-01  240661.112933  0.839737  5.239754  6.239754         1.0      1000.0   
    
             fluid_cum       gas_cum    oil_volume  water_volume   gas_volume  \
    date                                                                        
    2021-01    31000.0   6097.046559  20276.242593  10723.757407  6097.046559   
    2021-01    31000.0   6303.752879  20988.830611  10011.169389  6303.752879   
    2021-02    59000.0  10886.641342  15926.259334  12073.740666  4789.594783   
    2021-02    59000.0  11630.965564  17736.778097  10263.221903  5327.212684   
    2021-03    90000.0  15466.646977  15228.601876  15771.398124  4580.005635   
    2021-03    90000.0  17130.405973  18309.326030  12690.673970  5499.440409   
    2021-04   120000.0  19276.312705  12667.931665  17332.068335  3809.665727   
    2021-04   120000.0  22069.080478  16441.874075  13558.125925  4938.674505   
    2021-05   151000.0  22679.468646  11317.565289  19682.434711  3403.155941   
    2021-05   151000.0  26798.909748  15746.405444  15253.594556  4729.829270   
    2021-06   181000.0  25549.859452   9547.208449  20452.791551  2870.390805   
    2021-06   181000.0  31040.081702  14119.635565  15880.364435  4241.171954   
    2021-07   212000.0  28159.475447   8681.176852  22318.823148  2609.615996   
    2021-07   212000.0  35103.432788  13527.851520  17472.148480  4063.351086   
    2021-08   243000.0  30472.314523   7695.071433  23304.928567  2312.839076   
    2021-08   243000.0  38870.907809  12543.126062  18456.873938  3767.475020   
    2021-09   273000.0  32477.332507   6671.830902  23328.169098  2005.017984   
    2021-09   273000.0  42261.261530  11287.918873  18712.081127  3390.353721   
    2021-10   304000.0  34348.414852   6226.925472  24773.074528  1871.082345   
    2021-10   304000.0  45525.750876  10869.243605  20130.756395  3264.489347   
    2021-11   334000.0  35995.394850   5481.731833  24518.268167  1646.979998   
    2021-11   334000.0  48475.934207   9823.116077  20176.883923  2950.183331   
    2021-12   365000.0  37553.587305   5186.735906  25813.264094  1558.192455   
    2021-12   365000.0  51329.479113   9501.706757  21498.293243  2853.544906   
    2022-01   366000.0  37601.666120    160.262718    839.737282    48.078815   
    2022-01   366000.0  51418.450133    296.570066    703.429934    88.971020   
    2022-01    31000.0   6097.046559  20276.242593  10723.757407  6097.046559   
    2022-02    59000.0  10886.641342  15926.259334  12073.740666  4789.594783   
    2022-03    90000.0  15466.646977  15228.601876  15771.398124  4580.005635   
    2022-04   120000.0  19276.312705  12667.931665  17332.068335  3809.665727   
    2022-05   151000.0  22679.468646  11317.565289  19682.434711  3403.155941   
    2022-06   181000.0  25549.859452   9547.208449  20452.791551  2870.390805   
    2022-07   212000.0  28159.475447   8681.176852  22318.823148  2609.615996   
    2022-08   243000.0  30472.314523   7695.071433  23304.928567  2312.839076   
    2022-09   273000.0  32477.332507   6671.830902  23328.169098  2005.017984   
    2022-10   304000.0  34348.414852   6226.925472  24773.074528  1871.082345   
    2022-11   334000.0  35995.394850   5481.731833  24518.268167  1646.979998   
    2022-12   365000.0  37553.587305   5186.735906  25813.264094  1558.192455   
    2023-01   366000.0  37601.666120    160.262718    839.737282    48.078815   
    
            period scenario  
    date                     
    2021-01    pdp     base  
    2021-01    pdp     base  
    2021-02    pdp     base  
    2021-02    pdp     base  
    2021-03    pdp     base  
    2021-03    pdp     base  
    2021-04    pdp     base  
    2021-04    pdp     base  
    2021-05    pdp     base  
    2021-05    pdp     base  
    2021-06    pdp     base  
    2021-06    pdp     base  
    2021-07    pdp     base  
    2021-07    pdp     base  
    2021-08    pdp     base  
    2021-08    pdp     base  
    2021-09    pdp     base  
    2021-09    pdp     base  
    2021-10    pdp     base  
    2021-10    pdp     base  
    2021-11    pdp     base  
    2021-11    pdp     base  
    2021-12    pdp     base  
    2021-12    pdp     base  
    2022-01    pdp     base  
    2022-01    pdp     base  
    2022-01    pud     base  
    2022-02    pud     base  
    2022-03    pud     base  
    2022-04    pud     base  
    2022-05    pud     base  
    2022-06    pud     base  
    2022-07    pud     base  
    2022-08    pud     base  
    2022-09    pud     base  
    2022-10    pud     base  
    2022-11    pud     base  
    2022-12    pud     base  
    2023-01    pud     base  



```python
sns.lineplot(data=s1_f, x=s1_f.index.to_timestamp(), y='oil_rate', hue='iteration', style='period')
```




    <AxesSubplot:xlabel='date', ylabel='oil_rate'>




    
![png](output_10_1.png)
    


When generating the cashflow an internal operation of broadcasting the iterations to produce, in this case, two cashflow models:

+ *cashflow model 1*: **Period_1 Iteration_0** + **Period_2 Iteration_0**
+ *cashflow model 2*: **Period_1 Iteration_1** + **Period_2 Iteration_0**


```python
s1_c = s1.generate_cashflow(freq_output='M')
s1_c[1].fcf()
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
      <th>income_base-pdp</th>
      <th>income_base-pud</th>
      <th>total_income</th>
      <th>fix_opex_base-pdp</th>
      <th>var_opex_base-pdp</th>
      <th>fix_opex_base-pud</th>
      <th>var_opex_base-pud</th>
      <th>total_opex</th>
      <th>capex_base-pdp</th>
      <th>capex_base-pud</th>
      <th>total_capex</th>
      <th>fcf</th>
      <th>cum_fcf</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2021-01</th>
      <td>1.259330e+06</td>
      <td>0.000000e+00</td>
      <td>1.259330e+06</td>
      <td>-5000.0</td>
      <td>-104944.153053</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-109944.153053</td>
      <td>-5000000.0</td>
      <td>0.0</td>
      <td>-5000000.0</td>
      <td>-3.850614e+06</td>
      <td>-3.850614e+06</td>
    </tr>
    <tr>
      <th>2021-02</th>
      <td>1.064207e+06</td>
      <td>0.000000e+00</td>
      <td>1.064207e+06</td>
      <td>-5000.0</td>
      <td>-88683.890486</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-93683.890486</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>9.705228e+05</td>
      <td>-2.880092e+06</td>
    </tr>
    <tr>
      <th>2021-03</th>
      <td>1.098560e+06</td>
      <td>0.000000e+00</td>
      <td>1.098560e+06</td>
      <td>-5000.0</td>
      <td>-91546.630149</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-96546.630149</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.002013e+06</td>
      <td>-1.878079e+06</td>
    </tr>
    <tr>
      <th>2021-04</th>
      <td>9.865124e+05</td>
      <td>0.000000e+00</td>
      <td>9.865124e+05</td>
      <td>-5000.0</td>
      <td>-82209.370374</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-87209.370374</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>8.993031e+05</td>
      <td>-9.787755e+05</td>
    </tr>
    <tr>
      <th>2021-05</th>
      <td>9.447843e+05</td>
      <td>0.000000e+00</td>
      <td>9.447843e+05</td>
      <td>-5000.0</td>
      <td>-78732.027218</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-83732.027218</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>8.610523e+05</td>
      <td>-1.177232e+05</td>
    </tr>
    <tr>
      <th>2021-06</th>
      <td>8.471781e+05</td>
      <td>0.000000e+00</td>
      <td>8.471781e+05</td>
      <td>-5000.0</td>
      <td>-70598.177827</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-75598.177827</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>7.715800e+05</td>
      <td>6.538567e+05</td>
    </tr>
    <tr>
      <th>2021-07</th>
      <td>8.116711e+05</td>
      <td>0.000000e+00</td>
      <td>8.116711e+05</td>
      <td>-5000.0</td>
      <td>-67639.257599</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-72639.257599</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>7.390318e+05</td>
      <td>1.392889e+06</td>
    </tr>
    <tr>
      <th>2021-08</th>
      <td>7.525876e+05</td>
      <td>0.000000e+00</td>
      <td>7.525876e+05</td>
      <td>-5000.0</td>
      <td>-62715.630308</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-67715.630308</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>6.848719e+05</td>
      <td>2.077761e+06</td>
    </tr>
    <tr>
      <th>2021-09</th>
      <td>6.772751e+05</td>
      <td>0.000000e+00</td>
      <td>6.772751e+05</td>
      <td>-5000.0</td>
      <td>-56439.594367</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-61439.594367</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>6.158355e+05</td>
      <td>2.693596e+06</td>
    </tr>
    <tr>
      <th>2021-10</th>
      <td>6.521546e+05</td>
      <td>0.000000e+00</td>
      <td>6.521546e+05</td>
      <td>-5000.0</td>
      <td>-54346.218023</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-59346.218023</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>5.928084e+05</td>
      <td>3.286404e+06</td>
    </tr>
    <tr>
      <th>2021-11</th>
      <td>5.893870e+05</td>
      <td>0.000000e+00</td>
      <td>5.893870e+05</td>
      <td>-5000.0</td>
      <td>-49115.580387</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-54115.580387</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>5.352714e+05</td>
      <td>3.821676e+06</td>
    </tr>
    <tr>
      <th>2021-12</th>
      <td>5.701024e+05</td>
      <td>0.000000e+00</td>
      <td>5.701024e+05</td>
      <td>-5000.0</td>
      <td>-47508.533786</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-52508.533786</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>5.175939e+05</td>
      <td>4.339270e+06</td>
    </tr>
    <tr>
      <th>2022-01</th>
      <td>1.779420e+04</td>
      <td>1.216575e+06</td>
      <td>1.234369e+06</td>
      <td>-5000.0</td>
      <td>-1482.850328</td>
      <td>-5000.0</td>
      <td>-101381.212966</td>
      <td>-112864.063293</td>
      <td>0.0</td>
      <td>-450000.0</td>
      <td>-450000.0</td>
      <td>6.715047e+05</td>
      <td>5.010774e+06</td>
    </tr>
    <tr>
      <th>2022-02</th>
      <td>0.000000e+00</td>
      <td>9.555756e+05</td>
      <td>9.555756e+05</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-5000.0</td>
      <td>-79631.296668</td>
      <td>-84631.296668</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>8.709443e+05</td>
      <td>5.881719e+06</td>
    </tr>
    <tr>
      <th>2022-03</th>
      <td>0.000000e+00</td>
      <td>9.137161e+05</td>
      <td>9.137161e+05</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-5000.0</td>
      <td>-76143.009380</td>
      <td>-81143.009380</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>8.325731e+05</td>
      <td>6.714292e+06</td>
    </tr>
    <tr>
      <th>2022-04</th>
      <td>0.000000e+00</td>
      <td>7.600759e+05</td>
      <td>7.600759e+05</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-5000.0</td>
      <td>-63339.658324</td>
      <td>-68339.658324</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>6.917362e+05</td>
      <td>7.406028e+06</td>
    </tr>
    <tr>
      <th>2022-05</th>
      <td>0.000000e+00</td>
      <td>6.790539e+05</td>
      <td>6.790539e+05</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-5000.0</td>
      <td>-56587.826445</td>
      <td>-61587.826445</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>6.174661e+05</td>
      <td>8.023494e+06</td>
    </tr>
    <tr>
      <th>2022-06</th>
      <td>0.000000e+00</td>
      <td>5.728325e+05</td>
      <td>5.728325e+05</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-5000.0</td>
      <td>-47736.042245</td>
      <td>-52736.042245</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>5.200965e+05</td>
      <td>8.543591e+06</td>
    </tr>
    <tr>
      <th>2022-07</th>
      <td>0.000000e+00</td>
      <td>5.208706e+05</td>
      <td>5.208706e+05</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-5000.0</td>
      <td>-43405.884259</td>
      <td>-48405.884259</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>4.724647e+05</td>
      <td>9.016055e+06</td>
    </tr>
    <tr>
      <th>2022-08</th>
      <td>0.000000e+00</td>
      <td>4.617043e+05</td>
      <td>4.617043e+05</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-5000.0</td>
      <td>-38475.357166</td>
      <td>-43475.357166</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>4.182289e+05</td>
      <td>9.434284e+06</td>
    </tr>
    <tr>
      <th>2022-09</th>
      <td>0.000000e+00</td>
      <td>4.003099e+05</td>
      <td>4.003099e+05</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-5000.0</td>
      <td>-33359.154512</td>
      <td>-38359.154512</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>3.619507e+05</td>
      <td>9.796235e+06</td>
    </tr>
    <tr>
      <th>2022-10</th>
      <td>0.000000e+00</td>
      <td>3.736155e+05</td>
      <td>3.736155e+05</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-5000.0</td>
      <td>-31134.627360</td>
      <td>-36134.627360</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>3.374809e+05</td>
      <td>1.013372e+07</td>
    </tr>
    <tr>
      <th>2022-11</th>
      <td>0.000000e+00</td>
      <td>3.289039e+05</td>
      <td>3.289039e+05</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-5000.0</td>
      <td>-27408.659166</td>
      <td>-32408.659166</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>2.964953e+05</td>
      <td>1.043021e+07</td>
    </tr>
    <tr>
      <th>2022-12</th>
      <td>0.000000e+00</td>
      <td>3.112042e+05</td>
      <td>3.112042e+05</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-5000.0</td>
      <td>-25933.679532</td>
      <td>-30933.679532</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>2.802705e+05</td>
      <td>1.071048e+07</td>
    </tr>
    <tr>
      <th>2023-01</th>
      <td>0.000000e+00</td>
      <td>9.615763e+03</td>
      <td>9.615763e+03</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>-5000.0</td>
      <td>-801.313590</td>
      <td>-5801.313590</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>3.814449e+03</td>
      <td>1.071430e+07</td>
    </tr>
  </tbody>
</table>
</div>




```python
n_cashflows = len(s1_c)

fig, ax= plt.subplots(n_cashflows,1,figsize=(15,7))

for i in range(n_cashflows):
    s1_c[i].plot(cum=True, ax=ax[i])
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])



    
![png](output_13_1.png)
    


## Period Dependency

As mentioned above, the period Dependency is set by declaring the `depends` keyword on the period instance whose start date depends on other period. 

The next example shows the definitions of two periods which one of them a probabilistic variable has been set. 


```python
p3_dict = {
    'name':'pdp',
    'dca': {
        'ti':'2021-01-01',
        'di':0.025,
        'freq_di':'M',
        'qi':{'dist':'norm', 'kw':{'loc':1500,'scale':200}}, #[800,1000],
        'b':0,
    },
    'start':'2021-01-01',
    'end':'2027-01-01',
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

p4_dict = {
    'name':'pud',
    'dca': {
        'ti':'2022-01-01',
        'di':0.3,
        'freq_di':'A',
        'qi':3000,
        'b':0,
    },
    'start':'2022-01-01',
    'end':'2027-01-01',
    'freq_output':'A',
    'depends':{'period':'pdp'},
    'cashflow_params':[
        {
            'name':'wo',
            'value':-500000,
            'period':1,
            'target':'capex'
        },
        {
            'name':'abandon',
            'value':-300000,
            'period':-1,
            'target':'capex'
        },
    ]
}
```

To create a scenario you can also pass a dictionary well structuted instead of create all classes separately, like Periods.

By declaring the `iter` key with an integer the forecast will iterate this number. Notice that, the Period 4 has neither probabilistic variables nor multiple variables however as it depends on the end date of the first. Consequently the function creates the number of iterations required to reach 10 fully iterations that covers both periods.


```python
s2_dict = {
    'name':'Dependency',
    'periods':[
        p3_dict,
        p4_dict
    ],
    'cashflow_params': cashflow_params,
    'iter':10
}
s2_dict
```




    {'name': 'Dependency',
     'periods': [{'name': 'pdp',
       'dca': {'ti': '2021-01-01',
        'di': 0.025,
        'freq_di': 'M',
        'qi': {'dist': 'norm', 'kw': {'loc': 1500, 'scale': 200}},
        'b': 0},
       'start': '2021-01-01',
       'end': '2027-01-01',
       'freq_output': 'A',
       'rate_limit': 300,
       'cashflow_params': [{'name': 'capex',
         'value': {'date': ['2021-01-01'], 'value': [-5000000]},
         'target': 'capex'}]},
      {'name': 'pud',
       'dca': {'ti': '2022-01-01', 'di': 0.3, 'freq_di': 'A', 'qi': 3000, 'b': 0},
       'start': '2022-01-01',
       'end': '2027-01-01',
       'freq_output': 'A',
       'depends': {'period': 'pdp'},
       'cashflow_params': [{'name': 'wo',
         'value': -500000,
         'period': 1,
         'target': 'capex'},
        {'name': 'abandon', 'value': -300000, 'period': -1, 'target': 'capex'}]}],
     'cashflow_params': [{'name': 'fix_opex', 'value': -5000, 'target': 'opex'},
      {'name': 'var_opex',
       'value': -5,
       'target': 'opex',
       'multiply': 'oil_volume'},
      {'name': 'income',
       'value': 60,
       'target': 'income',
       'multiply': 'oil_volume'}],
     'iter': 10}




```python
s2 = Scenario(**s2_dict)
print(type(s2))
```

    <class 'dcapy.schedule.schedule.Scenario'>


Generate Forecast


```python
s2_f = s2.generate_forecast(iter=10, seed=21)
print(s2_f)
```

             oil_rate       oil_cum  iteration     oil_volume period    scenario
    date                                                                        
    2021  1489.607150  0.000000e+00          0  468800.999434    pdp  Dependency
    2022  1098.939651  4.688010e+05          0  407326.632111    pdp  Dependency
    2023   810.729430  8.146533e+05          0  300500.294141    pdp  Dependency
    2024   598.105827  1.069802e+06          0  221910.986683    pdp  Dependency
    2025   440.877785  1.258475e+06          0  163712.145277    pdp  Dependency
    ...           ...           ...        ...            ...    ...         ...
    2027  2222.454662  9.460135e+05          7  946013.494512    pud  Dependency
    2026  3000.000000  0.000000e+00          8  473006.747256    pud  Dependency
    2027  2222.454662  9.460135e+05          8  946013.494512    pud  Dependency
    2026  3000.000000  0.000000e+00          9  473006.747256    pud  Dependency
    2027  2222.454662  9.460135e+05          9  946013.494512    pud  Dependency
    
    [80 rows x 6 columns]


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)



```python
sns.lineplot(data=s2_f,  x=s2_f.index.to_timestamp(), y='oil_rate', hue='iteration',style='period')
```




    <AxesSubplot:xlabel='date', ylabel='oil_rate'>




    
![png](output_21_1.png)
    



```python
s2_c = s2.generate_cashflow(freq_output='A')

print(f'Number of cashflow models {len(s2_c)}')
```

    Number of cashflow models 10



```python
s2_c[0].fcf()
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
      <th>income_Dependency-pdp</th>
      <th>income_Dependency-pud</th>
      <th>total_income</th>
      <th>fix_opex_Dependency-pdp</th>
      <th>var_opex_Dependency-pdp</th>
      <th>fix_opex_Dependency-pud</th>
      <th>var_opex_Dependency-pud</th>
      <th>total_opex</th>
      <th>capex_Dependency-pdp</th>
      <th>wo_Dependency-pud</th>
      <th>abandon_Dependency-pud</th>
      <th>total_capex</th>
      <th>fcf</th>
      <th>cum_fcf</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2021</th>
      <td>2.812806e+07</td>
      <td>0.000000e+00</td>
      <td>2.812806e+07</td>
      <td>-5000.0</td>
      <td>-2.344005e+06</td>
      <td>0.0</td>
      <td>0.000000e+00</td>
      <td>-2.349005e+06</td>
      <td>-5000000.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>-5000000.0</td>
      <td>2.077905e+07</td>
      <td>2.077905e+07</td>
    </tr>
    <tr>
      <th>2022</th>
      <td>2.443960e+07</td>
      <td>0.000000e+00</td>
      <td>2.443960e+07</td>
      <td>-5000.0</td>
      <td>-2.036633e+06</td>
      <td>0.0</td>
      <td>0.000000e+00</td>
      <td>-2.041633e+06</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>2.239796e+07</td>
      <td>4.317702e+07</td>
    </tr>
    <tr>
      <th>2023</th>
      <td>1.803002e+07</td>
      <td>0.000000e+00</td>
      <td>1.803002e+07</td>
      <td>-5000.0</td>
      <td>-1.502501e+06</td>
      <td>0.0</td>
      <td>0.000000e+00</td>
      <td>-1.507501e+06</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.652252e+07</td>
      <td>5.969954e+07</td>
    </tr>
    <tr>
      <th>2024</th>
      <td>1.331466e+07</td>
      <td>0.000000e+00</td>
      <td>1.331466e+07</td>
      <td>-5000.0</td>
      <td>-1.109555e+06</td>
      <td>0.0</td>
      <td>0.000000e+00</td>
      <td>-1.114555e+06</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.220010e+07</td>
      <td>7.189964e+07</td>
    </tr>
    <tr>
      <th>2025</th>
      <td>9.822729e+06</td>
      <td>0.000000e+00</td>
      <td>9.822729e+06</td>
      <td>-5000.0</td>
      <td>-8.185607e+05</td>
      <td>0.0</td>
      <td>0.000000e+00</td>
      <td>-8.235607e+05</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>8.999168e+06</td>
      <td>8.089881e+07</td>
    </tr>
    <tr>
      <th>2026</th>
      <td>-3.775426e+07</td>
      <td>2.838040e+07</td>
      <td>-9.373852e+06</td>
      <td>-5000.0</td>
      <td>3.146188e+06</td>
      <td>-5000.0</td>
      <td>-2.365034e+06</td>
      <td>7.711544e+05</td>
      <td>0.0</td>
      <td>-500000.0</td>
      <td>-300000.0</td>
      <td>-800000.0</td>
      <td>-9.402698e+06</td>
      <td>7.149611e+07</td>
    </tr>
    <tr>
      <th>2027</th>
      <td>0.000000e+00</td>
      <td>5.676081e+07</td>
      <td>5.676081e+07</td>
      <td>0.0</td>
      <td>0.000000e+00</td>
      <td>-5000.0</td>
      <td>-4.730067e+06</td>
      <td>-4.735067e+06</td>
      <td>0.0</td>
      <td>-500000.0</td>
      <td>-300000.0</td>
      <td>-800000.0</td>
      <td>5.122574e+07</td>
      <td>1.227219e+08</td>
    </tr>
  </tbody>
</table>
</div>




```python
s2.npv([0.15], freq_rate='A',freq_cashflow='A').reset_index().to_dict()
```




    {'index': {0: 0.1499999999999999,
      1: 0.1499999999999999,
      2: 0.1499999999999999,
      3: 0.1499999999999999,
      4: 0.1499999999999999,
      5: 0.1499999999999999,
      6: 0.1499999999999999,
      7: 0.1499999999999999,
      8: 0.1499999999999999,
      9: 0.1499999999999999},
     'npv': {0: 83387511.45599285,
      1: 82960222.54647115,
      2: 91277731.89554133,
      3: 88872673.70059997,
      4: 89139483.06955868,
      5: 85885826.29488969,
      6: 82277300.0707481,
      7: 82070212.93389057,
      8: 91900627.35896699,
      9: 83671291.75916964},
     'iteration': {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9}}




```python
n_cashflows = len(s2_c)

def cell_ijk(cell_id,nx,ny):
    cell_id +=1
    k=np.ceil(cell_id/(nx*ny)).astype(int)
    j=np.ceil((cell_id-(nx*ny)*(k-1))/nx).astype(int)
    i=np.ceil(cell_id-(nx*ny*(k-1))-nx*(j-1)).astype(int)
    return i-1,j-1,k-1

fig, ax= plt.subplots(5,2,figsize=(20,15))

for idx in range(n_cashflows):

    c = cell_ijk(idx+1,5,2)
    print(idx,c)
    s2_c[idx].plot(cum=True, format='m',ax=ax[c[0]-1,c[1]])
```

    0 (1, 0, 0)


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])


    1 (2, 0, 0)


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])


    2 (3, 0, 0)


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])


    3 (4, 0, 0)


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])


    4 (0, 1, 0)


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])


    5 (1, 1, 0)


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])


    6 (2, 1, 0)


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])


    7 (3, 1, 0)


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])


    8 (4, 1, 0)


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])


    9 (0, 0, 1)


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])



    
![png](output_25_20.png)
    



```python
from dcapy.auth import Credential
```


```python
cred = Credential(token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImIyZDQ5NjMyLWM0MzEtNDAzYi04OTEyLTJiZGIyOTA3NTMxNCIsIm5hbWUiOiJTYW50aWFnbyIsImxhc3RfbmFtZSI6IkN1ZXJ2byIsInVzZXJuYW1lIjoic2N1ZXJ2bzkxIiwiZXhwIjoxNjI2OTI2NTk3fQ.n3HuheJvoQKF9RNKTC9gEstC449EWd2qsrWR7f30V2U')
```


```python
s2.insert_db(cred, 'Scenario-Cash tutorial')
```




    '01de434e-d393-4f3e-8ecf-98e86b4dd39c'




```python
sd = Scenario()

sd.get_db('01de434e-d393-4f3e-8ecf-98e86b4dd39c',cred)
```


```python
type(sd)
```




    dcapy.schedule.schedule.Scenario




```python

```
