from pydantic import BaseModel, Field, validator
from typing import Union, List, Optional, Literal
from datetime import date
import pandas as pd
import numpy as np
import numpy_financial as npf

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
    periods : Optional[int] = Field(None)
    freq: Literal['M','D','A'] = Field('M')
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
        
    def get_cashflow(self, freq_output=None):
        #Get the date format according the frequency specified
        if freq_output is None:
            freq_output = self.freq

        #Create the timeSeries either with dates or integers
        if isinstance(self.const_value, list):
            periods = len(self.const_value)
        prng = pd.period_range(start=self.start, end=self.end, periods=self.periods, freq=self.freq) if isinstance(self.start,date) else np.arange(self.start, self.end,1)
        periods = len(prng)
        if not isinstance(self.const_value, list):
            const_value = [self.const_value] * periods
        time_series = pd.Series(data=self.const_value, index=prng, dtype=np.float64)

        #If the change points exists. Iterate overt the chgpts as zip to
        #assign each index to corresponding cashflow time
        if self.chgpts:

            fmt = freq_format[self.freq]

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
            time_series = time_series.to_timestamp().to_period(freq_output).groupby(level=0).agg('sum')

        return time_series


class CashFlowParams(BaseModel):
    name : str
    const_value : Optional[float]
    array_values : Optional[ChgPts]
    target : Literal['income','opex','capex']
    multiply : Optional[str]
    agg : Literal['sum','mean'] = Field('sum')
    wi : float = Field(1,ge=0,le=1)

     
class CashFlowModel(BaseModel):
    name : str
    income : Optional[List[CashFlow]]
    opex : Optional[List[CashFlow]]
    capex : Optional[List[CashFlow]]

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

    # TODO: Method to estimate de Free Cash Flow
    
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

        return fcf_df

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















    

