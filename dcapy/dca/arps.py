
#External Libraries Import
import numpy as np 
import pandas as pd 
from datetime import datetime, date, timedelta
from typing import Union
from scipy.optimize import curve_fit
#Local Imports
from .dca import DCA 
from .timeconverter import list_freq, converter_factor, time_converter_matrix
from ..filters import zscore

def arps_exp(time_array:np.ndarray,qi:float,di:float)->np.ndarray:
    """arps_exp Calculate the rate of Exponential, b=0, Arps Declination

    Parameters
    ----------
    qi : float
        Initial rate
    di : float
        Initial Declination
    time_array : np.ndarray
        Array of numbers that represents the periods of timeto calculate rate

    Returns
    -------
    np.ndarray
        Array of the rates calculated for the time_array
    """
    return qi*np.exp(-di*time_array)

def arps_hyp(time_array:np.ndarray,qi:float,di:float,b:float)->np.ndarray:
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
def arps_forecast(time_array:Union[np.ndarray, list],qi:Union[np.ndarray,float],di:Union[np.ndarray,float],
                 b:Union[np.ndarray,float],
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
    #print(params_dict)
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
            time_diff,
            params_dict['qi'],
            params_dict['di'],
        ),
        arps_hyp(
            time_diff,
            params_dict['qi'],
            params_dict['di'],
            params_dict['b']
        )
    )
    
    
    return np.squeeze(f.T)



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
    def __init__(self,qi:float=None, di:float=None, b:float=None, ti:Union[float,date]=None,freq_di:str='M'):
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

    #####################################################
    ############## Properties ###########################
    
            
        @property
        def qi(self):
            return self._qi

        @qi.setter
        def qi(self,value):
            if value is not None:
                try:
                    value = float(value)
                except Exception as e: 
                    print(e)
                    self._qi = None
            else:
                self._qi = value
                
        @property
        def di(self):
            return self._di

        @di.setter
        def di(self,value):
            if value is not None:
                try:
                    value = float(value)
                except Exception as e: 
                    print(e)
                    self._di = None
            else:
                self._di = value
                
        @property
        def b(self):
            return self._b

        @b.setter
        def b(self,value):
            if value is not None:
                try:
                    value = float(value)
                except Exception as e: 
                    print(e)
                    self._b = None
            else:
                self._b = value
            
        @property
        def ti(self):
            return self._ti

        @ti.setter
        def ti(self,value):
            if value is not None:
                try:
                    assert isinstance(value,(float,date))
                except Exception as e: 
                    print(e)
                    self._ti = None
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
        if self.format() == 'number':
            return self.ti
        else:
            return self.ti.toordinal()


    def format(self):
        if isinstance(self.ti,date):
            return 'date'
        else:
            return 'number'
                
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
        freq = 'D' if self.format()=='date' else freq
        di_factor = converter_factor(self.freq_di,freq)
        time = arps_rate_time(self.qi,self.di*di_factor,self.b,rate)
        return time 
    
    def forecast(self,start:Union[date,float]=None, end:Union[date,float]=None, rate_limit:float=None,
                 np_limit:float=None, freq_input:str='D', freq_output:str='M')->pd.DataFrame:
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
        freq_output : str, optional
            Frequency at which the forecast will be returned. 
            by default the frequency will be on monthly basis, by default 'M'

        Returns
        -------
        pd.DataFrame
            Result DataFrame indexed by DateTime array
        """
        
        if self.format() == 'date':
            assert all(isinstance(i,date) for i in [start,end])
            time_range = pd.Series(pd.date_range(start=start, end=end, freq=freq_input))
            time_array = time_range.apply(lambda x: x.toordinal()) - self.ti.toordinal()

            di_factor = converter_factor(self.freq_di,'D')
            if rate_limit is not None:
                time_limit = self.rate_time(rate_limit)
                time_index = time_array<=time_limit
                time_array = time_array.loc[time_index]
                time_range = time_range.loc[time_index]
                
            _forecast = arps_forecast(time_array,self.qi,self.di*di_factor,self.b)
            _forecast_df = pd.DataFrame({'rate':np.squeeze(_forecast)},index=time_range)
        else:
            assert all(isinstance(i,(int,float)) for i in [start,end])
            
            fq = converter_factor(freq_input,freq_output)
            assert fq>=1, 'The output frecuency must be greater than input'
            time_array = np.arange(start, end, int(fq))
            di_factor = converter_factor(self.freq_di,freq_input)
            
            if rate_limit is not None:
                time_limit = self.rate_time(rate_limit,freq=freq_input)
                print(time_limit)
                time_index = time_array<=time_limit
                time_array = time_array[time_index]
        
            _forecast = arps_forecast(time_array,self.qi,self.di*di_factor,self.b,self.ti_n())
        
            _forecast_df = pd.DataFrame({'rate':np.squeeze(_forecast)},index=time_array)
        
        return _forecast_df
    
    def fit(self,df:pd.DataFrame=None,time:Union[str,np.ndarray,pd.Series]=None,
            rate:Union[str,np.ndarray,pd.Series]=None,b:float=None, filter=None,kw_filter={}):
        """fit Fit a production time series to a parameterized Arps Ecuation. Optionally,
        a anomaly detection filter can be passed. It returns an Arps Instance with the fitted
        attributes.

        Parameters
        ----------
        df : pd.DataFrame, optional
            pandas DataFrame with the information to be fitted , by default None
        time : Union[str,np.ndarray,pd.Series], optional
            Column name of the df DataFrame or array with the time information, by default None
        rate : Union[str,np.ndarray,pd.Series], optional
            Column name of the df DataFrame or array with the rate information, by default None
        b : float, optional
            b Arps coefficient. If None it becomes an additional parameter to fit, by default None
        filter : str, optional
            [description], by default None

        Returns
        -------
        Arps
            [description]
        """
        
        #Check inputs
        x = df[time].values if isinstance(time,str) else time 
        y = df[rate].values if isinstance(rate,str) else rate
        
        #Keep production greater than 0
        zeros_filter_array = np.zeros(x.shape)
        zeros_filter_array[y<=0] == 1
        
        #Apply filter 
        anomaly_filter_array = np.zeros(x.shape)
        if filter is not None:
            if callable(filter):
                anomaly_array = filter(x[zeros_filter_array==0],y[zeros_filter_array==0],**kw_filter)
            elif isinstance(filter,str):
                anomaly_array = eval(f'{filter}(x[zeros_filter_array==0],y[zeros_filter_array==0],**kw_filter)')

            #Rebuild the full anomaly array with the original input shape
            anomaly_filter_array[zeros_filter_array==0] = anomaly_array
        
        total_filter = zeros_filter_array + anomaly_filter_array
        
        if b is None:
            def cost_function(_x,_qi,_di,_b):
                return arps_forecast(_x,_qi,_di,_b)
            try:
                vtoordinal = np.vectorize(datetime.toordinal)
                _x = vtoordinal(x)
            except Exception as e:
                print(e)
                _x = x.astype(float)

            
            popt, pcov = curve_fit(cost_function, _x[total_filter==0]-_x[total_filter==0][0], y[total_filter==0], bounds=(0.0, [np.inf, np.inf, 1]))
            
            self.qi = popt[0]
            self.di = popt[1]
            self.b = popt[2]
            self.ti = x[total_filter==0][0]
        else:
            def cost_function(x,qi,di):
                return arps_forecast(x,qi,di,b)
            try:
                vtoordinal = np.vectorize(datetime.toordinal)
                _x = vtoordinal(x)
            except Exception as e:
                print(e)
                _x = x.astype(float)
            popt, pcov = curve_fit(cost_function, _x[total_filter==0], y[total_filter==0], bounds=(0.0, [np.inf, np.inf]))
   
            self.qi = popt[0]
            self.di = popt[1]
            self.ti = x[total_filter==0][0]
            self.b = b
        return pd.DataFrame({'time':x,'rate':y,'filter':total_filter})
        
        
        
                
        
                
        
        