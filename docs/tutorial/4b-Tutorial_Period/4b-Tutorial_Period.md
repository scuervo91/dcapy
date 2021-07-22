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

               oil_rate       oil_cum  iteration   oil_volume  fluid_rate  \
    date                                                                    
    2021-01   80.000000      0.000000          0  2448.672116       250.0   
    2021-02   77.987393   2448.672116          0  2303.691934       250.0   
    2021-03   76.213109   4607.383867          0  2245.736596       250.0   
    2021-04   74.295771   6940.145308          0  2267.189892       250.0   
    2021-05   72.486222   9141.763651          0  2210.152858       250.0   
    2021-06   70.662643  11360.451023          0  2218.687372       250.0   
    2021-01  100.000000      0.000000          1  3060.840145       250.0   
    2021-02   97.484241   3060.840145          1  2879.614917       250.0   
    2021-03   95.266386   5759.229834          1  2807.170745       250.0   
    2021-04   92.869714   8675.181635          1  2833.987365       250.0   
    2021-05   90.607777  11427.204563          1  2762.691072       250.0   
    2021-06   88.328304  14200.563778          1  2773.359215       250.0   
    
             water_rate       bsw       wor     water_cum  fluid_cum  \
    date                                                               
    2021-01  170.000000  0.680000  2.125000      0.000000        0.0   
    2021-02  172.012607  0.688050  2.205646   5332.390824     7750.0   
    2021-03  173.786891  0.695148  2.280276  10198.423768    14750.0   
    2021-04  175.704229  0.702817  2.364929  15645.254867    22500.0   
    2021-05  177.513778  0.710055  2.448931  20970.668217    30000.0   
    2021-06  179.337357  0.717349  2.537937  26530.126285    37750.0   
    2021-01  150.000000  0.600000  1.500000      0.000000        0.0   
    2021-02  152.515759  0.610063  1.564517   4727.988530     7750.0   
    2021-03  154.733614  0.618934  1.624220   9060.529709    14750.0   
    2021-04  157.130286  0.628521  1.691943  13931.568584    22500.0   
    2021-05  159.392223  0.637569  1.759145  18713.335272    30000.0   
    2021-06  161.671696  0.646687  1.830350  23725.157856    37750.0   
    
             water_volume  fluid_volume  
    date                                 
    2021-01   5332.390824        7750.0  
    2021-02   5099.211884        7375.0  
    2021-03   5156.432022        7375.0  
    2021-04   5386.122225        7625.0  
    2021-05   5442.435709        7625.0  
    2021-06   5559.458067        7750.0  
    2021-01   4727.988530        7750.0  
    2021-02   4530.264855        7375.0  
    2021-03   4601.790027        7375.0  
    2021-04   4826.402781        7625.0  
    2021-05   4896.794636        7625.0  
    2021-06   5011.822584        7750.0  


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)


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

    <class 'dcapy.schedule.schedule.Period'>



```python
print(p1.json(exclude_unset=True, indent=2))
```

    {
      "name": "Period-1",
      "dca": {
        "qi": [
          80.0,
          100.0
        ],
        "di": 0.3,
        "b": 0.0,
        "ti": "2021-01-01",
        "freq_di": "A",
        "fluid_rate": 250.0
      },
      "start": "2021-01-01",
      "end": "2021-06-01",
      "freq_output": "M"
    }


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

    3 validation errors for Period
    dca
      value is not a valid dict (type=type_error.dict)
    dca
      value is not a valid dict (type=type_error.dict)
    freq_output
      value is not a valid enumeration member; permitted: 'A', 'M', 'D' (type=type_error.enum; enum_values=[<FreqEnum.A: 'A'>, <FreqEnum.M: 'M'>, <FreqEnum.D: 'D'>])


The wrong user input trigger the Pydantic validation error indicating the `dna` is not valid neither does `freq output`


Pydantic allows to create instances by passing a dictionary and it will validate even the deeper instances, for example the dca model

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

    name='Period-1' cashflow_params=None cashflow=None forecast=None seed=None iter=1 ppf=None description=None id=None dca=Declination 
     Ti: 2021-01-01 
     Qi: [80.0, 100.0] bbl/d 
     Di: 0.3 A 
     b: 0.0 start=datetime.date(2021, 1, 1) end=datetime.date(2022, 1, 1) time_list=None freq_input='D' freq_output=<FreqEnum.M: 'M'> rate_limit=None cum_limit=None depends=None type=<SchemasEnum.period: 'period'>


It automatically validates dates even they are strings, floats and deeper instances like dca.Arps

If an input error is made on dca model the validator will also detect where is the mistake.

To generate the forecast of the period just call the method `generate_forecast`


```python
print(p1.generate_forecast())
```

               oil_rate       oil_cum  iteration   oil_volume  fluid_rate  \
    date                                                                    
    2021-01   80.000000      0.000000          0  2448.672116       250.0   
    2021-02   77.987393   2448.672116          0  2303.691934       250.0   
    2021-03   76.213109   4607.383867          0  2245.736596       250.0   
    2021-04   74.295771   6940.145308          0  2267.189892       250.0   
    2021-05   72.486222   9141.763651          0  2210.152858       250.0   
    2021-06   70.662643  11360.451023          0  2156.322329       250.0   
    2021-07   68.941582  13454.408309          0  2102.074456       250.0   
    2021-08   67.207178  15564.599934          0  2083.647957       250.0   
    2021-09   65.516407  17621.704223          0  1999.281182       250.0   
    2021-10   63.920689  19563.162298          0  1948.984085       250.0   
    2021-11   62.312598  21519.672393          0  1901.514589       250.0   
    2021-12   60.794911  23366.191475          0  1853.677064       250.0   
    2022-01   59.265458  25227.026520          0  1860.835045       250.0   
    2021-01  100.000000      0.000000          1  3060.840145       250.0   
    2021-02   97.484241   3060.840145          1  2879.614917       250.0   
    2021-03   95.266386   5759.229834          1  2807.170745       250.0   
    2021-04   92.869714   8675.181635          1  2833.987365       250.0   
    2021-05   90.607777  11427.204563          1  2762.691072       250.0   
    2021-06   88.328304  14200.563778          1  2695.402911       250.0   
    2021-07   86.176978  16818.010386          1  2627.593070       250.0   
    2021-08   84.008973  19455.749917          1  2604.559946       250.0   
    2021-09   81.895509  22027.130278          1  2499.101477       250.0   
    2021-10   79.900861  24453.952872          1  2436.230106       250.0   
    2021-11   77.890748  26899.590491          1  2376.893236       250.0   
    2021-12   75.993639  29207.739344          1  2317.096330       250.0   
    2022-01   74.081822  31533.783150          1  2326.043807       250.0   
    
             water_rate       bsw       wor     water_cum  fluid_cum  \
    date                                                               
    2021-01  170.000000  0.680000  2.125000      0.000000        0.0   
    2021-02  172.012607  0.688050  2.205646   5332.390824     7750.0   
    2021-03  173.786891  0.695148  2.280276  10198.423768    14750.0   
    2021-04  175.704229  0.702817  2.364929  15645.254867    22500.0   
    2021-05  177.513778  0.710055  2.448931  20970.668217    30000.0   
    2021-06  179.337357  0.717349  2.537937  26530.126285    37750.0   
    2021-07  181.058418  0.724234  2.626259  31961.878818    45250.0   
    2021-08  182.792822  0.731171  2.719841  37628.456296    53000.0   
    2021-09  184.483593  0.737934  2.815838  43347.447664    60750.0   
    2021-10  186.079311  0.744317  2.911097  48929.827008    68250.0   
    2021-11  187.687402  0.750750  3.012030  54748.136469    76000.0   
    2021-12  189.205089  0.756820  3.112186  60424.289136    83500.0   
    2022-01  190.734542  0.762938  3.218309  66337.059948    91250.0   
    2021-01  150.000000  0.600000  1.500000      0.000000        0.0   
    2021-02  152.515759  0.610063  1.564517   4727.988530     7750.0   
    2021-03  154.733614  0.618934  1.624220   9060.529709    14750.0   
    2021-04  157.130286  0.628521  1.691943  13931.568584    22500.0   
    2021-05  159.392223  0.637569  1.759145  18713.335272    30000.0   
    2021-06  161.671696  0.646687  1.830350  23725.157856    37750.0   
    2021-07  163.823022  0.655292  1.901007  28639.848523    45250.0   
    2021-08  165.991027  0.663964  1.975873  33785.570370    53000.0   
    2021-09  168.104491  0.672418  2.052670  38996.809580    60750.0   
    2021-10  170.099139  0.680397  2.128877  44099.783760    68250.0   
    2021-11  172.109252  0.688437  2.209624  49435.170587    76000.0   
    2021-12  174.006361  0.696025  2.289749  54655.361420    83500.0   
    2022-01  175.918178  0.703673  2.374647  60108.824936    91250.0   
    
             water_volume  fluid_volume    period  
    date                                           
    2021-01   5332.390824        7750.0  Period-1  
    2021-02   5099.211884        7375.0  Period-1  
    2021-03   5156.432022        7375.0  Period-1  
    2021-04   5386.122225        7625.0  Period-1  
    2021-05   5442.435709        7625.0  Period-1  
    2021-06   5495.605300        7625.0  Period-1  
    2021-07   5549.165006        7625.0  Period-1  
    2021-08   5692.784423        7750.0  Period-1  
    2021-09   5650.685356        7625.0  Period-1  
    2021-10   5700.344403        7625.0  Period-1  
    2021-11   5747.231064        7625.0  Period-1  
    2021-12   5794.461740        7625.0  Period-1  
    2022-01   5912.770813        7750.0  Period-1  
    2021-01   4727.988530        7750.0  Period-1  
    2021-02   4530.264855        7375.0  Period-1  
    2021-03   4601.790027        7375.0  Period-1  
    2021-04   4826.402781        7625.0  Period-1  
    2021-05   4896.794636        7625.0  Period-1  
    2021-06   4963.256626        7625.0  Period-1  
    2021-07   5030.206257        7625.0  Period-1  
    2021-08   5178.480529        7750.0  Period-1  
    2021-09   5157.106695        7625.0  Period-1  
    2021-10   5219.180503        7625.0  Period-1  
    2021-11   5277.788830        7625.0  Period-1  
    2021-12   5336.827175        7625.0  Period-1  
    2022-01   5453.463516        7750.0  Period-1  


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)


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

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)


               oil_rate       oil_cum  iteration   oil_volume  fluid_rate  \
    date                                                                    
    2021-01   80.000000      0.000000          0  2448.672116       250.0   
    2021-02   77.987393   2448.672116          0  2303.691934       250.0   
    2021-03   76.213109   4607.383867          0  2245.736596       250.0   
    2021-04   74.295771   6940.145308          0  2267.189892       250.0   
    2021-05   72.486222   9141.763651          0  2210.152858       250.0   
    2021-06   70.662643  11360.451023          0 -4570.881825       250.0   
    2021-01  100.000000      0.000000          1  3060.840145       250.0   
    2021-02   97.484241   3060.840145          1  2879.614917       250.0   
    2021-03   95.266386   5759.229834          1  2807.170745       250.0   
    2021-04   92.869714   8675.181635          1  2833.987365       250.0   
    2021-05   90.607777  11427.204563          1  2762.691072       250.0   
    2021-06   88.328304  14200.563778          1  2695.402911       250.0   
    2021-07   86.176978  16818.010386          1  2627.593070       250.0   
    2021-08   84.008973  19455.749917          1  2604.559946       250.0   
    2021-09   81.895509  22027.130278          1  2499.101477       250.0   
    2021-10   79.900861  24453.952872          1  2436.230106       250.0   
    2021-11   77.890748  26899.590491          1  2376.893236       250.0   
    2021-12   75.993639  29207.739344          1  2317.096330       250.0   
    2022-01   74.081822  31533.783150          1  2326.043807       250.0   
    
             water_rate       bsw       wor     water_cum  fluid_cum  \
    date                                                               
    2021-01  170.000000  0.680000  2.125000      0.000000        0.0   
    2021-02  172.012607  0.688050  2.205646   5332.390824     7750.0   
    2021-03  173.786891  0.695148  2.280276  10198.423768    14750.0   
    2021-04  175.704229  0.702817  2.364929  15645.254867    22500.0   
    2021-05  177.513778  0.710055  2.448931  20970.668217    30000.0   
    2021-06  179.337357  0.717349  2.537937  26530.126285    37750.0   
    2021-01  150.000000  0.600000  1.500000      0.000000        0.0   
    2021-02  152.515759  0.610063  1.564517   4727.988530     7750.0   
    2021-03  154.733614  0.618934  1.624220   9060.529709    14750.0   
    2021-04  157.130286  0.628521  1.691943  13931.568584    22500.0   
    2021-05  159.392223  0.637569  1.759145  18713.335272    30000.0   
    2021-06  161.671696  0.646687  1.830350  23725.157856    37750.0   
    2021-07  163.823022  0.655292  1.901007  28639.848523    45250.0   
    2021-08  165.991027  0.663964  1.975873  33785.570370    53000.0   
    2021-09  168.104491  0.672418  2.052670  38996.809580    60750.0   
    2021-10  170.099139  0.680397  2.128877  44099.783760    68250.0   
    2021-11  172.109252  0.688437  2.209624  49435.170587    76000.0   
    2021-12  174.006361  0.696025  2.289749  54655.361420    83500.0   
    2022-01  175.918178  0.703673  2.374647  60108.824936    91250.0   
    
             water_volume  fluid_volume    period  
    date                                           
    2021-01   5332.390824        7750.0  Period-1  
    2021-02   5099.211884        7375.0  Period-1  
    2021-03   5156.432022        7375.0  Period-1  
    2021-04   5386.122225        7625.0  Period-1  
    2021-05   5442.435709        7625.0  Period-1  
    2021-06           NaN        7625.0  Period-1  
    2021-01   4727.988530        7750.0  Period-1  
    2021-02   4530.264855        7375.0  Period-1  
    2021-03   4601.790027        7375.0  Period-1  
    2021-04   4826.402781        7625.0  Period-1  
    2021-05   4896.794636        7625.0  Period-1  
    2021-06   4963.256626        7625.0  Period-1  
    2021-07   5030.206257        7625.0  Period-1  
    2021-08   5178.480529        7750.0  Period-1  
    2021-09   5157.106695        7625.0  Period-1  
    2021-10   5219.180503        7625.0  Period-1  
    2021-11   5277.788830        7625.0  Period-1  
    2021-12   5336.827175        7625.0  Period-1  
    2022-01   5453.463516        7750.0  Period-1  



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

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)





    <AxesSubplot:xlabel='date', ylabel='oil_rate'>




    
![png](output_19_2.png)
    


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

               oil_rate        oil_cum  iteration    oil_volume  fluid_rate  \
    date                                                                      
    2021-01  800.000000       0.000000          0  24486.721159       250.0   
    2021-02  779.873928   24486.721159          0  23036.919336       250.0   
    2021-03  762.131092   46073.838672          0  22457.365959       250.0   
    2021-04  742.957710   69401.453077          0  22671.898918       250.0   
    2021-05  724.862217   91417.636508          0  22101.528575       250.0   
    2021-06  706.626430  113604.510228          0  21563.223292       250.0   
    2021-07  689.415822  134544.083091          0  21020.744556       250.0   
    2021-08  672.071781  155645.999340          0  20836.479567       250.0   
    2021-09  655.164075  176217.042226          0  19992.811818       250.0   
    2021-10  639.206885  195631.622975          0  19489.840850       250.0   
    2021-11  623.125980  215196.723927          0  19015.145887       250.0   
    2021-12  607.949111  233661.914748          0  18536.770638       250.0   
    2022-01  592.654577  252270.265203          0  18608.350455       250.0   
    
             water_rate       bsw       wor      water_cum  fluid_cum  \
    date                                                                
    2021-01 -550.000000 -2.200000 -0.687500      -0.000000        0.0   
    2021-02 -529.873928 -2.119496 -0.679435  -16426.091762     7750.0   
    2021-03 -512.131092 -2.048524 -0.671972  -30765.762324    14750.0   
    2021-04 -492.957710 -1.971831 -0.663507  -46047.451328    22500.0   
    2021-05 -474.862217 -1.899449 -0.655107  -60293.317825    30000.0   
    2021-06 -456.626430 -1.826506 -0.646206  -74448.737154    37750.0   
    2021-07 -439.415822 -1.757663 -0.637374  -87631.211817    45250.0   
    2021-08 -422.071781 -1.688287 -0.628016 -100715.437039    53000.0   
    2021-09 -405.164075 -1.620656 -0.618416 -113275.523361    60750.0   
    2021-10 -389.206885 -1.556828 -0.608890 -124951.729918    68250.0   
    2021-11 -373.125980 -1.492504 -0.598797 -136518.635308    76000.0   
    2021-12 -357.949111 -1.431796 -0.588781 -147257.108643    83500.0   
    2022-01 -342.654577 -1.370618 -0.578169 -157879.400516    91250.0   
    
             water_volume  fluid_volume    period  
    date                                           
    2021-01 -16426.091762        7750.0  Period-1  
    2021-02 -15382.881162        7375.0  Period-1  
    2021-03 -14810.679783        7375.0  Period-1  
    2021-04 -14763.777750        7625.0  Period-1  
    2021-05 -14200.642913        7625.0  Period-1  
    2021-06 -13668.946996        7625.0  Period-1  
    2021-07 -13133.349943        7625.0  Period-1  
    2021-08 -12822.155772        7750.0  Period-1  
    2021-09 -12118.146439        7625.0  Period-1  
    2021-10 -11621.555974        7625.0  Period-1  
    2021-11 -11152.689363        7625.0  Period-1  
    2021-12 -10680.382604        7625.0  Period-1  
    2022-01 -10622.291873        7750.0  Period-1  


    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)


### Generate a cashflow

When calling the `generate_cashflow` method it return a list of `CashFlowModel`


```python
cf_model = p1_cash.generate_cashflow()

for i in cf_model:
    print(type(i))
```

    <class 'dcapy.cashflow.cashflow.CashFlowModel'>



```python
print(cf_model[0].fcf())
```

             income_Period-1  total_income  fix_opex_Period-1  var_opex_Period-1  \
    2021-01     1.322283e+06  1.322283e+06            -5000.0     -293840.653906   
    2021-02     1.243994e+06  1.243994e+06            -5000.0     -276443.032030   
    2021-03     1.212698e+06  1.212698e+06            -5000.0     -269488.391508   
    2021-04     1.224283e+06  1.224283e+06            -5000.0     -272062.787018   
    2021-05     1.193483e+06  1.193483e+06            -5000.0     -265218.342905   
    2021-06     1.164414e+06  1.164414e+06            -5000.0     -258758.679501   
    2021-07     1.135120e+06  1.135120e+06            -5000.0     -252248.934673   
    2021-08     1.125170e+06  1.125170e+06            -5000.0     -250037.754807   
    2021-09     1.079612e+06  1.079612e+06            -5000.0     -239913.741813   
    2021-10     1.052451e+06  1.052451e+06            -5000.0     -233878.090205   
    2021-11     1.026818e+06  1.026818e+06            -5000.0     -228181.750639   
    2021-12     1.000986e+06  1.000986e+06            -5000.0     -222441.247658   
    2022-01     1.004851e+06  1.004851e+06            -5000.0     -223300.205458   
    
                total_opex  capex_drill_Period-1  total_capex           fcf  \
    2021-01 -298840.653906            -3000000.0   -3000000.0 -1.976558e+06   
    2021-02 -281443.032030                   0.0          0.0  9.625506e+05   
    2021-03 -274488.391508                   0.0          0.0  9.382094e+05   
    2021-04 -277062.787018                   0.0          0.0  9.472198e+05   
    2021-05 -270218.342905                   0.0          0.0  9.232642e+05   
    2021-06 -263758.679501                   0.0          0.0  9.006554e+05   
    2021-07 -257248.934673                   0.0          0.0  8.778713e+05   
    2021-08 -255037.754807                   0.0          0.0  8.701321e+05   
    2021-09 -244913.741813                   0.0          0.0  8.346981e+05   
    2021-10 -238878.090205                   0.0          0.0  8.135733e+05   
    2021-11 -233181.750639                   0.0          0.0  7.936361e+05   
    2021-12 -227441.247658                   0.0          0.0  7.735444e+05   
    2022-01 -228300.205458                   0.0          0.0  7.765507e+05   
    
                  cum_fcf  
    2021-01 -1.976558e+06  
    2021-02 -1.014007e+06  
    2021-03 -7.579773e+04  
    2021-04  8.714220e+05  
    2021-05  1.794686e+06  
    2021-06  2.695342e+06  
    2021-07  3.573213e+06  
    2021-08  4.443345e+06  
    2021-09  5.278043e+06  
    2021-10  6.091616e+06  
    2021-11  6.885253e+06  
    2021-12  7.658797e+06  
    2022-01  8.435348e+06  


# Make a plot of the Cashflow Model


```python
fig, ax= plt.subplots(figsize=(15,7))

cf_model[0].plot(cum=True, ax=ax)
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])



    
![png](output_28_1.png)
    



```python
## Estimate the NPV and IRR
```


```python
p1_cash.npv([0.1,0.15], freq_rate='A', freq_cashflow='M')
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
      <th>0.007974</th>
      <td>7.935376e+06</td>
      <td>0</td>
    </tr>
    <tr>
      <th>0.011715</th>
      <td>7.712939e+06</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>




```python
p1_cash.irr()
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
      <th>irr</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.466046</td>
    </tr>
  </tbody>
</table>
</div>



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

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:84: RuntimeWarning: divide by zero encountered in true_divide
      f = qi/(di*(b-1))
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:87: RuntimeWarning: invalid value encountered in multiply
      return f*(g-h)



```python
n_cashflows = len(p2_cashflow)

fig, ax= plt.subplots(n_cashflows,2,figsize=(15,7))

for i in range(n_cashflows):
    forecast_iteration = p2_forecast[p2_forecast['iteration']==i] 
    sns.lineplot(data =forecast_iteration, x=forecast_iteration.index.to_timestamp(), y='oil_rate', ax=ax[i,0])
    p2_cashflow[i].plot(cum=True, ax=ax[i,1])
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])



    
![png](output_34_1.png)
    



```python
p2_cash.npv([0.1,0.17], freq_rate='A', freq_cashflow='M')
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
      <th>0.007974</th>
      <td>7.935376e+06</td>
      <td>0</td>
    </tr>
    <tr>
      <th>0.013170</th>
      <td>7.628429e+06</td>
      <td>0</td>
    </tr>
    <tr>
      <th>0.007974</th>
      <td>6.622938e+06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>0.013170</th>
      <td>6.351756e+06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>0.007974</th>
      <td>3.895086e+06</td>
      <td>2</td>
    </tr>
    <tr>
      <th>0.013170</th>
      <td>3.700136e+06</td>
      <td>2</td>
    </tr>
  </tbody>
</table>
</div>



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

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:245: RuntimeWarning: invalid value encountered in true_divide
      (np.power(qi / rate, b) - 1)/(b * di)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)



```python
n_cashflows = len(p3_cashflow)

fig, ax= plt.subplots(n_cashflows,1,figsize=(15,15), gridspec_kw={'hspace':0.4})

for i in range(n_cashflows):
    p3_cashflow[i].plot(cum=True, ax=ax[i])
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:351: UserWarning: FixedFormatter should only be used together with FixedLocator
      grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/cashflow/cashflow.py:359: UserWarning: FixedFormatter should only be used together with FixedLocator
      spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])



    
![png](output_38_1.png)
    


Here, the same forecast was used to create five different cashflow models according with the iterations defined on the Oil price


```python
p3_cash.npv([0.1], freq_rate='A', freq_cashflow='M')
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
      <th>0.007974</th>
      <td>-1.687330e+06</td>
      <td>0</td>
    </tr>
    <tr>
      <th>0.007974</th>
      <td>3.746782e+05</td>
      <td>1</td>
    </tr>
    <tr>
      <th>0.007974</th>
      <td>2.436687e+06</td>
      <td>2</td>
    </tr>
    <tr>
      <th>0.007974</th>
      <td>6.560703e+06</td>
      <td>3</td>
    </tr>
    <tr>
      <th>0.007974</th>
      <td>1.068472e+07</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>



## Export the model

All classes in `dcapy` are based on Pydantic, hence they can be directly exported to a dictionary, json and further to yml

#### Export to Dictionary


```python
print(p3_cash.dict(exclude={'forecast','cashflow'}, exclude_unset=True))
```

    {'name': 'Period-1', 'cashflow_params': [{'name': 'fix_opex', 'value': -5000.0, 'target': <TargetEnum.opex: 'opex'>, 'freq_value': <FreqEnum.M: 'M'>}, {'name': 'var_opex', 'value': -12.0, 'target': <TargetEnum.opex: 'opex'>, 'multiply': 'oil_volume'}, {'name': 'income', 'wi': 0.9, 'value': [20.0, 30.0, 40.0, 60.0, 80.0], 'target': <TargetEnum.income: 'income'>, 'multiply': 'oil_volume'}, {'name': 'capex_drill', 'periods': 1, 'value': -3000000.0, 'target': <TargetEnum.capex: 'capex'>}], 'dca': {'qi': 700.0, 'di': 0.3, 'b': 0.0, 'ti': datetime.date(2021, 1, 1), 'freq_di': <FreqEnum.A: 'A'>, 'fluid_rate': 250.0}, 'start': datetime.date(2021, 1, 1), 'end': datetime.date(2022, 1, 1), 'freq_output': <FreqEnum.M: 'M'>, 'rate_limit': 70.0}


#### Export to json


```python
print(p3_cash.json(exclude={'forecast','cashflow'}, exclude_unset=True))
```

    {"name": "Period-1", "cashflow_params": [{"name": "fix_opex", "value": -5000.0, "target": "opex", "freq_value": "M"}, {"name": "var_opex", "value": -12.0, "target": "opex", "multiply": "oil_volume"}, {"name": "income", "wi": 0.9, "value": [20.0, 30.0, 40.0, 60.0, 80.0], "target": "income", "multiply": "oil_volume"}, {"name": "capex_drill", "periods": 1, "value": -3000000.0, "target": "capex"}], "dca": {"qi": 700.0, "di": 0.3, "b": 0.0, "ti": "2021-01-01", "freq_di": "A", "fluid_rate": 250.0}, "start": "2021-01-01", "end": "2022-01-01", "freq_output": "M", "rate_limit": 70.0}



```python
p3_cash.tree()
```




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-weight: bold">📉Period-1                                                                                   </span>
</pre>




#### Export to cloud

Dcapy has integrated connection with an API hosted on [Heroku](https://www.heroku.com) that allows to save your models on the cloud. This allows you to create, update and delete your models on a remote database whicgh is accesible throught a single account (with Oauth2 Authentication).


```python
from dcapy.auth import Credential
```


```python
cred = Credential(token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImIyZDQ5NjMyLWM0MzEtNDAzYi04OTEyLTJiZGIyOTA3NTMxNCIsIm5hbWUiOiJTYW50aWFnbyIsImxhc3RfbmFtZSI6IkN1ZXJ2byIsInVzZXJuYW1lIjoic2N1ZXJ2bzkxIiwiZXhwIjoxNjI2OTI2NTk3fQ.n3HuheJvoQKF9RNKTC9gEstC449EWd2qsrWR7f30V2U')
```


```python
p3_cash.insert_db(cred, 'Period-Cash tutorial1')
```




    '65f4790e-a515-4a14-bb12-9109010ed5e9'




```python

```
