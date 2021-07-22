# Heroku - Cloud API

API End Point [https://dcapyapi.herokuapp.com/](https://dcapyapi.herokuapp.com/)
Documentation [https://dcapyapi.herokuapp.com/docs](https://dcapyapi.herokuapp.com/docs)

By taking advantage of the use of Pydantic (Library to make validations) a Web API has been implemented with [FastAPI](https://fastapi.tiangolo.com/) (A web framework for building APIs) and hosted on Heroku. This API, so far, allows the users to save, edit and delete the models configurations on the cloud. 

By using the API, a user can work on any Schedule Model (`Period`, `Scenario`, `Well`,`WellsGroup`), save the model to the cloud host, then on any other time the user can continue working on it, update the cloud model or delete it

`dcapy` has a wrapper for the API that allows you to make those processes in an integrated way. 


```python
from dcapy.schedule import Period
from dcapy.dca import Arps
from dcapy.auth import Credential
from datetime import date
```

## Authentication

To start using the cloud API service you have to create an account on [https://dcapyapi.herokuapp.com/admin/create](https://dcapyapi.herokuapp.com/admin/create) with an username and password. Underneath the API uses a Oauth2 methodology to authenticate every time you'll make some request. 

First Create a `Credential` instance with a token given when the user log in on [https://dcapyapi.herokuapp.com/admin/login](https://dcapyapi.herokuapp.com/admin/login)


```python
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImIyZDQ5NjMyLWM0MzEtNDAzYi04OTEyLTJiZGIyOTA3NTMxNCIsIm5hbWUiOiJTYW50aWFnbyIsImxhc3RfbmFtZSI6IkN1ZXJ2byIsInVzZXJuYW1lIjoic2N1ZXJ2bzkxIiwiZXhwIjoxNjI2OTI5MTY2fQ.ZLt6dbub8eVlxmGcRqfilXWbbSvi7n2Xkh7khO-o8kQ'

cred = Credential(token = token)
```

Now let's create a simple `Period` model


```python
dec_model = Arps(
    ti = date(2021,1,1),
    di = 0.3,
    freq_di = 'A',
    qi = [80,100],
    b = 0,
    fluid_rate = 250
)

p1 = Period(
    name = 'Period-1908',
    dca = dec_model,
    start = date(2021,1,1),
    end = date(2021,6,1),
    freq_output='M'
)

```

Check the object created


```python
print(type(p1))
print(p1.json(exclude_unset=True,indent=2))
```

    <class 'dcapy.schedule.schedule.Period'>
    {
      "name": "Period-1908",
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


By calling a the method `insert_db` and providing the crededentials and a description the user can save the model on the cloud. It is highly recommended to write some description of the models to later identify them. If the operation is sucessfully, it returns an unique key that identify the model. 


```python
p1.insert_db(cred, description='Test_Tutorial_Period')
```




    'c331945f-b1ea-4fb2-bb79-57d40a345427'



You don't have to memorize the key, it is saved on the attribute `id` of the model


```python
p1.id
```




    'c331945f-b1ea-4fb2-bb79-57d40a345427'




```python
## Check the user models
```

If you want to check the user models saved on the cloud, call the credential method `get_models_info` 


```python
cred.get_models_info()
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
      <th>id</th>
      <th>created_at</th>
      <th>modified_at</th>
      <th>type</th>
      <th>description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>87f1fe6a-1aa7-4d7f-a130-80ec0bf78fa0</td>
      <td>2021-07-01 22:46:58.411024+00:00</td>
      <td>2021-07-01 22:46:58.411071+00:00</td>
      <td>period</td>
      <td>Period-Cash tutorial</td>
    </tr>
    <tr>
      <th>1</th>
      <td>f1191ba8-9082-4104-9079-9c3c5747e96c</td>
      <td>2021-07-01 22:55:51.386600+00:00</td>
      <td>2021-07-01 22:55:51.386648+00:00</td>
      <td>scenario</td>
      <td>Scenario-Cash tutorial</td>
    </tr>
    <tr>
      <th>2</th>
      <td>eee95d1f-dee3-40e0-a1a7-800f83e3d7a1</td>
      <td>2021-07-02 00:09:54.352606+00:00</td>
      <td>2021-07-02 00:09:54.352675+00:00</td>
      <td>well</td>
      <td>well-Cash tutorial</td>
    </tr>
    <tr>
      <th>3</th>
      <td>f066f385-c108-4c7b-8e79-2a55c9301d72</td>
      <td>2021-07-02 00:14:51.151289+00:00</td>
      <td>2021-07-02 00:14:51.151313+00:00</td>
      <td>wellsgroup</td>
      <td>Tutorial-Wellsgroup</td>
    </tr>
    <tr>
      <th>4</th>
      <td>c6e698a3-cc55-4805-ad38-1027f4001951</td>
      <td>2021-07-21 02:23:24.856509+00:00</td>
      <td>2021-07-21 02:23:24.856551+00:00</td>
      <td>well</td>
      <td>well-Cash tutorial_update</td>
    </tr>
    <tr>
      <th>5</th>
      <td>65f4790e-a515-4a14-bb12-9109010ed5e9</td>
      <td>2021-07-22 03:34:15.472286+00:00</td>
      <td>2021-07-22 03:34:15.472329+00:00</td>
      <td>period</td>
      <td>Period-Cash tutorial1</td>
    </tr>
    <tr>
      <th>6</th>
      <td>01de434e-d393-4f3e-8ecf-98e86b4dd39c</td>
      <td>2021-07-22 03:37:42.568885+00:00</td>
      <td>2021-07-22 03:37:42.568928+00:00</td>
      <td>scenario</td>
      <td>Scenario-Cash tutorial</td>
    </tr>
    <tr>
      <th>7</th>
      <td>1b1ecf58-e252-4ea0-9ac3-66bee10cc050</td>
      <td>2021-07-22 03:41:04.218514+00:00</td>
      <td>2021-07-22 03:41:04.218567+00:00</td>
      <td>well</td>
      <td>well-Cash tutorial_update1</td>
    </tr>
    <tr>
      <th>8</th>
      <td>5f625d24-517d-4890-8067-f8e4da41f779</td>
      <td>2021-07-22 03:44:05.168659+00:00</td>
      <td>2021-07-22 03:44:05.168703+00:00</td>
      <td>wellsgroup</td>
      <td>Tutorial-Wellsgroup</td>
    </tr>
    <tr>
      <th>9</th>
      <td>c331945f-b1ea-4fb2-bb79-57d40a345427</td>
      <td>2021-07-22 04:32:42.161613+00:00</td>
      <td>2021-07-22 04:32:42.161652+00:00</td>
      <td>period</td>
      <td>Test_Tutorial_Period</td>
    </tr>
  </tbody>
</table>
</div>



The row #9 containst the information of the model that was just created.

You can also get only the `Periods` Model


```python
cred.get_models_info(schema='period')
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
      <th>id</th>
      <th>created_at</th>
      <th>modified_at</th>
      <th>type</th>
      <th>description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>87f1fe6a-1aa7-4d7f-a130-80ec0bf78fa0</td>
      <td>2021-07-01 22:46:58.411024+00:00</td>
      <td>2021-07-01 22:46:58.411071+00:00</td>
      <td>period</td>
      <td>Period-Cash tutorial</td>
    </tr>
    <tr>
      <th>1</th>
      <td>65f4790e-a515-4a14-bb12-9109010ed5e9</td>
      <td>2021-07-22 03:34:15.472286+00:00</td>
      <td>2021-07-22 03:34:15.472329+00:00</td>
      <td>period</td>
      <td>Period-Cash tutorial1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>c331945f-b1ea-4fb2-bb79-57d40a345427</td>
      <td>2021-07-22 04:32:42.161613+00:00</td>
      <td>2021-07-22 04:32:42.161652+00:00</td>
      <td>period</td>
      <td>Test_Tutorial_Period</td>
    </tr>
  </tbody>
</table>
</div>



## Load a Model

By having the id of the model you can load a model in your python environment by calling the method `.get_db`


```python
p_load = Period()
p_load.get_db('c331945f-b1ea-4fb2-bb79-57d40a345427',cred)
```


```python
print(type(p_load))
print(p_load.json(exclude_unset=True,indent=2))
```

    <class 'dcapy.schedule.schedule.Period'>
    {
      "name": "Period-1908",
      "id": "c331945f-b1ea-4fb2-bb79-57d40a345427",
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


### Generate Forecast


```python
p_load.generate_forecast()
```

    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:68: RuntimeWarning: divide by zero encountered in true_divide
      return qi/np.power(1+b*di*time_array,1/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:85: RuntimeWarning: divide by zero encountered in true_divide
      g = np.power(b*di*time_array+1,(b-1)/b)
    /home/scuervo/Documents/dev/apps/dcapy/dcapy/dca/arps.py:86: RuntimeWarning: divide by zero encountered in true_divide
      h = np.power(b*di*ti+1,(b-1)/b)





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
      <th>oil_rate</th>
      <th>oil_cum</th>
      <th>iteration</th>
      <th>oil_volume</th>
      <th>fluid_rate</th>
      <th>water_rate</th>
      <th>bsw</th>
      <th>wor</th>
      <th>water_cum</th>
      <th>fluid_cum</th>
      <th>water_volume</th>
      <th>fluid_volume</th>
      <th>period</th>
    </tr>
    <tr>
      <th>date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2021-01</th>
      <td>80.000000</td>
      <td>0.000000</td>
      <td>0</td>
      <td>2448.672116</td>
      <td>250.0</td>
      <td>170.000000</td>
      <td>0.680000</td>
      <td>2.125000</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>5332.390824</td>
      <td>7750.0</td>
      <td>Period-1908</td>
    </tr>
    <tr>
      <th>2021-02</th>
      <td>77.987393</td>
      <td>2448.672116</td>
      <td>0</td>
      <td>2303.691934</td>
      <td>250.0</td>
      <td>172.012607</td>
      <td>0.688050</td>
      <td>2.205646</td>
      <td>5332.390824</td>
      <td>7750.0</td>
      <td>5099.211884</td>
      <td>7375.0</td>
      <td>Period-1908</td>
    </tr>
    <tr>
      <th>2021-03</th>
      <td>76.213109</td>
      <td>4607.383867</td>
      <td>0</td>
      <td>2245.736596</td>
      <td>250.0</td>
      <td>173.786891</td>
      <td>0.695148</td>
      <td>2.280276</td>
      <td>10198.423768</td>
      <td>14750.0</td>
      <td>5156.432022</td>
      <td>7375.0</td>
      <td>Period-1908</td>
    </tr>
    <tr>
      <th>2021-04</th>
      <td>74.295771</td>
      <td>6940.145308</td>
      <td>0</td>
      <td>2267.189892</td>
      <td>250.0</td>
      <td>175.704229</td>
      <td>0.702817</td>
      <td>2.364929</td>
      <td>15645.254867</td>
      <td>22500.0</td>
      <td>5386.122225</td>
      <td>7625.0</td>
      <td>Period-1908</td>
    </tr>
    <tr>
      <th>2021-05</th>
      <td>72.486222</td>
      <td>9141.763651</td>
      <td>0</td>
      <td>2210.152858</td>
      <td>250.0</td>
      <td>177.513778</td>
      <td>0.710055</td>
      <td>2.448931</td>
      <td>20970.668217</td>
      <td>30000.0</td>
      <td>5442.435709</td>
      <td>7625.0</td>
      <td>Period-1908</td>
    </tr>
    <tr>
      <th>2021-06</th>
      <td>70.662643</td>
      <td>11360.451023</td>
      <td>0</td>
      <td>2218.687372</td>
      <td>250.0</td>
      <td>179.337357</td>
      <td>0.717349</td>
      <td>2.537937</td>
      <td>26530.126285</td>
      <td>37750.0</td>
      <td>5559.458067</td>
      <td>7750.0</td>
      <td>Period-1908</td>
    </tr>
    <tr>
      <th>2021-01</th>
      <td>100.000000</td>
      <td>0.000000</td>
      <td>1</td>
      <td>3060.840145</td>
      <td>250.0</td>
      <td>150.000000</td>
      <td>0.600000</td>
      <td>1.500000</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>4727.988530</td>
      <td>7750.0</td>
      <td>Period-1908</td>
    </tr>
    <tr>
      <th>2021-02</th>
      <td>97.484241</td>
      <td>3060.840145</td>
      <td>1</td>
      <td>2879.614917</td>
      <td>250.0</td>
      <td>152.515759</td>
      <td>0.610063</td>
      <td>1.564517</td>
      <td>4727.988530</td>
      <td>7750.0</td>
      <td>4530.264855</td>
      <td>7375.0</td>
      <td>Period-1908</td>
    </tr>
    <tr>
      <th>2021-03</th>
      <td>95.266386</td>
      <td>5759.229834</td>
      <td>1</td>
      <td>2807.170745</td>
      <td>250.0</td>
      <td>154.733614</td>
      <td>0.618934</td>
      <td>1.624220</td>
      <td>9060.529709</td>
      <td>14750.0</td>
      <td>4601.790027</td>
      <td>7375.0</td>
      <td>Period-1908</td>
    </tr>
    <tr>
      <th>2021-04</th>
      <td>92.869714</td>
      <td>8675.181635</td>
      <td>1</td>
      <td>2833.987365</td>
      <td>250.0</td>
      <td>157.130286</td>
      <td>0.628521</td>
      <td>1.691943</td>
      <td>13931.568584</td>
      <td>22500.0</td>
      <td>4826.402781</td>
      <td>7625.0</td>
      <td>Period-1908</td>
    </tr>
    <tr>
      <th>2021-05</th>
      <td>90.607777</td>
      <td>11427.204563</td>
      <td>1</td>
      <td>2762.691072</td>
      <td>250.0</td>
      <td>159.392223</td>
      <td>0.637569</td>
      <td>1.759145</td>
      <td>18713.335272</td>
      <td>30000.0</td>
      <td>4896.794636</td>
      <td>7625.0</td>
      <td>Period-1908</td>
    </tr>
    <tr>
      <th>2021-06</th>
      <td>88.328304</td>
      <td>14200.563778</td>
      <td>1</td>
      <td>2773.359215</td>
      <td>250.0</td>
      <td>161.671696</td>
      <td>0.646687</td>
      <td>1.830350</td>
      <td>23725.157856</td>
      <td>37750.0</td>
      <td>5011.822584</td>
      <td>7750.0</td>
      <td>Period-1908</td>
    </tr>
  </tbody>
</table>
</div>




```python

```
