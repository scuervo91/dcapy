#External Imports
from typing import Union, Optional, List, Literal
from pydantic import BaseModel, Field, validator
from datetime import date, timedelta
import pandas as pd
import numpy as np

#Local Imports
from ..dca import Arps, Wor, FreqEnum
from .cashflow import CashFlowInput, CashFlowModel, CashFlow, ChgPts

# Put together all classes of DCA in a Union type. Pydantic uses this type to validate
# the input dca is a subclass of DCA. 
# Still I don't know if there's a way Pydantic check if a input variable is subclass of other class
#Example.  Check y Arps is subclass of DCA
union_classes_dca = Union[Arps,Wor]

freq_format={
    'M':'%Y-%m',
    'D':'%Y-%m-%d',
    'A':'%Y'
}

class Forecast(BaseModel):
	date : List[Union[date,int]]
	oil_rate : Optional[List[float]]
	oil_cum : Optional[List[float]]
	oil_volume : Optional[List[float]]
	gas_rate : Optional[List[float]]
	gas_cum : Optional[List[float]]
	gas_volume : Optional[List[float]]
	fluid_rate : Optional[List[float]]
	water_rate : Optional[List[float]]
	bsw : Optional[List[float]]
	wor : Optional[List[float]]
	water_cum : Optional[List[float]]
	fluid_cum : Optional[List[float]]
	water_cum : Optional[List[float]] 
	fluid_volume : Optional[List[float]] 
	iteration : Optional[List[int]]
	period : Optional[List[str]]
	scenario : Optional[List[str]] 
	well : Optional[List[str]] 
	freq : Literal['M','D','A'] = Field('M')
	
	def df(self):
		_forecast_dict = self.dict()
		freq = _forecast_dict.pop('freq')
		_fr = pd.DataFrame(_forecast_dict)
		_fr['date'] = pd.to_datetime(_fr['date'])
		_fr.set_index('date',inplace=True)
		_fr = _fr.to_period(freq)

		return _fr
   
  
class Period(BaseModel):
	name : str
	dca : union_classes_dca 
	start: Union[int,date]
	end: Optional[Union[int,date]]
	time_list : Optional[List[Union[int,date]]] = Field(None)
	freq_input: Literal['M','D','A'] = Field('M')
	freq_output: Literal['M','D','A'] = Field('M')
	rate_limit: Optional[float] = Field(None, ge=0)
	cum_limit: Optional[float] = Field(None, ge=0)
	cashflow_params : Optional[CashFlowInput] = Field(None)
	cashflow_out : Optional[CashFlowModel] = Field(None)
	depends: Optional[str] = Field(None)
	forecast: Optional[pd.DataFrame] = Field(None)

	@validator('end')
	def start_end_match_type(cls,v,values):
	    if type(v) != type(values['start']):
	        raise ValueError('start and end must be the same type')
	    return v

	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True

	def date_mode(self):
		if isinstance(self.start,date):
			return True
		if isinstance(self.start,int):
			return False

	def generate_forecast(self):
		_forecast = self.dca.forecast(
			time_list = self.time_list,start=self.start, end=self.end, freq_input=self.freq_input, 
			freq_output=self.freq_output, rate_limit=self.rate_limit, 
   			cum_limit=self.cum_limit
		)
		_forecast['period'] = self.name
		self.forecast = _forecast
		return _forecast

	def generate_cashflow(self):

		if self.forecast is not None and self.cashflow_params is not None:

			is_date_mode = self.date_mode()
			#Format date
			cashflow_model_dict = {'name':self.name}
			for param in self.cashflow_params.params_list:
				#initialize the individual cashflow dict

				if param.target not in cashflow_model_dict.keys():
					cashflow_model_dict[param.target] = []

				cashflow_dict = {}

				#set the name
				cashflow_dict.update({
					'name':param.name,
					'start':self.forecast.index.min().strftime('%Y-%m-%d') if is_date_mode else self.forecast.index.min(),
					'end':self.forecast.index.max().strftime('%Y-%m-%d') if is_date_mode else self.forecast.index.max(),
					'freq':self.freq_output
				})


				if param.multiply:
					#Forecast Column name to multiply the param

					#Check if the column exist in the forecast pandas dataframe
					if param.multiply in self.forecast.columns:
						multiply_col = param.multiply
					else:
						print(f'{param.multiply} is not in forecast columns. {self.forecast.columns}')
						continue


					if param.const_value:
						_const_value = self.forecast[multiply_col].multiply(param.const_value).multiply(param.wi)
						cashflow_dict.update({'const_value':_const_value.tolist()})

					if param.array_values:

						#If the array values date is a datetime.date convert to output frecuency
						#to be consistent with the freq of the forecast when multiply
						idx = pd.to_datetime(param.array_values.date).to_period(self.freq_output) if is_date_mode  else param.array_values.date
						values_series = pd.Series(param.array_values.value, index=idx)

						_array_values = self.forecast[multiply_col].multiply(values_series).multiply(param.wi).dropna()

						if _array_values.empty:
							print(f'param {param.name} array values not multiplied with forecast. There is no index match')
						else:
							cashflow_dict.update({
								'chgpts':{
									'date':_array_values.index.strftime('%Y-%m-%d').tolist(),
									'value':_array_values.tolist()
								}
							})

				else:
					cashflow_dict.update({
						'const_value':param.const_value * param.wi,
						'chgpts': ChgPts(date = param.chgpts.date, value = param.chgpts.date.param.wi)
					})


				cashflow_model_dict[param.target].append(cashflow_dict)

			#Check all keys are not empty. Otherwise delete them

			for key in cashflow_model_dict:
				if len(cashflow_model_dict[key]) == 0:
					del cashflow_model_dict[key]



			cashflow_model = CashFlowModel(**cashflow_model_dict)
			self.cashflow_out = cashflow_model

			return cashflow_model
	

class Scenario(BaseModel):
	name : str
	periods: List[Period]
	cashflow : Optional[CashFlowModel] = Field(None)
	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True

	# TODO: Make validation for all periods are in the same time basis (Integers or date)

	def generate_forecast(self, periods:list = None):

		#Make filter
		if periods:
			_periods = [i for i in self.periods if i.name in periods]
		else:
			_periods = self.periods


		list_forecast = []
		list_periods_errors = []

		for p in _periods:

			try:
				_f = p.generate_forecast()
			except Exception as e:
				print(e)
				list_periods_errors.append(p.name)
			else:
				list_forecast.append(_f)


		scenario_forecast = pd.concat(list_forecast, axis=0)
		scenario_forecast['scenario'] = self.name

		return scenario_forecast

	def generate_cashflow(self,periods:list = None):

		#Make filter
		if periods:
			_periods = [i for i in self.periods if i.name in periods]
		else:
			_periods = self.periods


		cashflow_model = CashFlowModel(name=self.name)
		list_periods_errors = []
		for p in _periods:

			try:
				_cf = p.generate_cashflow()
			except Exception as e:
				print(e)
				list_periods_errors.append(p.name)
			else:
				cashflow_model.append(_cf)

		self.cashflow = cashflow_model

		return cashflow_model

 
class Schedule(BaseModel):
	name : str
	scenarios : List[Scenario]
	cashflows : Optional[List[CashFlowModel]]
	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True 



