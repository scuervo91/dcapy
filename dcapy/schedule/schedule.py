#External Imports
from typing import Union, Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import date, timedelta

#Local Imports
from ..dca import Arps
from ..dca import FreqEnum

# Put together all classes of DCA in a Union type. Pydantic uses this type to validate
# the input dca is a subclass of DCA. 
# Still I don't know if there's a way Pydantic check if a input variable is subclass of other class
#Example.  Check y Arps is subclass of DCA
union_classes_dca = Union[Arps]

class CashFlowSchedule(BaseModel):
	oil_price : Optional[float]
	gas_price : Optional[float]
	capex : Optional[float]
	fix_opex : Optional[float]
	oil_var_opex : Optional[float]
	gas_var_opex : Optional[float]

class PeriodSchedule(BaseModel):
	name : str
	dca : union_classes_dca 
	start: Union[int,date]
	end: Union[int,date]
	freq_input: FreqEnum = Field('M')
	freq_output: FreqEnum = Field('M')
	rate_limit: Optional[float] = Field(None, ge=0)
	cum_limit: Optional[float] = Field(None, ge=0)
	fluid_rate: Optional[float] = Field(None,ge=0)
	bsw: Optional[float] = Field(None, ge=0,le=1)
	gor: Optional[float] = Field(None,ge=0)
	glr: Optional[float] = Field(None,ge=0)
	cashflow : Optional[CashFlowSchedule] = Field(None)

	class Config:
		arbitrary_types_allowed = True
		title = 'PeriodSchedule'

	def forecast(self):
		return self.dca.forecast(
			start=self.start, end=self.end, freq_input=self.freq_input, 
			freq_output=self.freq_output, rate_limit=self.rate_limit, cum_limit=self.cum_limit)


class ScenarioSchedule(BaseModel):
	periods: List[PeriodSchedule]
	class Config:
		arbitrary_types_allowed = True





    