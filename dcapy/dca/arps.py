
#External Libraries Import
import numpy as np 
import pandas as pd 
from datetime import datetime, date, timedelta
from typing import Union
from scipy.optimize import curve_fit
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
#Local Imports
from .dca import DCA 
from .timeconverter import list_freq, converter_factor, time_converter_matrix, check_value_or_prob
from ..filters import zscore

def arps_exp_rate(time_array:np.ndarray,qi:float,di:float)->np.ndarray:
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
    time_array = np.atleast_1d(time_array)
    return qi*np.exp(-di*time_array)

def arps_exp_cumulative(time_array:np.ndarray,qi:float,di:float,ti=0)->np.ndarray:
    """arps_exp Calculate the Cumulative of Exponential, b=0, Arps Declination

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
        Array of the Cumulative calculated for the time_array
    """
    time_array = np.atleast_1d(time_array)
    return (qi/di)*(np.exp(-di*ti) - np.exp(-di*time_array))

def arps_hyp_rate(time_array:np.ndarray,qi:float,di:float,b:float)->np.ndarray:
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
    time_array = np.atleast_1d(time_array)
    return qi/np.power(1+b*di*time_array,1/b)

def arps_hyp_cumulative(time_array:np.ndarray,qi:float,di:float,b:float,ti=0)->np.ndarray:
    """arps_exp Calculate the cumulative of hyperbolic , 0<b<1, Arps Declination

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
        Array of the cumulative calculated for the time_array
    """
    time_array = np.atleast_1d(time_array)
    f = qi/(di*(b-1))
    g = np.power(b*di*time_array+1,(b-1)/b)
    h = np.power(b*di*ti+1,(b-1)/b)
    return f*(g-h)

def arps_arm_cumulative(time_array:np.ndarray,qi:float,di:float,b:float,ti=0)->np.ndarray:
    """arps_exp Calculate the cumulative of Armonic , b=1, Arps Declination

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
        Array of the cumulative calculated for the time_array
    """
    time_array = np.atleast_1d(time_array)
    return (qi/di)*np.log((di*time_array + 1)/(di*ti+1))

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
                # TODO Review atleast2D
               params_dict[i] = np.atleast_1d(params_dict[i]).reshape(-1,1)
            except Exception as e:
                print(e)
                raise
    
    time_diff = np.atleast_1d(time_array) - ti
    
    f = np.where(
        params_dict['b']==0,
        arps_exp_rate(
            time_diff,
            params_dict['qi'],
            params_dict['di'],
        ),
        arps_hyp_rate(
            time_diff,
            params_dict['qi'],
            params_dict['di'],
            params_dict['b']
        )
    )
    
    
    return np.squeeze(f.T)

def arps_cumulative(time_array:Union[np.ndarray, list],qi:Union[np.ndarray,float],di:Union[np.ndarray,float],
                 b:Union[np.ndarray,float],
                 ti:Union[np.ndarray,float]=0.0)->np.ndarray:
    """arps_cumulative Estimate the cumulative forecast for the time_array  given the Arps Parameters

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
        Production cumulative forecast in a numpy array
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
                # TODO Review atleast2D
               params_dict[i] = np.atleast_1d(params_dict[i]).reshape(-1,1)
            except Exception as e:
                print(e)
                raise
    
    time_diff = np.atleast_1d(time_array) - ti
       
    f = np.where(
        params_dict['b']==0,
        arps_exp_cumulative(time_diff,params_dict['qi'],params_dict['di']),
        np.where(
            params_dict['b']==1,
            arps_arm_cumulative(time_diff,params_dict['qi'],params_dict['di'],params_dict['b']),
            arps_hyp_cumulative(time_diff,params_dict['qi'],params_dict['di'],params_dict['b'])
        ))
      
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
    qi = np.atleast_1d(qi)
    di = np.atleast_1d(di)
    b = np.atleast_1d(b)

    time_until = np.where(
        b==0,
        np.log(qi / rate) * (1/di),
        (np.power(qi / rate, b) - 1)/(b * di)
    )

    #if b == 0:
    #    time_until = np.log(qi / rate) * (1/di)
    #else:
    #    time_until = (np.power(qi / rate, b) - 1)/(b * di)
    
    return time_until.astype(int)

            
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

    Methods
    ----------
    rate_time
        Estimate the time at which the Arps instance would reach the defined rate
    """
    def __init__(self,qi:float=None, di:float=None, b:float=None, ti:Union[float,date]=None,freq_di:str='M', seed:int=None):
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
        seed : int
            Seed for the random number generator

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
        self.seed = seed

    #####################################################
    ############## Properties ###########################
    
            
    @property
    def qi(self):
        return self._qi

    @qi.setter
    def qi(self,value):
        if value is not None:
            try:
                value = check_value_or_prob(value)
                self._qi = value
            except Exception as e: 
                print(e)
                raise Exception
        else:
            self._qi = None

    def get_qi(self,size=None, ppf=None):
        if isinstance(self.qi,stats._distn_infrastructure.rv_frozen):
            if size is None:
                return self.qi.mean()
            elif ppf is None:
                return self.qi.rvs(size=size,random_state=self.seed)
            else:
                return self.qi.ppf(ppf)

        else:
            return self.qi

            
    @property
    def di(self):
        return self._di

    @di.setter
    def di(self,value):
        if value is not None:
            try:
                value = check_value_or_prob(value)
                self._di = value
            except Exception as e: 
                print(e)
                raise Exception
        else:
            self._di = None

    def get_di(self,size=None, ppf=None):
        if isinstance(self.di,stats._distn_infrastructure.rv_frozen):
            if size is None:
                return self.di.mean()
            elif ppf is None:
                return self.di.rvs(size=size,random_state=self.seed)
            else:
                return self.di.ppf(ppf)

        else:
            return self.di
            
    @property
    def b(self):
        return self._b

    @b.setter
    def b(self,value):
        if value is not None:
            try:
                value = check_value_or_prob(value)
                self._b = value
            except Exception as e: 
                print(e)
                raise Exception
        else:
            self._b = None

    def get_b(self,size=None, ppf=None):
        if isinstance(self.b,stats._distn_infrastructure.rv_frozen):
            if size is None:
                return self.b.mean()
            elif ppf is None:
                return self.b.rvs(size=size,random_state=self.seed)
            else:
                return self.b.ppf(ppf)

        else:
            return self.b
        
    @property
    def ti(self):
        return self._ti

    @ti.setter
    def ti(self,value):
        if value is not None:
            try:
                assert isinstance(value,(int,date))
                self._ti = value
            except Exception as e: 
                print(e)
                raise Exception
        else:
            self._ti = None
    
    @property
    def freq_di(self):
        return self._freq_di

    @freq_di.setter
    def freq_di(self,value):
        try:
            assert value in list_freq
            self._freq_di = value
        except Exception as e: 
            print(e)
            raise Exception

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
        return 'Declination \n Ti: {self.ti} \n Qi: {self.qi} bbl/d \n Di: {self.di} {self.freq_di} \n b: {self.b}'.format(self=self)

    def __str__(self):
        return 'Declination \n Ti: {self.ti} \n Qi: {self.qi} bbl/d \n Di: {self.di} {self.freq_di} \n b: {self.b}'.format(self=self)
                
    @staticmethod
    def rate_time(qi:Union[np.ndarray,float],di:Union[np.ndarray,float],
                 b:Union[np.ndarray,float], rate:Union[int,float,np.ndarray])->np.ndarray:
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

        return arps_rate_time(qi,di,b,rate)
    
    def forecast(self,time_list:Union[pd.Series,np.ndarray]=None,start:Union[date,float]=None, end:Union[date,float]=None, rate_limit:float=None,
                 np_limit:float=None, freq_input:str='D', freq_output:str='M', n:int=None,ppf=None)->pd.DataFrame:
        """forecast Estimate the forecast given the Arps parameters, dates and limits.

        Parameters
        ----------
        time_list: Union[float,date], optional
            A numpy array or pandas Series with dtype datetime64 when format date
            is used else with dtype float for days numbers. It is used for custom time, by default None
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
        n: int, optional
            Number of samples to be simulated using Montecarlo simulation
        ppf: float, optional
            Percentil number to be generated instead if random numbers when a probability
            distribution is set

        Returns
        -------
        pd.DataFrame
            Result DataFrame indexed by DateTime array
        """
        
        #If the Instance format is date perform operations to convert
        # the dates to ordinal and estimate the production rates
        if self.format() == 'date':

            #Check if the time range was given. If True, use this to estimate the time array for
            # the Forecast
            if time_list is not None:
                assert isinstance(time_list, (pd.Series, np.ndarray)), f'Must be np.array or pd.Series with dtype datetime64. {type(time_array)} was given'
                assert np.issubdtype(time_list.dtype, np.datetime64), f'dtype must be datetime64. {time_array.dtype} was given'
                time_list = pd.Series(time_list).dt.to_period(freq_output)
            else:
                assert all(isinstance(i,date) for i in [start,end])
                time_list = pd.period_range(start=start, end=end, freq=freq_output)

            time_range = pd.Series(time_list)
            time_array = time_range.apply(lambda x: x.to_timestamp().toordinal()) - self.ti.toordinal()
            time_array = time_array.values
            di_factor = converter_factor(self.freq_di,'D')
        else:
            if time_list is not None:
                time_list = np.atleast_1d(time_list)
                assert isinstance(time_list, (pd.Series, np.ndarray)), f'Must be np.array or pd.Series with dtype datetime64. {type(time_array)} was given'
                assert np.issubdtype(time_list.dtype, np.integer), f'dtype must be integer. {time_array.dtype} was given'
            else:
                assert all(isinstance(i,(int,float)) for i in [start,end])          
                fq = converter_factor(freq_input,freq_output)
                assert fq>=1, 'The output frecuency must be greater than input'
                time_list = np.arange(start, end, int(fq))

            time_array = time_list
            time_range = time_list
            di_factor = converter_factor(self.freq_di,freq_input)

        
        qi = self.get_qi(size=n, ppf=ppf)
        di = self.get_di(size=n, ppf=ppf)*di_factor
        b = self.get_b(size=n, ppf=ppf)
            
        if rate_limit is not None:
            time_limit = self.rate_time(qi,di,b,rate_limit)
            time_index = time_array<=time_limit.reshape(-1,1)

            if n is None:
                time_index = time_array>time_limit
                time_array = time_array[time_index]
                time_range = time_range[time_index]
            else:
                time_array = np.tile(time_array,(size,1))[time_index] = np.nan
                
        cum_factor = converter_factor('D',freq_input)
        _forecast = arps_forecast(time_array,qi,di,b).flatten('F')
        _cumulative = arps_cumulative(time_array,qi*cum_factor,di,b).flatten('F')
        _iterations = np.repeat(np.arange(0,n),_forecast.shape[0]/n) if n is not None else np.zeros(_forecast.shape)
        _forecast_df = pd.DataFrame(
            {
                'rate':np.squeeze(_forecast),
                'cumulative':np.squeeze(_cumulative),
                'iteration':_iterations
            },
                index=np.tile(time_range,n) if n is not None else time_range)
        
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
        # TODO: Add the option to start the cumulative with an Initial Value different a 0
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

            #Apply the Filters
            x_filter = _x[total_filter==0]-_x[total_filter==0][0]
            y_filter = y[total_filter==0]
            
            #Optimization process
            popt, pcov = curve_fit(cost_function, x_filter, y_filter, bounds=(0.0, [np.inf, np.inf, 1]))
            
            #Assign the results to the Class
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
             
            #Apply the Filters   
            x_filter = _x[total_filter==0]-_x[total_filter==0][0]
            y_filter = y[total_filter==0]
            
            #Optimization process
            popt, pcov = curve_fit(cost_function, x_filter, y_filter, bounds=(0.0, [np.inf, np.inf]))
   
            self.qi = popt[0]
            self.di = popt[1]
            self.ti = x[total_filter==0][0]
            self.b = b
            
        return pd.DataFrame({'time':x,'rate':y,'filter':total_filter})
        
        
    def plot(self, start:Union[float,date]=None, end:Union[float,date]=None,
             freq_input:str='D',freq_output:str='M',rate_limit:float=None,
             np_limit:float=None,n:int=None,ppf=None,ax=None,rate_kw:dict={},cum_kw:dict={},
             ad_kw:dict={},cum:bool=False,anomaly:float=False, **kwargs):
        """plot. Make a Plot in a Matplotlib axis of the rate forecast. 
         Optionally plot the cumulative curve in a second vertical axis.

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
        ax : [type], optional
            Matplotlib axes. If None it creates a new axes
        rate_kw : dict, optional
            Dictionary with the Matplotlib properties of the rate curve.
            For example to change the color, width, style.
        cum_kw : dict, optional
            Dictionary with the Matplotlib properties of the rate curve.
            For example to change the color, width, style.
        ad_kw : dict, optional
            Dictionary with the Matplotlib properties of the rate curve.
            For example to change the color, width, style.
        cum : bool, optional
            If True it plots the cumulative curve
        anomaly : float, optional
            If True it plots the anomaly curve
        """
        f = self.forecast(start=start, end=end, 
                            freq_input=freq_input,freq_output=freq_output,
                            rate_limit=rate_limit, np_limit=np_limit, n=n, ppf=ppf)
        #Create the Axex
        dax= ax or plt.gca()

        # Default kwargs for rate
        def_rate_kw = {
            'color': 'darkgreen',
            'linestyle':'--',
            'linewidth': 2
        }
        for (k,v) in def_rate_kw.items():
            if k not in rate_kw:
                rate_kw[k]=v

        # Default kwargs for cum
        def_cum_kw = {
            'color': 'darkgreen',
            'linestyle':'dotted',
            'linewidth': 2
        }
        for (k,v) in def_cum_kw.items():
            if k not in cum_kw:
                cum_kw[k]=v

        # Default kwargs for anomaly detection
        def_ad_kw = {
            'c': 'red',
            's':40,
            'marker': 'o'
        }
        for (k,v) in def_ad_kw.items():
            if k not in ad_kw:
                ad_kw[k]=v

        #Plotting
        time_axis = f.index.to_timestamp() if self.format()=='date' else f.index
        sns.lineplot(data=f, x=time_axis, y='rate', hue='iteration',**rate_kw, ax=dax)
        #dax.plot(time_axis,f['rate'],**rate_kw)   

        if cum:
            cumax=dax.twinx()
            cumax.plot(time_axis,f['cumulative'],**cum_kw)  


                
        
                
        
        