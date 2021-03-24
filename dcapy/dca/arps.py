
#External Libraries Import
import numpy as np 
import pandas as pd 
from datetime import datetime, date, timedelta
from typing import Union
from scipy.optimize import curve_fit
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pydantic import BaseModel, Field
from typing import Union, List, Optional
#Local Imports
from .dca import DCA, ProbVar
from .timeconverter import list_freq, converter_factor, time_converter_matrix, check_value_or_prob, FreqEnum
from ..filters import zscore

def arps_exp_rate(time_array:np.ndarray,qi:float,di:float)->np.ndarray:
    """arps_exp_rate Calculate the rate of Exponential, b=0, Arps Declination

    Args:
        time_array (np.ndarray): Initial Rate
        qi (float): Initial Flow
        di (float): Nominal Declination rate 

    Returns:
        np.ndarray: Array of the rates calculated for the time_array
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
               params_dict[i] = np.atleast_2d(params_dict[i]).reshape(-1,1)
            except Exception as e:
                print(e)
                raise
    
    time_diff = np.atleast_1d(time_array).astype(float) - params_dict['ti']
    time_diff[time_diff<0] = np.nan
    
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
    
    time_diff = np.atleast_1d(time_array).astype(float) - params_dict['ti']
       
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
                 b:Union[np.ndarray,float], rate:Union[int,float,np.ndarray],ti:Union[int,float,np.ndarray]=0)->int:
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
    ti = np.atleast_1d(ti)

    time_until = np.where(
        b==0,
        np.log(qi / rate) * (1/di),
        (np.power(qi / rate, b) - 1)/(b * di)
    ) + ti

    #if b == 0:
    #    time_until = np.log(qi / rate) * (1/di)
    #else:
    #    time_until = (np.power(qi / rate, b) - 1)/(b * di)
    
    return time_until.astype(int)

            
class Arps(BaseModel,DCA):
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
    qi: Union[ProbVar,List[float],float] = Field(None)
    di: Union[ProbVar,List[float],float] = Field(None)
    b: Union[ProbVar,List[float],float] = Field(None)
    ti: Union[int,date,List[int],List[date]] = Field(None)
    freq_di: FreqEnum = Field('M')
    seed : Optional[int] = Field(None)
    fluid_rate: Optional[Union[float,List[float]]] = Field(None)
    bsw: Optional[Union[float,List[float]]] = Field(None)
    wor: Optional[Union[float,List[float]]] = Field(None)
    gor: Optional[Union[float,List[float]]] = Field(None)
    glr: Optional[Union[float,List[float]]] = Field(None)

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True

    #def __init__(self,qi:float=None, di:float=None, b:float=None, ti:Union[float,date]=None,freq_di:str='M', seed:int=None):
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
        #self.qi = qi 
        #self.di = di 
        #self.b = b
        #self.ti = ti 
        #self.freq_di = freq_di
        #self.seed = seed

    #####################################################
    ############## Properties ###########################
    
            
    def get_qi(self,size=None, ppf=None):
        if isinstance(self.qi,ProbVar):
            return self.qi.get_sample(size=size, ppf=ppf)
        else:
            return np.atleast_1d(self.qi)

            
    def get_di(self,size=None, ppf=None):
        if isinstance(self.di,ProbVar):
            return self.di.get_sample(size=size, ppf=ppf)
        else:
            return np.atleast_1d(self.di)
            

    def get_b(self,size=None, ppf=None):
        if isinstance(self.b,ProbVar):
            return self.b.get_sample(size=size, ppf=ppf)
        else:
            return np.atleast_1d(self.b)
        

    def ti_n(self):
        if self.format() == 'number':
            return self.ti
        else:
            return self.ti.toordinal()


    def format(self):
        if isinstance(self.ti,date):
            return 'date'
        elif isinstance(self.ti,int):
            return 'number'
        elif isinstance(self.ti,list):
            if isinstance(self.ti[0],date):
                return 'date'
            else:
                return 'number'
                
    def __repr__(self):
        return 'Declination \n Ti: {self.ti} \n Qi: {self.qi} bbl/d \n Di: {self.di} {self.freq_di} \n b: {self.b}'.format(self=self)

    def __str__(self):
        return 'Declination \n Ti: {self.ti} \n Qi: {self.qi} bbl/d \n Di: {self.di} {self.freq_di} \n b: {self.b}'.format(self=self)
                
    @staticmethod
    def rate_time(qi:Union[np.ndarray,float],di:Union[np.ndarray,float],
                 b:Union[np.ndarray,float], rate:Union[int,float,np.ndarray],ti=None)->np.ndarray:
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

        return arps_rate_time(qi,di,b,rate, ti=ti)
    
    def forecast(self,time_list:Union[pd.Series,np.ndarray]=None,start:Union[date,float]=None, end:Union[date,float]=None, rate_limit:float=None,
                 cum_limit:float=None, freq_input:str='D', freq_output:str='M', iter:int=1,ppf=None, **kwargs)->pd.DataFrame:
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
            at which either rate_limit or cum_limit reach the rate limit is beyond end_date,
            the last date will be end_date, otherwise the date estimated, by default None
        rate_limit : float, optional
            Rate at which the forecast will stop, by default None
        cum_limit : float, optional
            Cumulative volume at which the forecast will stop, by default None
        freq_input : str, optional
            Frequency at which the estimations will be performed. 
            By default the forecast is estimated on daily basis. , by default 'D'
        freq_output : str, optional
            Frequency at which the forecast will be returned. 
            by default the frequency will be on monthly basis, by default 'M'
        iter: int, optional
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
                assert isinstance(time_list, (pd.Series, np.ndarray)), f'Must be np.array or pd.Series with dtype datetime64. {type(time_list)} was given'
                assert np.issubdtype(time_list.dtype, np.datetime64), f'dtype must be datetime64. {time_list.dtype} was given'
                time_list = pd.Series(time_list).dt.to_period(freq_output)
            else:
                assert all(isinstance(i,date) for i in [start,end])
                time_list = pd.period_range(start=start, end=end, freq=freq_output)

            ti_array = np.array([i.toordinal() for i in np.atleast_1d(self.ti)], dtype=int)
            ti_delta = ti_array - ti_array[0]

            time_range = pd.Series(time_list)
            time_array = time_range.apply(lambda x: x.to_timestamp().toordinal()) - ti_array.min()
            time_array = time_array.values
            di_factor = converter_factor(self.freq_di,'D')
        else:
            if time_list is not None:
                time_list = np.atleast_1d(time_list)
                assert isinstance(time_list, (pd.Series, np.ndarray)), f'Must be np.array or pd.Series with dtype datetime64. {type(time_list)} was given'
                assert np.issubdtype(time_list.dtype, np.integer), f'dtype must be integer. {time_list.dtype} was given'
            else:
                assert all(isinstance(i,(int,float)) for i in [start,end])     
                fq = converter_factor(freq_input,freq_output)
                assert fq>=1, 'The output frecuency must be greater than input'
                time_list = np.arange(start, end, int(fq))

            ti_delta = np.zeros(1)
            time_array = time_list
            time_range = time_list
            di_factor = converter_factor(self.freq_di,freq_input)

        
        qi = self.get_qi(size=iter, ppf=ppf)
        di = self.get_di(size=iter, ppf=ppf)*di_factor
        b = self.get_b(size=iter, ppf=ppf)
        
        
        iter = np.array([i.shape[0] for i in [qi,di,b,ti_delta]]).max()

        if rate_limit is not None:
            time_limit = self.rate_time(qi,di,b,rate_limit, ti=ti_delta)
            if iter==1:
                time_index = time_array<time_limit
                time_array = time_array[time_index]
                time_range = time_range[time_index]
            else:
                time_index = time_array<=time_limit.reshape(-1,1)
                time_array = np.tile(time_array,(iter,1)).astype('float')
                time_array[~time_index] = np.nan
                
        cum_factor = converter_factor('D',freq_input) if self.format() == 'number' else 1
        _forecast = arps_forecast(time_array,qi,di,b,ti=ti_delta).flatten('F')
        _cumulative = arps_cumulative(time_array,qi*cum_factor,di,b,ti=ti_delta).flatten('F')
        _iterations = np.repeat(np.arange(0,iter),_forecast.shape[0]/iter) #if n is not None else np.zeros(_forecast.shape)
        _forecast_df = pd.DataFrame(
            {
                'oil_rate':np.squeeze(_forecast),
                'oil_cum':np.squeeze(_cumulative),
                'iteration':_iterations
            },
                index=np.tile(time_range,iter) #if n is not None else time_range)
        )
        _forecast_df.index.name='date'
        for i in _forecast_df['iteration'].unique():
            _forecast_df.loc[_forecast_df['iteration']==i,'oil_volume'] = np.diff(_forecast_df.loc[_forecast_df['iteration']==i,'oil_cum'].values,prepend=0)
                
        #Water Rate
        if any([i is not None for i in [self.fluid_rate,self.bsw,self.wor]]):
                              
            if self.fluid_rate:
                _forecast_df['fluid_rate'] = self.fluid_rate if isinstance(self.fluid_rate,float) else np.tile(self.fluid_rate,iter)
                _forecast_df['water_rate'] = _forecast_df['fluid_rate'] - _forecast_df['oil_rate']
                _forecast_df['bsw'] = _forecast_df['water_rate'] / _forecast_df['fluid_rate']
                _forecast_df['wor'] = _forecast_df['water_rate'] / _forecast_df['oil_rate']
            elif self.bsw:
                _forecast_df['bsw'] = self.bsw if isinstance(self.bsw,float) else np.tile(self.bsw,iter)
                _forecast_df['water_rate'] = (_forecast_df['bsw']*_forecast_df['oil_rate'])/(1-_forecast_df['bsw'])
                _forecast_df['fluid_rate'] = _forecast_df['oil_rate'] + _forecast_df['water_rate']
                _forecast_df['wor'] = _forecast_df['water_rate'] / _forecast_df['oil_rate']
            else:
                _forecast_df['wor'] = self.wor if isinstance(self.wor,float) else np.tile(self.wor,iter)
                _forecast_df['bsw'] = _forecast_df['wor']/(_forecast_df['wor']+1)
                _forecast_df['water_rate'] = (_forecast_df['bsw']*_forecast_df['oil_rate'])/(1-_forecast_df['bsw'])
                _forecast_df['fluid_rate'] = _forecast_df['oil_rate'] + _forecast_df['water_rate']
            
            for i in _forecast_df['iteration'].unique():
                _f_index = _forecast_df.loc[_forecast_df['iteration']==i].index
                if self.format() == 'date':
                    delta_time = np.diff(pd.Series(_f_index.to_timestamp()).apply(lambda x: x.toordinal()))
                    delta_time = np.append(0,delta_time)
                else:
                    delta_time = np.diff(_f_index,prepend=0)
                    
                _forecast_df.loc[_forecast_df['iteration']==i,'water_cum'] = _forecast_df.loc[_forecast_df['iteration']==i,'water_rate'].multiply(cum_factor).multiply(delta_time).cumsum()
                _forecast_df.loc[_forecast_df['iteration']==i,'fluid_cum'] = _forecast_df.loc[_forecast_df['iteration']==i,'fluid_rate'].multiply(cum_factor).multiply(delta_time).cumsum()                
                _forecast_df.loc[_forecast_df['iteration']==i,'water_volume'] = np.diff(_forecast_df.loc[_forecast_df['iteration']==i,'water_cum'].values,prepend=0)
                _forecast_df.loc[_forecast_df['iteration']==i,'fluid_volume'] = np.diff(_forecast_df.loc[_forecast_df['iteration']==i,'fluid_cum'].values,prepend=0) 
        #Gas Rate
        if any([i is not None for i in [self.gor,self.glr]]):
                              
            if self.gor:
                _forecast_df['gor'] = self.gor if isinstance(self.gor,float) else np.tile(self.gor,iter)
                _forecast_df['gas_rate'] = _forecast_df['oil_rate'] * _forecast_df['gor']
            elif self.glr and 'fluid_rate' in _forecast_df.columns:
                _forecast_df['glr'] = self.glr if isinstance(self.glr,float) else np.tile(self.glr,iter)
                _forecast_df['gas_rate'] = _forecast_df['fluid_rate'] * _forecast_df['glr']
                _forecast_df['gor'] = _forecast_df['gas_rate'] / _forecast_df['oil_rate']
            
            for i in _forecast_df['iteration'].unique():
                _f_index = _forecast_df.loc[_forecast_df['iteration']==i].index
                if self.format() == 'date':
                    delta_time = np.diff(pd.Series(_f_index.to_timestamp()).apply(lambda x: x.toordinal()))
                    delta_time = np.append(0,delta_time)
                else:
                    delta_time = np.diff(_f_index,prepend=0)
                    
                _forecast_df.loc[_forecast_df['iteration']==i,'gas_cum'] = _forecast_df.loc[_forecast_df['iteration']==i,'gas_rate'].multiply(cum_factor).multiply(delta_time).cumsum()
                _forecast_df.loc[_forecast_df['iteration']==i,'gas_volume'] = np.diff(_forecast_df.loc[_forecast_df['iteration']==i,'gas_cum'].values,prepend=0)

        return _forecast_df.dropna()
    
    def fit(self,df:pd.DataFrame=None,time:Union[str,np.ndarray,pd.Series]=None,
            rate:Union[str,np.ndarray,pd.Series]=None,b:float=None, filter=None,kw_filter={},prob=False):
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
            if isinstance(x[0],(np.datetime64,date)):
                _x = np.array([pd.Timestamp(i).toordinal() for i in x])
            else:
                _x = x.astype(float)


            #Apply the Filters
            x_filter = _x[total_filter==0]-_x[total_filter==0][0]
            y_filter = y[total_filter==0]
            
            #Optimization process
            popt, pcov = curve_fit(cost_function, x_filter, y_filter, bounds=(0.0, [np.inf, np.inf, 1]))
            #Assign the results to the Class
            self.qi = {'dist':'norm','kw':{'loc':popt[0],'scale':np.sqrt(np.diag(pcov)[0])}} if prob else popt[0] 
            self.di = {'dist':'norm','kw':{'loc':popt[1],'scale':np.sqrt(np.diag(pcov)[1])}} if prob else popt[1]
            self.b = {'dist':'norm','kw':{'loc':popt[2],'scale':np.sqrt(np.diag(pcov)[2])}} if prob else popt[2]
            self.ti = pd.Timestamp(x[total_filter==0][0]) if isinstance(x[total_filter==0][0],(np.datetime64,date)) else x[total_filter==0][0]
        else:
            def cost_function(x,qi,di):
                return arps_forecast(x,qi,di,b)
            if isinstance(x[0],(np.datetime64,date)):
                _x = np.array([pd.Timestamp(i).toordinal() for i in x])
            else:
                _x = x.astype(float)

             
            #Apply the Filters   
            x_filter = _x[total_filter==0]-_x[total_filter==0][0]
            y_filter = y[total_filter==0]
            
            #Optimization process
            popt, pcov = curve_fit(cost_function, x_filter, y_filter, bounds=(0.0, [np.inf, np.inf]))
   
            self.qi = {'dist':'norm','kw':{'loc':popt[0],'scale':np.sqrt(np.diag(pcov)[0])}} if prob else popt[0] 
            self.di = {'dist':'norm','kw':{'loc':popt[1],'scale':np.sqrt(np.diag(pcov)[1])}} if prob else popt[1]
            self.ti = pd.Timestamp(x[total_filter==0][0]) if isinstance(x[total_filter==0][0],(np.datetime64,date)) else x[total_filter==0][0]
            self.b = b
            
        return pd.DataFrame({'time':x,'oil_rate':y,'filter':total_filter})
        
        
    def plot(self, start:Union[float,date]=None, end:Union[float,date]=None,
             freq_input:str='D',freq_output:str='M',rate_limit:float=None,
             cum_limit:float=None,iter:int=1,ppf=None,ax=None,rate_kw:dict={},cum_kw:dict={},
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
            at which either econ_limit or cum_limit reach the rate limit is beyond end_date,
            the last date will be end_date, otherwise the date estimated, by default None
        rate_limit : float, optional
            Rate at which the forecast will stop, by default None
        cum_limit : float, optional
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
                            rate_limit=rate_limit, cum_limit=cum_limit, iter=iter, ppf=ppf)
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
        sns.lineplot(data=f, x=time_axis, y='oil_rate', hue='iteration',**rate_kw, ax=dax)
        #dax.plot(time_axis,f['oil_rate'],**rate_kw)   

        if cum:
            cumax=dax.twinx()
            cumax.plot(time_axis,f['oil_cum'],**cum_kw)  


                
        
                
        
        