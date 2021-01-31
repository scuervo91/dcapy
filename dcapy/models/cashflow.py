from pydantic import BaseModel, Field
from typing import Union, List, Optional
from datetime import date
from cashflows2.timeseries import cashflow

from ..dca import FreqEnum

class ChgPts(BaseModel):
    time : Union[int,date]
    value : float

class CashFlow(BaseModel):
    name : str
    const_value : Union[float,List[float]] = Field(0)
    start : date = Field(...)
    end : date = Field(...)
    period : Optional[int] = Field(None)
    freq: FreqEnum = Field('M')
    chgpts: Optional[ChgPts] = Field(None)

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        
    def cashflow(self):
        return cashflow(**self.dict())
    
class CashFlowGroup(BaseModel):
    name : str 
    cashflows : List[CashFlow]
    
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        
class CashFlowModel(BaseModel):
    income : CashFlowGroup
    opex : CashFlowGroup
    capex : CashFlowGroup
    
    
class CashFlowInput(BaseModel):
	oil_price : Optional[Union[float,List[float]]]
	gas_price : Optional[Union[float,List[float]]]
	capex : Optional[Union[float,List[float]]]
	fix_opex : Optional[Union[float,List[float]]]
	oil_var_opex : Optional[Union[float,List[float]]]
	gas_var_opex : Optional[Union[float,List[float]]]
    abandonment : Optional[Union[float,List[float]]]

    class Config:
        validate_assignment = True