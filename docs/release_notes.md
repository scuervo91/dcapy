# Release Notes

# 0.1.13

### Fixes
👷 Ti (Smoothing Function): Resolved an issue with the Ti that affected the function of smoothing (exponential weighted average). The previous implementation incorrectly labeled the first value to be deleted. This issue has been fixed by utilizing the built-in function in pandas' ewm method. The beta parameter now acts as the alpha parameter in the pandas function.

### Feature
di_freq Support: Introduced a new feature to fit data with dates of different di_freq. 
# 0.1.12
### Features
* 🎨 Create cashflows from dataframe
## 0.1.11
### Feature
* 🎨 When fitting a Arps class you can now choose the upper and lower 
bounds of parameter b
* 🎨 Adding option to provide change points to timeseries and fit every 
segment and forecasting the last one
*🎨 Adding the option to provide in a single DataFrame production for 
multiple wells, estimate the segments and create an schedule Object 


## 0.1.10
### Fixes
* 👷 Fix bug when printing


## 0.1.9
### Fixes
* 👷 Fix Percentiles functionality when calling forecast


## 0.1.8
### Fixes
* 👷 Fix Weiner Proccesses index when using with Schedule module

## 0.1.7
### Fixes
* 👷 Fix Broadcast shapes when provide multiple cashflow iteration and only one forecast

## 0.1.6
### Fixes
* 👷 Fix Schedule Cashflow generator when using relative dates with multiple time frequencies

## 0.1.5
### Fixes
* 👷 Fix Schedule module when using relative time series instead of dates.
* 👷 Fix when plotting the dca.Arps method.

## 0.1.4
### Fixes
* 👷 Fix exporting model to file yml. Drop `exclude_unset`

## 0.1.3
### Features
* 🎨 Add Support with [Dcapy API](https://dcapyapi.herokuapp.com/) hosted in Heroku. It allows to  upload, download, edit and delete models on the cloud. It is required to create an account.

### Fixes
* 👷 Fix Python imports modules

## 0.1.2
### Fixes
* 👷 Fix how to export the Rich HTML layout excluding both, the unset and none variables
* 👷 Fix Cashflow workflow when params not set in period but WellsGroup


## 0.1.1

### Features
* 🎨 Add support to pretty print Schemas throught [Rich Package](https://github.com/willmcgugan/rich). Print Tree schemas for `schedule` Module and Summary panel for `dca` module

### Fixes
* 👷 Fix the how the cashflow models store on the instances to be able to run multiple times different scenarios.

## 0.1.0

* Initial release!
