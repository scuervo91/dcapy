import os
path = os.path.abspath(os.path.join('..'))
print(path)
import sys
sys.path.insert(0,path)
from dcapy import dca
from dcapy import filters
import numpy as np 
import pandas as pd
from datetime import date
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns 
def main():

    ## Set up Database 
    Username='postgres'
    Password='Fenicia1703'
    Host='localhost'
    db_name='cedco'
    connect_database='postgresql://{}:{}@{}/{}'.format(Username,Password,Host,db_name)

    engine = create_engine(connect_database)
    
    query = """
        select w.well, p.date, p.bo
        from production p
        join wells w on p.well_id = w.id
        where w.well = 'CANACABARE-3' and p.date >= DATE '2019-09-01' and p.bo>0
        order by p.date
    """

    prod = pd.read_sql(query,engine)

    dc = dca.Arps(freq_di='D')

    rt = dc.fit(df=prod, rate='bo',time='date',filter=filters.zscore,b=0)
    print(rt.head())
    print(dc)
    f2 = dc.forecast(start=date(2019,9,1),end=date(2020,10,1),freq_input='M')
    print(f2)
    
    fig, ax = plt.subplots()
    
    prod.plot(x='date',y='bo',color='green',ax=ax)
    f2.plot(y='rate', color='red',linestyle='--',ax=ax)
    rt[rt['filter']>0].plot.scatter(x='time',y='rate',ax=ax)
    plt.show()

if __name__ == '__main__':
    main()