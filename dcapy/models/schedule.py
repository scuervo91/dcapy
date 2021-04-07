#External Imports
from typing import Union, Optional, List, Literal, Dict
from pydantic import BaseModel, Field, validator
from datetime import date, timedelta
import pandas as pd
import numpy as np

#Local Imports
from ..dca import Arps, Wor, FreqEnum, Forecast, converter_factor
from .cashflow import CashFlowModel, CashFlow, CashFlowParams, ChgPts

# Put together all classes of DCA in a Union type. Pydantic uses this type to validate
# the input dca is a subclass of DCA. 
# Still I don't know if there's a way Pydantic check if a input variable is subclass of other class
#Example.  Check y Arps is subclass of DCA
union_classes_dca = Union[Wor,Arps]

freq_format={
    'M':'%Y-%m',
    'D':'%Y-%m-%d',
    'A':'%Y'
}

class Depends(BaseModel):
    period : str = Field(...)
    delay : Union[timedelta,int] = Field(None)
  
class Period(BaseModel):
	name : str
	dca : union_classes_dca 
	start: Union[int,date]
	end: Optional[Union[int,date]]
	time_list : Optional[List[Union[int,date]]] = Field(None)
	freq_input: Literal['M','D','A'] = Field('D')
	freq_output: Literal['M','D','A'] = Field('D')
	rate_limit: Optional[float] = Field(None, ge=0)
	cum_limit: Optional[float] = Field(None, ge=0)
	iter : int = Field(1, ge=1)
	ppf : Optional[float] = Field(None, ge=0, le=1)
	cashflow_params : Optional[List[CashFlowParams]] = Field(None)
	cashflow : Optional[List[CashFlowModel]] = Field(None)
	depends: Optional[Depends] = Field(None)
	forecast: Optional[Forecast] = Field(None)

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

	def generate_forecast(self, freq_output=None, iter=None):
		#If freq_output is not defined in the method. 
  		# Use the freq_out defined in the class
		if freq_output is None:
			freq_output = self.freq_output

		#If freq_output is not defined in the method. 
  		# Use the freq_out defined in the class
		if iter is None:
			iter = self.iter
   
		_forecast = self.dca.forecast(
			time_list = self.time_list,start=self.start, end=self.end, freq_input=self.freq_input, 
			freq_output=freq_output, rate_limit=self.rate_limit, 
   			cum_limit=self.cum_limit, iter=iter, ppf=self.ppf
		)
		_forecast['period'] = self.name
		
		if self.dca.format()=='number':

			self.forecast = Forecast(freq=freq_output,**_forecast.reset_index().to_dict(orient='list'))
		else:

			self.forecast = Forecast(freq=freq_output,**_forecast.to_timestamp().reset_index().to_dict(orient='list'))
		return _forecast

	def get_end_dates(self):
		if self.forecast:
			_df = self.forecast.df().reset_index()
			dates_sr = _df.groupby('iteration')['date'].max()
			if self.dca.format()=='date':
				return [i.to_timestamp().date() for i in dates_sr]
			else:	
				return [i for i in dates_sr]
		raise ValueError('There is no any Forecast')

	def generate_cashflow(self, freq_output=None):
		if freq_output is None:
			freq_output = self.freq_output
   
		if self.forecast is not None and self.cashflow_params is not None:

			_forecast = self.forecast.df()

			is_date_mode = self.date_mode()
			#Format date

			list_cashflow_model = []

			#Iterate over list of cases
			for i in _forecast['iteration'].unique():

				_forecast_i = _forecast[_forecast['iteration']==i]

				cashflow_model_dict = {'name':self.name + '_' + str(i)}
				for param in self.cashflow_params:
					#initialize the individual cashflow dict

					if param.target not in cashflow_model_dict.keys():
						cashflow_model_dict[param.target] = []

					cashflow_dict = {}

					#set the name
					cashflow_dict.update({
						'name':param.name,
						'start':_forecast_i.index.min().strftime('%Y-%m-%d') if is_date_mode else _forecast_i.index.min(),
						'end':_forecast_i.index.max().strftime('%Y-%m-%d') if is_date_mode else _forecast_i.index.max(),
						'freq_output':freq_output,'freq_input':self.freq_input
					})


					if param.multiply:
						#Forecast Column name to multiply the param

						#Check if the column exist in the forecast pandas dataframe
						if param.multiply in _forecast_i.columns:
							multiply_col = param.multiply
						else:
							print(f'{param.multiply} is not in forecast columns. {_forecast_i.columns}')
							continue


						if param.const_value:
							_const_value = _forecast_i[multiply_col].multiply(param.const_value).multiply(param.wi)
							cashflow_dict.update({'const_value':_const_value.tolist()})

						if param.array_values:

							#If the array values date is a datetime.date convert to output frecuency
							#to be consistent with the freq of the forecast when multiply
							idx = pd.to_datetime(param.array_values.date).to_period(freq_output) if is_date_mode  else param.array_values.date
							values_series = pd.Series(param.array_values.value, index=idx)

							_array_values = _forecast_i[multiply_col].multiply(values_series).multiply(param.wi).dropna()

							if _array_values.empty:
								print(f'param {param.name} array values not multiplied with forecast. There is no index match')
							else:
								cashflow_dict.update({
									'chgpts':{
										'date':_array_values.index.strftime('%Y-%m-%d').tolist() if is_date_mode else _array_values.index,
										'value':_array_values.tolist()
									}
								})

					else:
						if param.const_value:
							cashflow_dict.update({
								'const_value':param.const_value * param.wi,
								'periods':param.periods
							})
						if param.array_values:
							cashflow_dict.update({
								'chgpts': ChgPts(date = param.array_values.date, value = param.array_values.value*param.wi)
							})


					cashflow_model_dict[param.target].append(cashflow_dict)

				#Check all keys are not empty. Otherwise delete them

				for key in cashflow_model_dict:
					if len(cashflow_model_dict[key]) == 0:
						del cashflow_model_dict[key]
				
				cashflow_model = CashFlowModel(**cashflow_model_dict)
				list_cashflow_model.append(cashflow_model)

			self.cashflow = list_cashflow_model

			return list_cashflow_model
		else:
			raise ValueError('Either Forecast or Cashflow Params not defined')

	def npv(self,rates, freq:str='A'):
     
		if self.cashflow is not None:
			npv_list = []
			rates = np.atleast_1d(rates)

			#Convert the Frequency of the rates to the cashflow frequency
			#Example: If the Cashflow is given in monthly basis and the discount
			#rates was given in Annual basis, then convert the discount rates
			#to montly by applying: (1+rate)^(0.0833) - 1
			c = converter_factor(freq,self.freq_output)
			rates = np.power(1 + rates,c) - 1
			
			for i,v in enumerate(self.cashflow):
				npv_i = v.npv(rates,freq_output=self.freq_output)
				npv_i['iteration'] = i
				npv_list.append(npv_i)

			return pd.concat(npv_list,axis=0)

		else:
			raise ValueError('Cashflow has not been defined')
  
	def irr(self, freq_output:str='A'):
		irr_list = []
		for i,v in enumerate(self.cashflow):
			irr_i = v.irr(freq_output=freq_output)
			irr_list.append(irr_i)


		return pd.DataFrame({'irr':irr_list})
     
class Scenario(BaseModel):
	name : str
	periods: Dict[str,Period]
	cashflow_params : Optional[List[CashFlowParams]] = Field(None)
	cashflow : Optional[List[CashFlowModel]] = Field(None)
	forecast: Optional[Forecast] = Field(None)
	freq_output: str = Field('D')
 
	@validator('periods', always=True)
	def match_periods_freqs(cls,v):
		format_list = []
		for i in v:
			format_list.append(v[i].dca.format())

		freq_list = []
		for i in v:
			freq_list.append(v[i].freq_output)

		if all(i==format_list[0] for i in format_list)&all(i==freq_list[0] for i in freq_list):
			return v 
		raise ValueError(f'The format of the periods are different {format_list}')
	
	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True

	# TODO: Make validation for all periods are in the same time basis (Integers or date)

	def generate_forecast(self, periods:list = None, freq_output=None, iter=None):
		if freq_output is None:
			freq_output = self.freq_output
		
		#Make filter
		if periods:
			_periods = [i for i in self.periods if i in periods]
		else:
			_periods = list(self.periods.keys())


		list_forecast = []
		list_periods_errors = []

		for p in _periods:
			if self.periods[p].depends:
				#Get the last dates of the forecast present period depends on
				depend_period = self.periods[p].depends.period
				new_ti = self.periods[depend_period].get_end_dates()
    
				# If delay is set. add the time delta
				if self.periods[p].depends.delay:
					new_ti = [i + self.periods[p].depends.delay for i in new_ti]

				self.periods[p].dca.ti = new_ti
			_f = self.periods[p].generate_forecast(freq_output=freq_output, iter=iter)
			
			#try:
			#	_f = self.periods[p].generate_forecast()
			#except Exception as e:
			#	print(e)
			#	listself.periods_errors.append(self.periods[p].name)
			#else:
			list_forecast.append(_f)


		scenario_forecast = pd.concat(list_forecast, axis=0)
		scenario_forecast['scenario'] = self.name

		if isinstance(scenario_forecast.index[0],pd.Period):
			self.forecast = Forecast(freq=freq_output,**scenario_forecast.to_timestamp().reset_index().to_dict(orient='list'))
		else:
			self.forecast = Forecast(freq=freq_output,**scenario_forecast.reset_index().to_dict(orient='list'))

		return scenario_forecast

	def _iterations(self,periods:list = None):
		#Make filter
		if periods:
			_periods = [i for i in self.periods if i in periods]
		else:
			_periods = list(self.periods.keys())

		n = []
		for i in _periods:
			n.append(np.array(self.periods[i].forecast.iteration).max())

		return np.array(n).max() + 1


	def generate_cashflow(self,periods:list = None, freq_output=None):
		if freq_output is None:
			freq_output = self.freq_output
		#Make filter
		if periods:
			_periods = [i for i in self.periods if i in periods]
		else:
			_periods = list(self.periods.keys())

		n = self._iterations(periods = periods)
		#print(n)

		cashflow_models = [CashFlowModel(name=f'{self.name}_{i}') for i in range(n)]
		list_periods_errors = []
		for p in _periods:
			if self.periods[p].cashflow_params is None:
				if self.cashflow_params:
					self.periods[p].cashflow_params = self.cashflow_params
				else:
					continue

			try:
				_cf = self.periods[p].generate_cashflow(freq_output=freq_output)
			except Exception as e:
				print(e)
				list_periods_errors.append(self.periods[p].name)
			else:
				if len(_cf)==1:
					_cf = [_cf[0] for i in range(n)]

				for i in range(n):
					cashflow_models[i].append(_cf[i])

		self.cashflow = cashflow_models

		return cashflow_models

	def npv(self,rates, freq='A'):
     
		if self.cashflow is not None:
			npv_list = []
			rates = np.atleast_1d(rates)

			#Convert the Frequency of the rates to the cashflow frequency
			#Example: If the Cashflow is given in monthly basis and the discount
			#rates was given in Annual basis, then convert the discount rates
			#to montly by applying: (1+rate)^(0.0833) - 1
			c = converter_factor(freq,self.freq_output)
			rates = np.power(1 + rates,c) - 1
			
			for i,v in enumerate(self.cashflow):
				npv_i = v.npv(rates,freq_output=self.freq_output)
				npv_i['iteration'] = i
				npv_list.append(npv_i)

			return pd.concat(npv_list,axis=0)

		else:
			raise ValueError('Cashflow has not been defined')

	def irr(self, freq_output:str='A'):
		irr_list = []
		for i,v in enumerate(self.cashflow):
			irr_i = v.irr(freq_output=freq_output)
			irr_list.append(irr_i)


		return pd.DataFrame({'irr':irr_list})


class Well(BaseModel):
	name : str 
	scenarios : Dict[str,Scenario]
	cashflow_params : Optional[List[CashFlowParams]] = Field(None)
	cashflow : Optional[Dict[str,List[CashFlowModel]]] = Field(None)
	forecast: Optional[Forecast] = Field(None)
 
	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True
 
	def generate_forecast(self, scenarios:Union[list,dict] = None, freq_output=None, iter=None):
		#Make filter
		if scenarios:
			scenarios_list = scenarios if isinstance(scenarios,list) else list(scenarios.keys())
			_scenarios = [i for i in self.scenarios if i in scenarios_list]
		else:
			_scenarios = list(self.scenarios.keys())
   
		list_forecast = []
  
		for s in _scenarios:
			periods = scenarios[s] if isinstance(scenarios,dict) else None
			_f = self.scenarios[s].generate_forecast(periods = periods, freq_output=freq_output, iter=iter)

			list_forecast.append(_f)
   
		well_forecast = pd.concat(list_forecast, axis=0)
		well_forecast['well'] = self.name
		if isinstance(well_forecast.index[0],pd.Period):
			self.forecast = Forecast(freq=freq_output,**well_forecast.to_timestamp().reset_index().to_dict(orient='list'))
		else:
			self.forecast = Forecast(freq=freq_output,**well_forecast.reset_index().to_dict(orient='list'))

		return well_forecast

	def generate_cashflow(self, scenarios:Union[list,dict] = None, freq_output=None):
		if scenarios:
			scenarios_list = scenarios if isinstance(scenarios,list) else list(scenarios.keys())
			_scenarios = [i for i in self.scenarios if i in scenarios_list]
		else:
			_scenarios = list(self.scenarios.keys())
   
		dict_cashflows = {}

		for s in _scenarios:
			if self.scenarios[s].cashflow_params is None:
				if self.cashflow_params:
					self.scenarios[s].cashflow_params = self.cashflow_params
				else:
					continue
 
			periods = scenarios[s] if isinstance(scenarios,dict) else None
			cash_s = self.scenarios[s].generate_cashflow(periods=periods, freq_output=freq_output)

			dict_cashflows.update({s:cash_s})
   
		self.cashflow = dict_cashflows 

		return dict_cashflows
   
class WellsGroup(BaseModel):
	name : str 
	wells : Dict[str,Well]
	cashflow_params : Optional[List[CashFlowParams]] = Field(None)
	cashflow : Optional[Dict[str,Dict[str,List[CashFlowModel]]]] = Field(None)
	forecast: Optional[Forecast] = Field(None)

	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True
  
	def generate_forecast(self, wells:Union[list,dict] = None, freq_output=None, iter=None):
		#Make filter
		if wells:
			wells_list = wells if isinstance(wells,list) else list(wells.keys())
			_wells = [i for i in self.wells if i in wells_list]
		else:
			_wells = self.wells
   
		list_forecast = []
  
		for w in _wells:
			scenarios = wells[w] if isinstance(wells,dict) else None
			_f = self.wells[w].generate_forecast(scenarios = scenarios, freq_output=freq_output, iter=iter)

			list_forecast.append(_f)
   
		wells_forecast = pd.concat(list_forecast, axis=0)
		if isinstance(wells_forecast.index[0],pd.Period):
			self.forecast = Forecast(freq=freq_output,**wells_forecast.to_timestamp().reset_index().to_dict(orient='list'))
		else:
			self.forecast = Forecast(freq=freq_output,**wells_forecast.reset_index().to_dict(orient='list'))

		return wells_forecast

	def generate_cashflow(self, wells:Union[list,dict] = None, freq_output=None):
		if wells:
			wells_list = wells if isinstance(wells,list) else list(wells.keys())
			_wells = [i for i in self.wells if i in wells_list]
		else:
			_wells = list(self.wells.keys())
   
		dict_cashflows = {}

		for w in _wells:
			if self.wells[w].cashflow_params is None:
				if self.cashflow_params:
					self.wells[w].cashflow_params = self.cashflow_params
				else:
					continue
 
			scenarios = wells[w] if isinstance(wells,dict) else None
			cash_s = self.wells[w].generate_cashflow(scenarios=scenarios, freq_output=freq_output)

			dict_cashflows.update({w:cash_s})
   
		self.cashflow = dict_cashflows 

		return dict_cashflows

def model_from_dict(d:dict):
    
    instance = d.pop('instance')
    
    if instance == 'period':
        return Period(**d)
    if instance == 'scenario':
        return Scenario(**d)
    if instance == 'well':
        return Well(**d)
    if instance == 'wells-group':
        return WellsGroup(**d)