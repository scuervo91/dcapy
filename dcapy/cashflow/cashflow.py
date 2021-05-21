from dcapy.dca.dca import ProbVar
from pydantic import BaseModel, Field, validator
from typing import Union, List, Optional
from datetime import date
import pandas as pd
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt 
import seaborn as sns
from enum import Enum
from ..dca import converter_factor
from ..wiener import Brownian, MeanReversion, GeometricBrownian
from ..dca import FreqEnum

freq_format={
    'M':'%Y-%m',
    'D':'%Y-%m-%d',
    'A':'%Y'
}

## Input clasess

class ChgPts(BaseModel):
    date : List[Union[int,date]]
    value : List[float]

    @validator('value')
    def lenght_match(cls,v,values):
        if len(v) != len(values['date']):
            raise ValueError('list must be with the same length')
        return v

class CashFlow(BaseModel):
    name : str
    const_value : Union[float,List[float]] = Field(0)
    start : Union[int,date] = Field(...)
    end : Union[int,date] = Field(...)
    periods : Optional[int] = Field(None, ge=-1)
    freq_output: FreqEnum = Field(None)
    freq_input: FreqEnum = Field('M')
    chgpts: Optional[ChgPts] = Field(None)

    @validator('end')
    def start_end_match_type(cls,v,values):
        if type(v) != type(values['start']):
            raise ValueError('start and end must be the same type')
        return v

    @validator('chgpts')
    def chgpts_type_start(cls,v,values):
        if v is not None:
            if type(v.date[0]) != type(values['start']):
                raise ValueError('chgpts.date must be the same type of start')
        return v

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        
    def get_cashflow(self,freq_output=None, agg='sum'):
        #Get the date format according the frequency specified
        if freq_output is None:
            if self.freq_output is None:
                freq_output = self.freq_input
            else:
                freq_output = self.freq_output
        c = converter_factor(self.freq_input,freq_output)
        #Create the timeSeries either with dates or integers
        if isinstance(self.const_value, list):
            periods = len(self.const_value)
        if self.periods:
            if self.periods < 0: # When the cashflow is at the end when abandoning a well
                prng = pd.period_range(start=self.end, periods=abs(self.periods), freq=self.freq_input) if isinstance(self.start,date) else np.arange(self.start, self.end+1,c)
            else:   
                prng = pd.period_range(start=self.start, periods=self.periods, freq=self.freq_input) if isinstance(self.start,date) else np.arange(self.start, self.end+1,c)
        else:
            prng = pd.period_range(start=self.start, end=self.end, periods=self.periods, freq=self.freq_input) if isinstance(self.start,date) else np.arange(self.start, self.end+1,c)
        periods = len(prng)
        if not isinstance(self.const_value, list):
            const_value = [self.const_value] * periods
        time_series = pd.Series(data=self.const_value, index=prng, dtype=np.float64)

        #If the change points exists. Iterate overt the chgpts as zip to
        #assign each index to corresponding cashflow time
        if self.chgpts:

            fmt = freq_format[freq_output]

            for i in zip(self.chgpts.date,self.chgpts.value):
                idx = i[0].strftime(fmt) if isinstance(i[0],date) else i[0]
                k = i[1]

                if idx in time_series.index:
                    time_series[idx] = k

        #If the cashflow is in dates. There is the posibility to change the frequency of the output
        #cashflow. For ejample, if the CashFlow is initiated in months, you can specify the 
        #output frequency to Annual, then a groupby-sum operation will be performed to get 
        #the desired period of time
        if isinstance(self.start,date):
            time_series = time_series.to_timestamp().to_period(freq_output).groupby(level=0).agg(agg)

        return time_series
    
    def irr(self,freq_output=None):

        csh = self.get_cashflow(freq_output=freq_output)

        irr = npf.irr(csh.values)

        return irr

    def npv(self, rates, freq_output=None):

        rates = np.atleast_1d(rates)
        csh = self.get_cashflow(freq_output=freq_output)

        npv_list = []
        for i in rates:
            npv_i = npf.npv(i,csh.values)
            npv_list.append(npv_i)
        return pd.DataFrame({'npv':npv_list}, index=rates)

class TargetEnum(str, Enum):
    income = 'income'
    opex = 'opex'
    capex = 'capex'
    
class AggEnum(str, Enum):
    sum = 'sum'
    mean = 'mean'


class CashFlowParams(BaseModel):
    name : str = Field(...)
    wi : Union[ProbVar,List[float],float,List[ChgPts],ChgPts,Brownian,MeanReversion,GeometricBrownian] = Field(1.)
    periods : Optional[int] = Field(None, ge=-1)
    value : Union[ProbVar,List[float],float,List[ChgPts],ChgPts,Brownian,MeanReversion,GeometricBrownian] = Field(...)
    target : TargetEnum = Field(...)
    multiply : Optional[str] = Field(None)
    agg : AggEnum = Field('mean')
    depends: bool = Field(False)
    iter: int = Field(1,ge=1) 
    general: bool = Field(False)
    freq_value: FreqEnum = Field(None)

    @validator('iter', always=True)
    def check_list_length(cls,v,values):
        check_names = ['value','wi']
        for i in check_names:
            if isinstance(values[i], list):
                v = len(values[i])
                #assert len(values[i]) == v
        return v
    
    def get_value(self,i:int, seed:int=None, freq_output:str=None, ppf:float=None, interval:float=None):
        if isinstance(self.value,(ChgPts,float)):
            return self.value 
        if isinstance(self.value,list):
            return self.value[i]
        if isinstance(self.value,ProbVar):
            return self.value.get_sample(size=1, seed=seed, ppf=ppf)
        if isinstance(self.value,(Brownian,MeanReversion,GeometricBrownian)):
            df = self.value.generate(processes=i+1,freq_output=freq_output,interval=interval,seed=seed)
            idx = [i.to_timestamp().strftime('%Y-%m-%d') for i in df.index]
            return ChgPts(date=idx, value=df.iloc[:,i].values.tolist())

    def get_wi(self,i:int, seed:int=None, freq_output:str=None, interval:float=None, ppf=None):
        if isinstance(self.wi,(ChgPts,float)):
            return self.wi 
        if isinstance(self.wi,list):
            return self.wi[i]
        if isinstance(self.wi,ProbVar):
            return self.wi.get_sample(size=1, seed=seed, ppf=ppf)
        if isinstance(self.wi,(Brownian,MeanReversion,GeometricBrownian)):
            df = self.wi.generate(processes=i+1,freq_output=freq_output,interval=interval,seed=seed)
            idx = [i.to_timestamp().strftime('%Y-%m-%d') for i in df.index]
            return ChgPts(date=idx, value=df.iloc[:,i].values.tolist())
        

class CashFlowModel(BaseModel):
    name : str
    income : Optional[List[CashFlow]]
    opex : Optional[List[CashFlow]]
    capex : Optional[List[CashFlow]]

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

    
    def append(self, cashflow_model):

        if cashflow_model.income:
            if self.income:
                self.income.extend(cashflow_model.income)
            else:
                self.income = cashflow_model.income 

        if cashflow_model.opex:
            if self.opex:
                self.opex.extend(cashflow_model.opex)
            else:
                self.opex = cashflow_model.opex

        if cashflow_model.capex:
            if self.capex:
                self.capex.extend(cashflow_model.capex)
            else:
                self.capex = cashflow_model.capex

    def fcf(self, freq_output=None):
        list_df = []
        if self.income:
            list_income = []
            for i in self.income:
                income_cash = i.get_cashflow(freq_output=freq_output)
                income_cash.name = i.name
                list_income.append(income_cash)

            income_df = pd.concat(list_income, axis=1).fillna(0)
            income_df['total_income'] = income_df.sum(axis=1)
            list_df.append(income_df)

        if self.opex:
            list_opex = []
            for i in self.opex:
                opex_cash = i.get_cashflow(freq_output=freq_output)
                opex_cash.name = i.name
                list_opex.append(opex_cash)

            opex_df = pd.concat(list_opex, axis=1).fillna(0)
            opex_df['total_opex'] = opex_df.sum(axis=1)
            list_df.append(opex_df)

        if self.capex:
            list_capex = []
            for i in self.capex:
                capex_cash = i.get_cashflow(freq_output=freq_output)
                capex_cash.name = i.name
                list_capex.append(capex_cash)

            capex_df = pd.concat(list_capex, axis=1).fillna(0)
            capex_df['total_capex'] = capex_df.sum(axis=1)
            list_df.append(capex_df)


        fcf_df = pd.concat(list_df, axis=1)

        for i in ['total_income','total_opex','total_capex']:
            if i not in fcf_df.columns:
                fcf_df[i] = 0

        fcf_df['fcf'] = fcf_df[['total_income','total_opex','total_capex']].sum(axis=1)

        fcf_df['cum_fcf'] = fcf_df['fcf'].cumsum()

        return fcf_df.fillna(0)
    
    def get_cashflows(self, freq_output=None):
        list_df = []
        if self.income:
            list_income = []
            for i in self.income:
                income_cash = i.get_cashflow(freq_output=freq_output)
                income_cash.name = 'value'
                income_cashdf = pd.DataFrame(income_cash)
                income_cashdf['desc'] = i.name
                income_cashdf['cash'] = 'income'
                list_income.append(income_cashdf)

            income_df = pd.concat(list_income, axis=0)
            #income_df['total_income'] = income_df.sum(axis=1)
            list_df.append(income_df)

        if self.opex:
            list_opex = []
            for i in self.opex:
                opex_cash = i.get_cashflow(freq_output=freq_output)
                opex_cash.name = 'value'
                opex_cashdf = pd.DataFrame(opex_cash)
                opex_cashdf['desc'] = i.name
                opex_cashdf['cash'] = 'opex'
                list_opex.append(opex_cashdf)

            opex_df = pd.concat(list_opex, axis=0)
            #opex_df['total_opex'] = opex_df.sum(axis=1)
            list_df.append(opex_df)

        if self.capex:
            list_capex = []
            for i in self.capex:
                capex_cash = i.get_cashflow(freq_output=freq_output)
                capex_cash.name = 'value'
                capex_cashdf = pd.DataFrame(capex_cash)
                capex_cashdf['desc'] = i.name
                capex_cashdf['cash'] = 'capex'
                list_capex.append(capex_cashdf)

            capex_df = pd.concat(list_capex, axis=0)
            #capex_df['total_capex'] = capex_df.sum(axis=1)
            list_df.append(capex_df)


        fcf_df = pd.concat(list_df, axis=0)

        return fcf_df.fillna(0)
    
    def get_cashflow_period(self, freq_output=None):
        cashflows = self.get_cashflows(freq_output=freq_output).reset_index()
        cashflows['index'] = cashflows['index'].astype('str')

        gr_cash = cashflows.groupby(['index','cash']).sum().reset_index()
        gr_fcf = pd.DataFrame(cashflows.groupby(['index'])['value'].sum().reset_index())
        gr_fcf['cash'] = 'fcf'
        
        return pd.concat([gr_cash,gr_fcf],axis=0)
    
    def plot(self, freq_output=None, ax=None, cum=False,bar_kw={}, format='k',fmt='${:,.1f}'):

        def_bar_kw = {
        'palette': {
            'income':'green',
            'opex':'orange',
            'capex':'red',
            'fcf':'gray'
        }
        }    
        for (k,v) in def_bar_kw.items():
            if k not in bar_kw:
                bar_kw[k]=v
                
        format_dict = {
            'k':{
                'factor':1e3,
                'title':'Thousands'
            },
            'm':{
                'factor':1e6,
                'title':'Millions'
            }
        }

        cashflows = self.get_cashflow_period(freq_output=freq_output)
        
        #Create the Axex
        grax= ax or plt.gca()
        sns.barplot(data=cashflows, x='index', y='value', hue='cash',ax=grax,**bar_kw)

        ticks = grax.get_yticks() 
        grax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks])
        grax.set_ylabel(f"Cashflows [{format_dict[format]['title']}]")
        
        if cum:
            spax=grax.twinx()
            gr_cum = cashflows.loc[cashflows['cash']=='fcf','value'].cumsum() #gr_fcf['value'].cumsum()
            sns.lineplot(data=gr_cum,ax=spax)
            ticks_cum = spax.get_yticks() 
            spax.set_yticklabels([fmt.format(i/format_dict[format]['factor']) for i in ticks_cum])
            spax.set_ylabel(f"Cumulative Cashflows [{format_dict[format]['title']}]")

    def irr(self,freq_output=None):

        fcf = self.fcf(freq_output=freq_output)

        irr = npf.irr(fcf['fcf'].values)

        return irr

    def npv(self, rates, freq_output=None):

        rates = np.atleast_1d(rates)
        fcf = self.fcf(freq_output=freq_output)

        npv_list = []
        for i in rates:
            npv_i = npf.npv(i,fcf['fcf'].values)
            npv_list.append(npv_i)
        return pd.DataFrame({'npv':npv_list}, index=rates)


def npv_cashflows(list_cashflows:list,rates, freq_rate:str,freq_cashflow:str):
    
    npv_list = []
    rates = np.atleast_1d(rates)

    #Convert the Frequency of the rates to the cashflow frequency
    #Example: If the Cashflow is given in monthly basis and the discount
    #rates was given in Annual basis, then convert the discount rates
    #to montly by applying: (1+rate)^(0.0833) - 1
    c = converter_factor(freq_rate,freq_cashflow)
    rates = np.power(1 + rates,c) - 1

    for i,v in enumerate(list_cashflows):
        npv_i = v.npv(rates,freq_output=freq_cashflow)
        npv_i['iteration'] = i
        npv_list.append(npv_i)

    return pd.concat(npv_list,axis=0)

def irr_cashflows(list_cashflows, freq_output):
		irr_list = []
		for i,v in enumerate(list_cashflows):
			irr_i = v.irr(freq_output=freq_output)
			irr_list.append(irr_i)


		return pd.DataFrame({'irr':irr_list})
    











    

