#External Imports
from typing import Union, Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import date, timedelta
import pandas as pd
import numpy as np
#Local Imports
from ..dca import Arps
from ..dca import FreqEnum
from .cashflow import CashFlowInput, CashFlowModel, CashFlow, ChgPts, CashFlowGroup

# Put together all classes of DCA in a Union type. Pydantic uses this type to validate
# the input dca is a subclass of DCA. 
# Still I don't know if there's a way Pydantic check if a input variable is subclass of other class
#Example.  Check y Arps is subclass of DCA
union_classes_dca = Union[Arps]

freq_format={
    'M':'%Y-%m',
    'D':'%Y-%m-%d',
    'A':'%Y'
}


class PeriodResult(BaseModel):
	forecast : pd.DataFrame 
	cashflow : Optional[CashFlowModel]
	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True

class Period(BaseModel):
	name : str
	dca : union_classes_dca 
	start: Union[int,date]
	end: Optional[Union[int,date]]
	freq_input: FreqEnum = Field('M')
	freq_output: FreqEnum = Field('M')
	rate_limit: Optional[float] = Field(None, ge=0)
	cum_limit: Optional[float] = Field(None, ge=0)
	#fluid_rate: Optional[Union[float,List[float]]] = Field(None)
	#bsw: Optional[Union[float,List[float]]] = Field(None)
	#wor: Optional[Union[float,List[float]]] = Field(None)
	#gor: Optional[Union[float,List[float]]] = Field(None)
	#glr: Optional[Union[float,List[float]]] = Field(None)
	cashflow_in : Optional[CashFlowInput] = Field(None)
	cashflow_out : Optional[CashFlowModel] = Field(None)
	depends: Optional[str] = Field(None)
	forecast: Optional[pd.DataFrame] = Field(None)

	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True
		title = 'PeriodSchedule'

	def generate_forecast(self):
		self.forecast = self.dca.forecast(
			start=self.start, end=self.end, freq_input=self.freq_input, 
			freq_output=self.freq_output, rate_limit=self.rate_limit, 
   			cum_limit=self.cum_limit
      	)
		return self.forecast

	def generate_cashflow(self):

		if self.forecast is not None:
			capex_sched = []
			opex_sched = []
			income_sched = []
			if self.cashflow_in:
				#Format date
				fmt = freq_format[self.freq_output]
				if self.cashflow_in.capex:
					# * cashflow2 only supports dates to define a cashflow. 
					capex_date = self.start.strftime('%Y-%m-%d')
					capex_sched.append(
	        			CashFlow(
	        				name = 'CAPEX',
	        				const_value=0,
							start = self.forecast.index.min().strftime('%Y-%m-%d'),
							end = self.forecast.index.max().strftime('%Y-%m-%d'),
							freq = self.freq_output,
							chgpts = [ChgPts(time=capex_date, value=self.cashflow_in.capex)] if isinstance(self.cashflow_in.capex,float) else  self.cashflow_in.capex
						)				
					)

				if self.cashflow_in.abandonment:
					abandonment_date = self.forecast.index[-1].strftime('%Y-%m-%d')
					capex_sched.append(
	        			CashFlow(
	        				name = 'ABANDONMENT',
	        				const_value=0,
							start = self.forecast.index.min().strftime('%Y-%m-%d'),
							end = self.forecast.index.max().strftime('%Y-%m-%d'),
							freq = self.freq_output,
							chgpts = [ChgPts(time=abandonment_date, value=self.cashflow_in.capex)] if isinstance(self.cashflow_in.abandonment,float) else  self.cashflow_in.abandonment
						)				
					)

				if self.cashflow_in.fix_opex:
					print(self.forecast.index.max().strftime('%Y-%m-%d'))
					opex_sched.append(
						CashFlow(
							name = 'FIX_OPEX',
							const_value = np.full(self.forecast.shape[0],self.cashflow_in.fix_opex).tolist() if isinstance(self.cashflow_in.fix_opex,float) else 0,
							start = self.forecast.index.min().strftime('%Y-%m-%d'),
							end = None if isinstance(self.cashflow_in.fix_opex,float) else self.forecast.index.max().strftime('%Y-%m-%d'),
							freq = self.freq_output,
							chgpts = None if isinstance(self.cashflow_in.fix_opex,float) else  self.cashflow_in.fix_opex

						)
					)

				if self.cashflow_in.oil_var_opex:
					opex_sched.append(
						CashFlow(
							name = 'OIL_VAR_OPEX',
							const_value = self.forecast['rate'].multiply(self.cashflow_in.oil_var_opex).tolist() if isinstance(self.cashflow_in.oil_var_opex,float) else 0,
							start = self.forecast.index.min().strftime('%Y-%m-%d'),
							end = None if isinstance(self.cashflow_in.oil_var_opex,float) else self.forecast.index.max().strftime('%Y-%m-%d'),
							freq = self.freq_output,
							chgpts = None if isinstance(self.cashflow_in.oil_var_opex,float) else  self.cashflow_in.oil_var_opex

						)
					)

				if self.cashflow_in.gas_var_opex:
					if 'gas_rate' in self.forecast.columns:
						opex_sched.append(
							CashFlow(
								name = 'GAS VAR_OPEX',
								const_value = self.forecast['gas_rate'].multiply(self.cashflow_in.gas_var_opex).tolist() if isinstance(self.cashflow_in.gas_var_opex,float) else 0,
								start = self.forecast.index.min().strftime('%Y-%m-%d'),
								end = None if isinstance(self.cashflow_in.gas_var_opex,float) else self.forecast.index.max().strftime('%Y-%m-%d'),
								freq = self.freq_output,
								chgpts = None if isinstance(self.cashflow_in.gas_var_opex,float) else  self.cashflow_in.gas_var_opex

							)
						)

				if self.cashflow_in.oil_price:
					income_sched.append(
						CashFlow(
							name = 'OIL_PRICE',
							const_value = self.forecast['rate'].multiply(self.oil_price).tolist() if isinstance(self.cashflow_in.oil_price,float) else 0,
							start = self.forecast.index.min().strftime('%Y-%m-%d'),
							end = None if isinstance(self.cashflow_in.oil_price,float) else self.forecast.index.max().strftime('%Y-%m-%d'),
							freq = self.freq_output,
							chgpts = None if isinstance(self.cashflow_in.oil_price,float) else  self.cashflow_in.oil_price

						)
					)

				if self.cashflow_in.gas_price:
					if 'gas_rate' in self.forecast.columns:
						income_sched.append(
							CashFlow(
								name = 'GAS_PRICE',
								const_value = self.forecast['gas_rate'].multiply(self.gas_price).tolist() if isinstance(self.cashflow_in.gas_price,float) else 0,
								start = self.forecast.index.min().strftime('%Y-%m-%d'),
								end = None if isinstance(self.cashflow_in.gas_price,float) else self.forecast.index.max().strftime('%Y-%m-%d'),
								freq = self.freq_output,
								chgpts = None if isinstance(self.cashflow_in.gas_price,float) else  self.cashflow_in.gas_price

							)
						)

			self.cashflow_out = CashFlowModel(
					capex = CashFlowGroup(name='capex',cashflows=capex_sched) if len(capex_sched)>0 else None,
					opex = CashFlowGroup(name='opex',cashflows=opex_sched) if len(opex_sched)>0 else None,
					income = CashFlowGroup(name='income',cashflows=income_sched) if len(income_sched)>0 else None
				)  
			return self.cashflow_out
	

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
