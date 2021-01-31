#External Imports
from typing import Union, Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import date, timedelta
import pandas as pd

#Local Imports
from ..dca import Arps
from ..dca import FreqEnum
from .cashflow import CashFlowInput, CashFlowModel

# Put together all classes of DCA in a Union type. Pydantic uses this type to validate
# the input dca is a subclass of DCA. 
# Still I don't know if there's a way Pydantic check if a input variable is subclass of other class
#Example.  Check y Arps is subclass of DCA
union_classes_dca = Union[Arps]


class PeriodResult(BaseModel):
	forecast : pd.DataFrame 
	cashflow : CashFlowModel
	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True

class Period(BaseModel):
	name : str
	dca : union_classes_dca 
	start: Union[int,date]
	end: Union[int,date]
	freq_input: FreqEnum = Field('M')
	freq_output: FreqEnum = Field('M')
	rate_limit: Optional[float] = Field(None, ge=0)
	cum_limit: Optional[float] = Field(None, ge=0)
	fluid_rate: Optional[Union[float,List[float]]] = Field(None)
	bsw: Optional[Union[float,List[float]]] = Field(None)
	wor: Optional[Union[float,List[float]]] = Field(None)
	gor: Optional[Union[float,List[float]]] = Field(None)
	glr: Optional[Union[float,List[float]]] = Field(None)
	cashflow : Optional[CashFlowInput] = Field(None)
	depends: Optional[str] = Field(None)

	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True
		title = 'PeriodSchedule'

	def forecast(self):
		_forecast = self.dca.forecast(
			start=self.start, end=self.end, freq_input=self.freq_input, 
			freq_output=self.freq_output, rate_limit=self.rate_limit, cum_limit=self.cum_limit)


  

class Scenario(BaseModel):
	name : str
	periods: List[Period]
	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True
  
 
class Schedule(BaseModel):
	name : str
	schedules : List[Scenario]
	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True
