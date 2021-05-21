#External Imports
import numpy as np 
import pandas as pd 
from datetime import date, timedelta
from typing import Union, List, Optional
from pydantic import BaseModel, Field, Extra
from scipy import stats
import statsmodels.formula.api as smf
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
import yaml
#Local Imports
from .dca import DCA, ProbVar
from .timeconverter import list_freq, converter_factor, time_converter_matrix, check_value_or_prob, FreqEnum


def bsw_to_wor(bsw):
    assert isinstance(bsw,(int,float,np.ndarray,pd.Series,list))
    bsw = np.atleast_1d(bsw)
    assert np.all((bsw>=0)&(bsw<=1))
    wor = bsw/(1-bsw)
    return wor 

def wor_to_bsw(wor):
    assert isinstance(wor,(int,float,np.ndarray,pd.Series,list))
    wor = np.atleast_1d(wor)
    assert np.all(wor>=0)
    bsw = wor/(wor+1)
    return bsw   

def wor_forecast(time_array:np.ndarray,fluid_rate:Union[float,np.ndarray], slope:float, 
	wor_i:float, rate_limit:float = None,cum_limit:float=None, wor_limit:float=None):


    time_array = np.atleast_1d(time_array)
    fluid_rate = np.atleast_1d(fluid_rate)

    #delta_time = np.diff(time_array,append=0)
    delta_time = np.gradient(time_array)

    wor_i1 = wor_i + 1

    # Create arrays
    wor = np.zeros(time_array.shape[0])
    wor[0] = wor_i


    wor_1 = np.zeros(time_array.shape[0])
    wor_1[0] = wor_i + 1

    bsw = np.zeros(time_array.shape[0])
    bsw[0] = wor_to_bsw(wor[0])

    oil_rate = np.zeros(time_array.shape[0])
    oil_rate[0] = fluid_rate[0]*(1-bsw[0])
    water_rate = np.zeros(time_array.shape[0])
    water_rate[0]=fluid_rate[0]*bsw[0]

    oil_cum = np.zeros(time_array.shape[0])
    oil_cum[0] = oil_rate[0]*delta_time[0]

    water_cum = np.zeros(time_array.shape[0])
    water_cum[0] = water_rate[0]*delta_time[0]

    fluid_cum = np.zeros(time_array.shape[0])
    fluid_cum[0] = fluid_rate[0]*delta_time[0]

    for i in range(1,delta_time.shape[0]):
        wor[i] = np.exp(slope*oil_cum[i-1])*wor_i
        wor_1[i] = wor[i] + 1
        bsw[i] = wor_to_bsw(wor[i])
        oil_rate[i] = fluid_rate[i]*(1-bsw[i])
        water_rate[i] = fluid_rate[i]*bsw[i]
        oil_cum[i] = oil_cum[i-1] + oil_rate[i]*delta_time[i]
        water_cum[i] = water_cum[i-1] + water_rate[i]*delta_time[i]
        fluid_cum[i] = water_cum[i] + oil_cum[i]
        if rate_limit:
            if oil_rate[i] <= rate_limit:
                break

        if cum_limit:
            if oil_cum[i] >= cum_limit:
                break     

        if wor_limit:
            if wor[i] >= wor_limit:
                break          

    _forecast = pd.DataFrame(
    	{
            'oil_rate':oil_rate,
            'water_rate':water_rate,
            'oil_cum':oil_cum,
            'water_cum':water_cum,
            'bsw':bsw,
            'wor':wor,
            'wor_1':wor_1,
            'delta_time':delta_time,
            'fluid_rate':fluid_rate,
            'fluid_cum' : fluid_cum
            },
            index = time_array
    )
    
    _forecast.index.name = 'date'

    return _forecast[:i+1]



class Wor(BaseModel,DCA):

    bsw: Union[ProbVar,List[float],float] = Field(None)
    slope: Union[ProbVar,List[float],float] = Field(None)
    fluid_rate : Union[float,List[float],List[List[float]]] = Field(None)
    ti: Union[int,date,List[int],List[date]] = Field(None)
    seed : Optional[int] = Field(None)
    gor: Optional[Union[float,List[float]]] = Field(None)
    glr: Optional[Union[float,List[float]]] = Field(None)


    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        extra = Extra.forbid
        
    def get_layout(self):
        text = yaml.dump(self.dict(exclude_unset=True))  
        
        panel_text = ':large_blue_diamond: [bold]Wor[/bold]\n' + text
        panel = Panel.fit(panel_text,title='[bold blue]WOR Model[/bold blue]')
        #console.print(layout)
        return panel

    def get_bsw(self,size=None, ppf=None, seed=None):
        """get_bsw get the number of bsw

        Args:
            size ([type], optional): number of iterations. Defaults to None.
            ppf ([type], optional): percentil. Defaults to None.

        Returns:
            np.array: Array if bsw
        """
        if isinstance(self.bsw,ProbVar):
            return self.bsw.get_sample(size=size, ppf=ppf, seed=seed)
        else:
            return np.atleast_1d(self.bsw)

    def get_slope(self,size=None, ppf=None, seed=None):
        """get_slope get the number of slope

        Args:
            size ([type], optional): number of iterations. Defaults to None.
            ppf ([type], optional): percentil. Defaults to None.

        Returns:
            np.array: Array if slope
        """
        if isinstance(self.slope,ProbVar):
            return self.slope.get_sample(size=size, ppf=ppf, seed=seed)
        else:
            return np.atleast_1d(self.slope)

    def format(self)->str:
        """format return the time format the instance is initialized

        Returns:
            str: number or date
        """
        if isinstance(self.ti,date):
            return 'date'
        elif isinstance(self.ti,int):
            return 'number'
        elif isinstance(self.ti,list):
            if isinstance(self.ti[0],date):
                return 'date'
            else:
                return 'number'
            
    def fit(self, df:pd.DataFrame=None,time:Union[str,np.ndarray,pd.Series]=None, 
        oil_rate:Union[str,np.ndarray,pd.Series]=None,
        water_rate:Union[str,np.ndarray,pd.Series]=None,
        filter=None,kw_filter={},prob:bool=False, formula:str = "np.log(wor) ~ cum" ):
        
        #Check inputs
        time = df[time].values.astype('datetime64') if isinstance(time,str) else time.astype('datetime64')
        oil = df[oil_rate].values if isinstance(oil_rate,str) else oil_rate 
        water = df[water_rate].values if isinstance(water_rate,str) else water_rate
        
        #Keep production greater than 0
        oil_filter_array,water_filter_array  = np.zeros(oil.shape), np.zeros(water.shape)
        oil_filter_array[oil<=0] == 1
        water_filter_array[water<=0] == 1
        
        oil_water_filter = oil_filter_array + water_filter_array
        
        #Calculate WOR
        wor = water / oil
        
        #Estimate delta time
        delta_time = np.array(np.gradient(time),dtype='timedelta64[D]').astype('int64')
        #volume and cum
        oil_vol = oil * delta_time
        oil_cum = np.cumsum(oil_vol)
        
        #Apply filter 
        anomaly_filter_array = np.zeros(oil_cum.shape)
        if filter is not None:
            if callable(filter):
                anomaly_array = filter(oil_cum[oil_water_filter==0],wor[oil_water_filter==0],**kw_filter)
            elif isinstance(filter,str):
                anomaly_array = eval(f'{filter}(oil_cum[oil_water_filter==0],wor[oil_water_filter==0],**kw_filter)')

            #Rebuild the full anomaly array with the original input shape
            anomaly_filter_array[oil_water_filter==0] = anomaly_array
        
        #total filter
        total_filter = oil_water_filter + anomaly_filter_array
        
        # Regression
        
        oil_cum_filter = oil_cum[total_filter==0]
        wor_filter = wor[total_filter==0]
        data = pd.DataFrame({'cum':oil_cum_filter,'wor':wor_filter})

        #Model 
        mod = smf.ols(formula = formula, data = data)
        res = mod.fit()
        bsw_mean = wor_to_bsw(np.exp(res.params['Intercept']))
        
        # TODO: Check how to convert the standard deviation from the WOR interception to BSW Units
        bsw_std = wor_to_bsw(res.bse['Intercept'])

        self.bsw = {'dist':'norm','kw':{'loc':bsw_mean,'scale':bsw_std}} if prob else bsw_mean
        self.slope = {'dist':'norm','kw':{'loc':res.params['cum'],'scale':res.bse['cum']}} if prob else res.params['cum']
        self.ti = pd.Timestamp(time[total_filter==0][0]) if isinstance(time[total_filter==0][0],(np.datetime64,date)) else time[total_filter==0][0]
        self.fluid_rate = np.mean(oil + water)
        return pd.DataFrame({
            'time':time,
            'oil_rate':oil,
            'water_rate':water,
            'wor':wor,
            'oil_cum':oil_cum,
            'filter':total_filter})
       
    def forecast(self,time_list:Union[pd.Series,np.ndarray]=None,start:Union[date,float]=None, 
    	end:Union[date,float]=None, fluid_rate:Union[np.ndarray,float,list]=None,rate_limit:float=None,cum_limit:float=None, wor_limit:float=None,
    	freq_input:str='D', freq_output:str='D', iter:int=1,ppf=None,cum_i=0, seed=None,**kwargs)->pd.DataFrame:
        if self.format() == 'date':
            freq_input = 'D'
            #Check if the time range was given. If True, use this to estimate the time array for
            # the Forecast
            if time_list is not None:
                assert isinstance(time_list, (pd.Series, np.ndarray)), f'Must be np.array or pd.Series with dtype datetime64. {type(time_list)} was given'
                assert np.issubdtype(time_list.dtype, np.datetime64), f'dtype must be datetime64. {time_list.dtype} was given'
                time_list = pd.Series(time_list).dt.to_period(freq_input)
            else:
                assert all(isinstance(i,date) for i in [start,end])
                time_list = pd.period_range(start=start, end=end, freq=freq_input)

            ti_array = np.array([i.toordinal() for i in np.atleast_1d(self.ti)], dtype=int)
            time_range = pd.Series(time_list)
            time_array = time_range.apply(lambda x: x.to_timestamp().toordinal()).values - ti_array.reshape(-1,1)
        else:
            if time_list is not None:
                time_list = np.atleast_1d(time_list)
                assert isinstance(time_list, (pd.Series, np.ndarray)), f'Must be np.array or pd.Series with dtype datetime64. {type(time_list)} was given'
                assert np.issubdtype(time_list.dtype, np.integer), f'dtype must be integer. {time_list.dtype} was given'
            else:
                assert all(isinstance(i,(int,float)) for i in [start,end])     
                fq = converter_factor(freq_input,freq_output)
                assert fq>=1, 'The output frecuency must be greater than input'
                time_list = np.arange(start, end, 1)

            ti_array = np.atleast_1d(self.ti).astype(int)
            
            time_array = time_list - ti_array.reshape(-1,1)
            time_range = time_list


       	#Broadcast variables to set the total iterations

        #Get bsw and slope
        bsw = self.get_bsw(size=iter, ppf=ppf, seed=seed)
        slope = self.get_slope(size=iter, ppf=ppf, seed=seed)

        #Get the fluid Rate. 
        # If the result is a 2D numpy array the size must match the Time array 
        # with the form [iterations, time_array].
        #
        #If the result is 1D, the length of the vector is the number of iterations will be performed
        #This vector is broadcasted to a 2D array that match the time_array shape
        
        fluid_rate = np.atleast_2d(self.fluid_rate) if fluid_rate is None else np.atleast_2d(fluid_rate)
        

        #Broadcast three variables
        br = np.broadcast_shapes(bsw.shape,slope.shape,fluid_rate.shape[0],time_array.shape[0])
        
        #Convert varibles into broadcast shape
        _bsw = bsw * np.ones(br)
        _slope = slope * np.ones(br)
        time_array = time_array * np.ones((br[0],1))

        # make the fluid array to be consistent with the time array
        _fluid = fluid_rate * np.ones((br[0],time_array.shape[1]))

        

        # Make the loop for the forecast
        list_forecast = []

        for i in range(br[0]):
            _wor = bsw_to_wor(_bsw[i])
            
            #Get only the time array values greater or equal to zero
            filter_time = time_array[i]>=0

            #The fluid rate is multiplied by a factor to estimate the cumulative production.            
            _f = wor_forecast(
                time_array[i][filter_time],
                _fluid[i][filter_time], 
                _slope[i], 
                _wor, 
                rate_limit=rate_limit,
                cum_limit=cum_limit, 
                wor_limit=wor_limit)
            
            _f['iteration'] = i
            #_f.index = time_range[1:_f.shape[0]+1]
            _f.index = time_range[filter_time][0:_f.shape[0]]
            #_f.index = time_range[0:_f.shape[0]]
            oil_vol = np.gradient(_f['oil_cum'].values)
            oil_vol[oil_vol<0] = 0
            water_vol = np.gradient(_f['water_cum'].values)
            water_vol[water_vol<0] = 0
            _f['oil_volume'] = oil_vol
            _f['water_volume'] = water_vol
            _f['oil_cum'] += cum_i

            #Gas Rate
            if any([i is not None for i in [self.gor,self.glr]]):

                if self.gor:
                    _f['gas_cum'] = _f['oil_cum'].multiply(self.gor) 
                    _f['gas_volume'] = np.diff(_f['gas_cum'], prepend=0) #/ _f['delta_time']
                    _f['gas_rate'] = _f['gas_volume'] / _f['delta_time']
                elif self.glr:
                    _f['gas_cum'] = _f['oil_cum'].add(_f['water_cum']).multiply(self.glr) 
                    _f['gas_volume'] = np.diff(_f['gas_cum'], prepend=0) / _f['delta_time']
                    _f['gas_rate'] = _f['gas_volume'] / _f['delta_time']
            else:
                _f['gas_cum'] = 0
                _f['gas_volume'] = 0
                _f['gas_rate'] = 0

            
            list_forecast.append(_f)

        _forecast = pd.concat(list_forecast, axis=0)
        _forecast.index.name = 'date'
        
        if self.format() == 'date' and freq_output!='D':
            _forecast = _forecast.to_timestamp().to_period(freq=freq_output)
            _forecast.reset_index(inplace=True)
            _forecast = _forecast.groupby(
                ['date','iteration']
            ).agg({
                'oil_rate':'mean',
                'water_rate':'mean',
                'oil_cum':'max',
                'gas_rate':'mean',
                'water_cum':'max',
                'bsw':'mean',
                'wor':'mean',
                'wor_1':'mean',
                'delta_time':'mean',
                'fluid_rate':'mean',
                'fluid_cum' : 'max',
                'gas_cum' : 'max',
                'oil_volume':'sum',
                'water_volume':'sum',
                'gas_volume':'sum'
            }).reset_index().set_index('date')

        return _forecast