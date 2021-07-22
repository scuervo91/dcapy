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
    display_name: Python 3
    language: python
    name: python3
---

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

By calling a the method `insert_db` and providing the crededentials and a description the user can save the model on the cloud. It is highly recommended to write some description of the models to later identify them. If the operation is sucessfully, it returns an unique key that identify the model. 

```python
p1.insert_db(cred, description='Test_Tutorial_Period')
```

You don't have to memorize the key, it is saved on the attribute `id` of the model

```python
p1.id
```

```python
## Check the user models
```

If you want to check the user models saved on the cloud, call the credential method `get_models_info` 

```python
cred.get_models_info()
```

The row #9 containst the information of the model that was just created.

You can also get only the `Periods` Model

```python
cred.get_models_info(schema='period')
```

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

### Generate Forecast

```python
p_load.generate_forecast()
```

```python

```
