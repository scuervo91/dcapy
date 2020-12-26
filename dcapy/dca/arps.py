
#External Libraries Import
import numpy as np 
import pandas as pd 
from datetime import datetime, date, timedelta
from typing import Union
#Local Imports
from .dca import DCA 
from .timeconverter import list_freq, converter_factor, time_converter_matrix

def arps_exp(qi:float,di:float,b:float,time_array:np.ndarray)->np.ndarray:
    """arps_exp Calculate the rate of Exponential, b=0, Arps Declination

    Parameters
    ----------
    qi : float
        Initial rate
    di : float
        Initial Declination
    b : float
        Arps Coeficient
    time_array : np.ndarray
        Array of numbers that represents the periods of timeto calculate rate

    Returns
    -------
    np.ndarray
        Array of the rates calculated for the time_array
    """
    return qi*np.exp(-di*time_array)

def arps_hyp(qi:float,di:float,b:float,time_array:np.ndarray)->np.ndarray:
    """arps_exp Calculate the rate of either Armonic or hyperbolic , b>0, Arps Declination

    Parameters
    ----------
    qi : float
        Initial rate
    di : float
        Initial Declination
    b : float
        Arps Coeficient
    time_array : np.ndarray
        Array of numbers that represents the periods of timeto calculate rate

    Returns
    -------
    np.ndarray
        Array of the rates calculated for the time_array
    """
    return qi/np.power(1+b*di*time_array,1/b)

#Arps Decline Curve
def arps_forecast(qi:Union[np.ndarray,float],di:Union[np.ndarray,float],
                 b:Union[np.ndarray,float], time_array:Union[np.ndarray, list],
                 ti:Union[np.ndarray,float]=0.0)->np.ndarray:
    """arps_decline Estimate the rate forecast for the time_array  given the Arps Parameters

    Parameters
    ----------
    qi : float
        Initial Rate at ti
    di : float
        Decline rate
    b : float
        description
    time_array : Union[np.ndarray, list]
        array of times to make forecast
    ti : float, optional
        Time of the initial rate qi, by default 0.0

    Returns
    -------
    np.ndarray
        Production forecast in a numpy array
    """
    params_dict = {
        'qi': qi,
        'di': di,
        'b': b,
        'ti': ti
    }
    for i in params_dict:
        if isinstance(params_dict[i],np.ndarray):
            params_dict[i] = params_dict[i].reshape(-1,1)
        else:
            try:
               params_dict[i] = np.atleast_1d(params_dict[i]).reshape(-1,1)
            except Exception as e:
                print(e)
                raise
    
    time_diff = np.atleast_1d(time_array) - ti
    
    f = np.where(
        params_dict['b']==0,
        arps_exp(
            params_dict['qi'],
            params_dict['di'],
            params_dict['b'],
            time_diff
        ),
        arps_hyp(
            params_dict['qi'],
            params_dict['di'],
            params_dict['b'],
            time_diff
        )
    )
    
    return f.T



def arps_rate_time(qi:Union[np.ndarray,float],di:Union[np.ndarray,float],
                 b:Union[np.ndarray,float], rate:Union[int,float,np.ndarray])->int:
    """arps_rate_time Estimate the time at which the rate is reached given Arps parameters

    Parameters
    ----------
    qi : float
        Initial Rate at ti
    di : float
        Decline rate
    b : float
        description
    rate : float
        Rate limit at which the forecast must be stop
    ti : float, optional
        Time of the initial rate qi, by default 0.0

    Returns
    -------
    np.ndarray
        Time at which the rate limit is reached
    """
    if b == 0:
        time_until = np.log(qi / rate) * (1/di)
    else:
        time_until = (np.power(qi / rate, b) - 1)/(b * di)
    
    return time_until.astype(int)

            
# Dict of allowed di frequencies
di_freq_dict = {
    'A':365,
    'M':30,
    'D':1
}

class Arps(DCA):
    """Arps Arps decline curve Instance

    Attributes
    ----------
    qi : float
        Initial Rate
    di : float
        Decline Rate
    b : float
        Arps Constant b
    ti : Union[float,date]
        Date of the Initial Rate 'qi'
    freq_di : str
        Frequency at with is reported the decline rate

    Attributes
    ----------
    rate_time
        Estimate the time at which the Arps instance would reach the defined rate
    """
    def __init__(self,qi:float, di:float, b:float, ti:Union[float,date],freq_di:str='M'):
        """__init__ Initiate instance of Arps Decline Curve Type

        Parameters
        ----------
        qi : float
            Initial Rate
        di : float
            Decline Rate
        b : float
            Arps Constant b
        ti : Union[float,date]
            Date of the Initial Rate 'qi'
        freq_di : str
            Frequency at with is reported the decline rate

        Returns
        -------
        Arps
            Return an instance of Arps class
        """
        self.qi = qi 
        self.di = di 
        self.b = b
        self.ti = ti 
        self.freq_di = freq_di
        self.format = 'date' if isinstance(self.ti,date) else 'number'

    #####################################################
    ############## Properties ###########################

        @property
        def qi(self):
            return self._qi

        @qi.setter
        def qi(self,value):
            try:
                value = float(value)
            except Exception as e: 
                print(e)
                raise
            else:
                self._qi = value
                
        @property
        def di(self):
            return self._di

        @di.setter
        def di(self,value):
            try:
                value = float(value)
            except Exception as e: 
                print(e)
                raise
            else:
                self._di = value
                
        @property
        def b(self):
            return self._b

        @b.setter
        def b(self,value):
            try:
                value = float(value)
            except Exception as e: 
                print(e)
                raise
            else:
                self._b = value
            
        @property
        def ti(self):
            return self._ti

        @ti.setter
        def ti(self,value):
            try:
                assert isinstance(value,(float,date))
            except Exception as e: 
                print(e)
                raise
            else:
                self._ti = value
        
        @property
        def freq_di(self):
            return self._ti

        @freq_di.setter
        def ti(self,value):
            try:
                assert value in list_freq
            except Exception as e: 
                print(e)
                raise
            else:
                self._freq_di = value

    def ti_n(self):
        if self.format == 'number':
            return self.ti
        else:
            return self.ti.toordinal()
                
    def __repr__(self):
        return 'Declination \n Ti: {self.ti} \n Qi: {self.qi} bbl/d \n Rate: {self.di} {self.freq_di} \n b: {self.b}'.format(self=self)

    def __str__(self):
        return 'Declination \n Ti: {self.ti} \n Qi: {self.qi} bbl/d \n Rate: {self.di} {self.freq_di} \n b: {self.b}'.format(self=self)
                

    def rate_time(self,rate:Union[int,float,np.ndarray],freq:str='D')->np.ndarray:
        """rate_time Estimate the time at which the Arps Instance would reach the given rate

        Parameters
        ----------
        rate : Union[int,float,np.ndarray]
            Rates at which are desired to estimate the time

        freq : str
            Time frecuency

        Returns
        -------
        np.ndarray
            array of times
        """      
        freq = 'D' if self.format=='date' else freq
        di_factor = converter_factor(self.freq_di,freq)
        time = arps_rate_time(self.qi,self.di*di_factor,self.b,rate)
        return time 
    
    def forecast(self,start:Union[date,float]=None, end:Union[date,float]=None, rate_limit:float=None,
                 np_limit:float=None, freq_input:str='D', freq_out:str='M')->pd.DataFrame:
        """forecast Estimate the forecast given the Arps parameters, dates and limits.

        Parameters
        ----------
        start :Union[float,date], optional
            The first date at which the DataFrame will start. If not specified,
            the Arps.ti parameter is used, by default None
        end : Union[float,date], optional
            The maximum date at which the DataFrame will end. if the resulting date
            at which either econ_limit or np_limit reach the rate limit is beyond end_date,
            the last date will be end_date, otherwise the date estimated, by default None
        rate_limit : float, optional
            Rate at which the forecast will stop, by default None
        np_limit : float, optional
            Cumulative volume at which the forecast will stop, by default None
        freq_input : str, optional
            Frequency at which the estimations will be performed. 
            By default the forecast is estimated on daily basis. , by default 'D'
        freq_out : str, optional
            Frequency at which the forecast will be returned. 
            by default the frequency will be on monthly basis, by default 'M'

        Returns
        -------
        pd.DataFrame
            Result DataFrame indexed by DateTime array
        """
        
        if self.format == 'date':
            assert all(isinstance(i,date) for i in [start,end])
            time_range = pd.Series(pd.date_range(start=start, end=end, freq=freq_input))
            time_array = time_range.apply(lambda x: x.toordinal()) - self.ti.toordinal()

            di_factor = converter_factor(self.freq_di,'D')
            if rate_limit is not None:
                time_limit = self.rate_time(rate_limit)
                time_index = time_array<=time_limit
                time_array = time_array.loc[time_index]
                time_range = time_range.loc[time_index]
                
            _forecast = arps_forecast(self.qi,self.di*di_factor,self.b,time_array)
        
        else:
            assert all(isinstance(i,(int,float)) for i in [start,end])
            
            fq = converter_factor(freq_input,freq_out)
            assert fq>=1, 'The output frecuency must be greater than input'
            time_range = np.arange(start, end, int(fq))
            time_array = np.arange(start, end, int(fq))
            di_factor = converter_factor(self.freq_di,freq_input)
            
            if rate_limit is not None:
                time_limit = self.rate_time(rate_limit,freq=freq_input)
                print(time_limit)
                time_index = time_array<=time_limit
                time_array = time_array[time_index]
                time_range = time_range[time_index]
        
            _forecast = arps_forecast(self.qi,self.di*di_factor,self.b,time_array,self.ti_n())
        
        _forecast_df = pd.DataFrame({'rate':np.squeeze(_forecast)},index=time_range)
        
        return _forecast_df