# Dcapy

+ **Documentation** [http://scuervo91.github.io/dcapy](http://scuervo91.github.io/dcapy)
+ **Sorce Code** [https://github.com/scuervo91/dcapy](https://github.com/scuervo91/dcapy)
+ **API Url** [https://dcapyapi.herokuapp.com/](https://dcapyapi.herokuapp.com/)
+ **PyPi** [https://pypi.org/project/dcapy/](https://pypi.org/project/dcapy/)

Dcapy is a Decline Curve Analysis Python package for Oil & Gas that includes the classes and functions to perform a simple production forecast as well as probabilistic Well Schedules with cashflow analysis.  

The key features are:

+ **Simple**: Arps and Wor forecast methodologies implemented
+ **Schedule**: Create multiple forecast *periods* for a single well that represent major interventions, new perforations, etc 
+ **Scenarios**: Create multiple Scenarios and evalueate their performance easily
+ **Cash Flow**: Add cashflow parameters (Income, opex, capex) to perform a cashflow analysis to each Period and/or Scenario
+ **Deterministic/Probabilistic**: Add probabilistic variables to add a risk analysis to both simple forecast and schedules. Automatically reschedule start production depending on the callbacks.
+ **Data Validation**: Dcapy uses Pydantic to make data validations when creating new instances
+ **API**: Simple API for saving models on the cloud


## Requirements

+ Python 3.8+ 


## Installation


```console
$ pip install dcapy

---> 100%
```


## License

This project is licensed under the terms of the MIT license.