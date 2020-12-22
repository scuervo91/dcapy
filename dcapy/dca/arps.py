
#External Libraries Import
import numpy as np 
import pandas as pd 
from datetime import datetime, date, timedelta
from typing import Union
#Local Imports
from .dca import DCA 


def arps_exp(qi:float,di:float,b:float,time_array:np.ndarray)->np.ndarray:
    """arps_exp [Calculate the rate of Exponential, b=0, Arps Declination]

    Parameters
    ----------
    qi : float
        [Initial rate]
    di : float
        [Initial Declination]
    b : float
        [Arps Coeficient]
    time_array : np.ndarray
        [Array of numbers that represents the periods of timeto calculate rate]

    Returns
    -------
    np.ndarray
        [Array of the rates calculated for the time_array]
    """
    return qi*np.exp(-di*time_array)

def arps_hyp(qi:float,di:float,b:float,time_array:np.ndarray)->np.ndarray:
    """arps_exp [Calculate the rate of either Armonic or hyperbolic , b>0, Arps Declination]

    Parameters
    ----------
    qi : float
        [Initial rate]
    di : float
        [Initial Declination]
    b : float
        [Arps Coeficient]
    time_array : np.ndarray
        [Array of numbers that represents the periods of timeto calculate rate]

    Returns
    -------
    np.ndarray
        [Array of the rates calculated for the time_array]
    """
    return qi/np.power(1+b*di*time_array,1/b)

#Arps Decline Curve
def arps_forecast(qi:Union[np.ndarray,float],di:Union[np.ndarray,float],
                 b:Union[np.ndarray,float], time_array:Union[np.ndarray, list],
                 ti:Union[np.ndarray,float]=0.0)->np.ndarray:
    """arps_decline [Estimate the rate forecast for the time_array  given the Arps Parameters]

    Parameters
    ----------
    qi : float
        [Initial Rate at ti]
    di : float
        [Decline rate]
    b : float
        [description]
    time_array : Union[np.ndarray, list]
        [array of times to make forecast]
    ti : float, optional
        [Time of the initial rate qi], by default 0.0

    Returns
    -------
    np.ndarray
        [description]
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
               params_dict[i] = np.atleast_1d(params_dict[i])
            except Exception as e:
                print(e)
                raise
    
    time_diff = time_array - ti
    
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
                
            




# Dict of allowed di frequencies
di_freq_dict = {
    'A':365,
    'M':30.42,
    'D':1
}

class Arps(DCA):
    
    def __init__(self,qi:float, di:float, b:float, ti:date,freq_di:str='A'):
        """__init__ [Initiate instance of Arps Decline Curve Type]

        Parameters
        ----------
        qi : float
            [Initial Rate]
        di : float
            [Decline Rate]
        b : float
            [Arps Constant b]
        ti : date
            [Date of the Initial Rate 'qi']
        freq_di : str
            [Frequency at with is reported the decline rate]

        Returns
        -------
        Arps
            [Return an instance of Arps class]
        """
        self.qi = qi 
        self.di = di 
        self.b = b
        self.ti = ti 
        self.freq_di = freq_di

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
                assert isinstance(value,date)
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
                assert value in di_freq_dict.keys()
            except Exception as e: 
                print(e)
                raise
            else:
                self._freq_di = value
            
    def forecast(self,start_date:date=None, end_date:date=None, econ_limit:float=None,
                 np_limit:float=None, freq_input:str='D', freq_out:str='M')->pd.DataFrame:
        """forecast [Estimate the forecast given the Arps parameters, dates and limits.]

        Parameters
        ----------
        start_date : date, optional
            [The first date at which the DataFrame will start. If not specified,
            the Arps.ti parameter is used], by default None
        end_date : date, optional
            [The maximum date at which the DataFrame will end. if the resulting date
            at which either econ_limit or np_limit reach the rate limit is beyond end_date,
            the last date will be end_date, otherwise the date estimated], by default None
        econ_limit : float, optional
            [Rate at which the forecast will stop], by default None
        np_limit : float, optional
            [Cumulative volume at which the forecast will stop], by default None
        freq_input : str, optional
            [Frequency at which the estimations will be performed. 
            By default the forecast is estimated on daily basis. ], by default 'D'
        freq_out : str, optional
            [Frequency at which the forecast will be returned. 
            by default the frequency will be on monthly basis], by default 'M'

        Returns
        -------
        pd.DataFrame
            [Result DataFrame indexed by DateTime array]
        """