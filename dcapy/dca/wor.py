#External Imports
import numpy as np 
import pandas as pd 
from datetime import date, timedelta
from typing import Union
from pydantic import BaseModel

#Local Imports
from .dca import DCA 
from .timeconverter import list_freq, converter_factor, time_converter_matrix, check_value_or_prob, FreqEnum


def bsw_to_wor(bsw):
    assert isinstance(bsw,(int,float,np.ndarray,pd.Series))
    bsw = np.atleast_1d(bsw)
    assert np.all((bsw>=0)&(bsw<=1))
    wor = bsw/(1-bsw)
    return wor 

def wor_to_bsw(wor):
    assert isinstance(wor,(int,float,np.ndarray,pd.Series))
    wor = np.atleast_1d(wor)
    assert np.all(wor>=0)
    bsw = wor/(wor+1)
    return bsw   

def wor_forecast(time_array:np.ndarray,fluid_rate:Union[float,np.ndarray], slope:float, 
	wor_i:float, rate_limit:float = None,np_limit:float=None, wor_limit:float=None,npi:float=0):


	time_array = np.atleast_1d(time_array)
	fluid_rate = np.atleast_1d(fluid_rate)

	cum_np = npi 
	cum_wp = 0 
	delta_time = np.diff(time_array,prepend=0)

	wor_i1 = wor_i + 1

	# Create arrays

	oil_cum = np.zeros(time_array.shape)
	oil_cum[0] = npi

	water_cum = np.zeros(time_array.shape)

	wor = np.zeros(time_array.shape)
	wor[0] = wor_i


	wor_1 = np.zeros(time_array.shape)
	wor_1[0] = wor_i + 1

	oil_rate = np.zeros(time_array.shape)
	water_rate = np.zeros(time_array.shape)
	bsw = np.zeros(time_array.shape)



	for i in range(1,delta_time.shape[0]):
		wor_1[i] = np.exp(slope*oil_cum[i-1])*wor_1[i-1]
		wor[i] = wor_1[i] - 1
		bsw[i] = wor_to_bsw(wor[i])
		oil_rate[i] = fluid_rate[i]*(1-bsw[i])
		water_rate[i] = fluid_rate[i]*bsw[i]
		oil_cum[i] = oil_cum[i-1] + oil_rate[i]*delta_time[i]
		water_cum[i] = water_cum[i-1] + water_rate[i]*delta_time[i]

		if rate_limit:
		    if oil_rate[i] <= rate_limit:
		        break

		if np_limit:
		    if oil_cum[i] >= np_limit:
		        break     

		if wor_limit:
		    if wor[i] >= wor_limit:
		        break          
	print(i)	        
	_forecast = pd.DataFrame(
		{
			'oil_rate':oil_rate,
			'water_rate':water_rate,
			'oil_cum':oil_cum,
			'water_cum':water_cum,
			'bsw':bsw,
			'wor':wor,
			'wor_1':wor_1,
			'delta_time':delta_time
		},
		index = time_array
	)

	return _forecast[1:i+1]



class Wor(BaseModel,DCA):

    bsw: Union[stats._distn_infrastructure.rv_frozen,List[float],float] = Field(...)
    slope: Union[stats._distn_infrastructure.rv_frozen,List[float],float] = Field(...)
    ti: Union[int,date] = Field(...)
    seed : Optional[int] = Field(None)
    fluid_rate: Optional[Union[float,List[float]]] = Field(None)
    gor: Optional[Union[float,List[float]]] = Field(None)
    glr: Optional[Union[float,List[float]]] = Field(None)


