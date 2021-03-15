from dcapy import dca
from datetime import date

d1 = dca.Arps(**{
        'ti':['2022-01-01','2022-03-01'],
        'di':[0.3],
        'freq_di':'M',
        'qi':1500,
        'b':0,
        'fluid_rate':1600
    })
f1 = d1.forecast(start=date(2022,1,1), end=date(2023,1,1), rate_limit=400)

print(f'shape {f1.shape}')
print(f1)