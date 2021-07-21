# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: dcapy
#     language: python
#     name: dcapy
# ---

# # Dcapy & Probabilistic Variables
#
# In `Dcapy` the two main classes to define a declination model are `Arps` and `Wor`. When creating instances of any of them you can define multiple values for a single parameter to create different iterations and obverve the impact of these changes in the result forecast. 
#
# The ability to accept multiple values opens the opportunity to evaluate uncertainty variables modeled by probabilistic distributions throughout a Montecarlo Analysis.
#
# Let's review some cases of those instances with multiple values

import os
from dcapy import dca
import numpy as np 
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import seaborn as sns 
from scipy import stats
np.seterr(divide='ignore')

# +
a1 = dca.Arps(
    ti = 0,
    di = 0.03,
    qi = [1500,1000],
    b = 0,
    freq_di='M'
)

fr = a1.forecast(start=0,end=12,freq_input='M',freq_output='M')
print(fr)
# -

# Here it was defined an `Arps` instance with two initial rates. The result forecast, indeed there are two different forecast, is a DataFrame with two iterations.
#
# What if you would like to simulate a forecast with a initial rate as probabilistic variable normally distributed with a mean of 1300 and a standard deviation of 300? 
#
# There are two ways you can do this. 

# ### 1- Create a probabilistic instance of `scipy.stats` module and create `n` random variables 

# +
qi_random = stats.norm.rvs(loc=1300, scale=300, size=10, random_state=91)

print('Random qi values generated')
print(qi_random)

a2 = dca.Arps(
    ti = 0,
    di = 0.03,
    qi = qi_random.tolist(),
    b = 0,
    freq_di='M'
)

a2.plot(start=0,end=12,freq_input='M',freq_output='M')

# -

# ### 2- Create a probabilistic instance of `dca.ProbVar` which is a wrapper for any of the `scipy.stats` probabilistic distributions adding some features to ease the forcasting process

# +
qi_prob = dca.ProbVar(dist='norm', kw=dict(loc=1300, scale=300), seed=91)

print(qi_prob)

# + **Get Random Samples**

qi_prob.get_sample(size=10)

# + **Get percent point**

qi_prob.get_sample(ppf=[0.1,0.5,0.9])

# + **Use `dca.ProbVar` in `dca.Arps`

# +
a3 = dca.Arps(
    ti = date(2021,1,1),
    di = 0.03,
    qi = dca.ProbVar(dist='norm', kw=dict(loc=1300, scale=300)),
    b = 0,
    freq_di='M',
    seed=91
)

a3.plot(start=date(2021,1,1),end=date(2022,1,1),freq_output='M', iter=10)

# +
w1 = dca.Wor(
    bsw = dca.ProbVar(dist='uniform', kw=dict(loc=0.3, scale=0.4)),
    slope = 3e-5,
    fluid_rate = 4000,
    ti=date(2021,1,1)
)

fr = w1.forecast(start=date(2021,1,1),end=date(2022,1,1),freq_output='D', iter=15, seed=91)

fig, ax = plt.subplots(2,1, figsize=(10,7))

sns.lineplot(data=fr, x=fr.index.to_timestamp(), y='oil_rate', hue='iteration', ax=ax[0],palette='Greens')
sns.lineplot(data=fr, x=fr.index.to_timestamp(), y='bsw', hue='iteration', ax=ax[1], palette='Blues')
# -


