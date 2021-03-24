# Dcapy

Dcapy is a Decline Curve Analysis Python package for Oil & Gas that includes the classes and functions to perform a simple production forecast as well as complete probabilistic Well Schedules with cash flow analysis.  


The key features are:

+ **Simple**: Arps and Wor forecast methodologies implemented
+ **Shedule**: Create multiple forecast periods *periods* for a single well that represent major interventions, new perforations, etc 
+ **Cash Flow**: Add cashflow parameters (Income, opex, capex) to perform a cashflow analysis 
+ **Deterministic/Probabilistic**: Add probabilistic variables to add a risk analysis to both simple forecast and schedules.
+ **Data Validation**: Dcapy uses Pydantic to make data validations when creating new instances

<div class="termy">
```console
$ pip install dcapy

---> 100%
```
</div>