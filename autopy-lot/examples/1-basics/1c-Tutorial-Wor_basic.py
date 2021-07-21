# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: 'Python 3.8.8 64-bit (''dcapy'': conda)'
#     language: python
#     name: python388jvsc74a57bd0607220d9aa50002d928e15b68ce75e93a4d790d4e944ca3137991ee1264619da
# ---

# # WOR Forecasting
#
# In this section is introduced the basic classes and functions to make Forecast by applying the Wor Methodology 

import os
from dcapy import dca
from datetime import date
import numpy as np 

# The WOR forecasting is an empirical method to estimate the trend of the water production with respect the cumulative oil production. 
#
#
# Generally you can determine the WOR (Water-Oil Ratio) vs the Np (Cumulative Oil Production) linear relationship on a semi-log plot when preducing at a constant rate of total fluids.
#
# $
# WOR = \frac{q_{w}}{q_{o}}
# $

# ## Simple Functions to convert Bsw to Wor
#

# +
list_bsw = [0.01,0.01,0.1,0.5,0.8,0.9,0.95,0.99]

list_wor = dca.bsw_to_wor(list_bsw)
# -

dca.wor_to_bsw(list_wor)

# ## Wor Forecasting function
#
# The parameters required to define a WOR model are:
#
# + **Slope**: It is the relationship between the WOR and Np. It is defined as $\frac{d(log(WOR))}{d Np}$
# + **Fluid Rate**: Total fluid rate production target
# + **Ti**: Initial Time
# + **WOR initial**: The Wor value at the initial time

# +
time1 = np.arange(0,10,1)
slope = 3e-6
bswi = 0.5
wori = dca.bsw_to_wor(bswi)
fluid_rate = [5000]*10

f1 = dca.wor_forecast(time1,fluid_rate,slope,wori)
print(f1)

# -

# In this case you have to pass an array with the desired rate whose length be equal to the time array. That means you can pass a fluid rate array with different values.

# +
time1 = np.arange(0,10,1)
slope = 3e-5
bswi = 0.5
wori = dca.bsw_to_wor(bswi)
fluid_rate = [5000]*5 + [6000]*5

f1 = dca.wor_forecast(time1,fluid_rate,slope,wori)
print(f1)
# -

# ## Wor Class
#
# Like Arps class, the Wor class have the same advantages described before. In this case you can pass the initial bsw directly so it internally will convert it to WOR value. 

# +
bsw = 0.5
slope = 3.5e-6
ti =  0
fluid = 1000
w1 = dca.Wor(bsw=bsw,slope=slope,ti=ti, fluid_rate = fluid)

print(type(w1))
# -

# The forecast method is also present with the same parameters as seen in Arps class

fr = w1.forecast(
    start = 0,
    end = 5,
)
print(fr)

# If you want to change the fluid rate you can pass a different value when calling the `forecast` method

fr = w1.forecast(
    start = 0,
    end = 10,
    fluid_rate = 2000
)
print(fr)

# ## Multiple Values
#
# You can create Wor instances with multiple values on each of the parameters. This will create additional iterations accorging with the number of cases and the broadcast shape

# +
bsw = [0.4,0.5,0.6]
slope = 3.5e-6
ti =  0
fluid = 1000
w2 = dca.Wor(bsw=bsw,slope=slope,ti=ti, fluid_rate = fluid)

fr = w2.forecast(
    start = 0,
    end = 4,
    fluid_rate = 2000
)
print(fr)
# -

# As the each case of fluid rate can be an array with multiple values, you can pass a 2D array to make more than one iteration.

# +
bsw = 0.4
slope = 3.5e-6
ti =  0
fluid = [[1000],[2000]]
w3 = dca.Wor(bsw=bsw,slope=slope,ti=ti, fluid_rate = fluid)

fr = w3.forecast(
    start = 0,
    end = 4,
)
print(fr)

# +
bsw = 0.4
slope = 3.5e-6
ti =  0
fluid = [[1000,1200,1300,1250],[2000,2200,2300,2250]]
w4 = dca.Wor(bsw=bsw,slope=slope,ti=ti, fluid_rate = fluid)

fr = w4.forecast(
    start = 0,
    end = 4,
)
print(fr)
# -

# ## Wor with Dates

# +
w1 = dca.Wor(
    bsw = 0.5,
    slope = 3e-5,
    fluid_rate = 4000,
    ti=date(2021,1,1)
)

print(w1)
# -

fr = w1.forecast(start=date(2021,1,1),end=date(2021,1,10),freq_output='D')
print(fr)

fr = w1.forecast(start=date(2021,1,1),end=date(2022,1,1),freq_output='M')
print(fr)

fr = w1.forecast(start=date(2021,1,1),end=date(2024,1,1),freq_output='A')
print(fr)
