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
#     name: python3
# ---

from dcapy.schedule import Period
from dcapy import dca
from dcapy.auth import Credential
from datetime import date

cred = Credential()
cred.login('scuervo91', 'Casa24')
cred

# +
dec_model = dca.Arps(
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
p1.insert_db(c, description='Test1')
# -

p = Period()
p.get_db('9b2e1223-214e-4e69-8595-10c1b77ed2ab',cred)

p.generate_forecast()


