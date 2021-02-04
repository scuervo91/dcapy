from pydantic import BaseModel, Field
from typing import Union, List, Optional, Literal
from datetime import date
from cashflows2.timeseries import cashflow
import pandas as pd

freq_format={
    'M':'%Y-%m',
    'D':'%Y-%m-%d',
    'A':'%Y'
}


class ChgPts(BaseModel):
    time : date
    value : float

class CashFlow(BaseModel):
    name : str
    const_value : Union[float,List[float]] = Field(0)
    start : date = Field(...)
    end : Optional[date] = Field(None)
    periods : Optional[int] = Field(None)
    freq: Literal['M','D','A'] = Field('M')
    chgpts: Optional[List[ChgPts]] = Field(None)
    agg_func : Literal['sum','mean'] = Field('mean')

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        
    def cashflow(self):
        #Get the date format according the frequency specified
        fmt = freq_format[self.freq]

        if self.chgpts:
            chgpts_dicts = {}
            for cash in self.chgpts:
                chgpts_dicts.update({cash.time:cash.value})

            print(chgpts_dicts)
            chgpts_sr = pd.Series(chgpts_dicts)
            chgpts_sr.index = pd.to_datetime(chgpts_sr.index).strftime(fmt)
            chgpts_dict = chgpts_sr.groupby(level=0).agg(self.agg_func).to_dict()
        else:
            chgpts_dict = None

        print(self.dict())
        return cashflow(
            const_value = self.const_value,
            start = self.start,
            end = self.end,
            periods = self.periods,
            freq = self.freq,
            chgpts = chgpts_dict
        )
    
class CashFlowGroup(BaseModel):
    name : str 
    cashflows : List[CashFlow]
    
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        
class CashFlowModel(BaseModel):
    income : Optional[CashFlowGroup]
    opex : Optional[CashFlowGroup]
    capex : Optional[CashFlowGroup]
    
    
class CashFlowInput(BaseModel):
    oil_price : Optional[Union[float,List[ChgPts]]]
    gas_price : Optional[Union[float,List[ChgPts]]]
    capex : Optional[Union[float,List[ChgPts]]]
    fix_opex : Optional[Union[float,List[ChgPts]]]
    oil_var_opex : Optional[Union[float,List[ChgPts]]]
    gas_var_opex : Optional[Union[float,List[ChgPts]]]
    abandonment : Optional[Union[float,List[ChgPts]]]

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True