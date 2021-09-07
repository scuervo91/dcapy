#External Imports
from typing import Union, Optional, List, Dict
from pydantic import BaseModel, Field, validator
from datetime import date, timedelta
import pandas as pd
import numpy as np
import pyDOE2 as ed
import yaml
import json
from rich.tree import Tree
from rich.panel import Panel
from rich.layout import Layout
from rich.columns import Columns
import requests
from enum import Enum
#Local Imports
from ..dca import Arps, Wor, FreqEnum, Forecast, converter_factor
from ..cashflow import CashFlowModel, CashFlow, CashFlowParams, ChgPts, npv_cashflows, irr_cashflows
from ..console import console
from ..auth import Credential
import traceback
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

class SchemasEnum(str, Enum):
    period = 'period'
    scenario = 'scenario'
    well = 'well'
    wellsgroup = 'wellsgroup'


class Depends(BaseModel):
    period : str = Field(...)
    delay : Union[timedelta,int] = Field(None)
  
    
class ScheduleBase(BaseModel):
	name:str = Field(None)
	cashflow_params : Optional[List[CashFlowParams]] = Field(None)
	cashflow : Optional[List[CashFlowModel]] = Field(None)
	forecast: Optional[Forecast] = Field(None)
	seed: Optional[int] = Field(None)
	iter : int = Field(1, ge=1)
	ppf : Optional[float] = Field(None, ge=0, le=1)
	description: str = Field(None)
	id: str = Field(None)
 
	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True
  
	def npv(self,rates, freq_rate='A',freq_cashflow='M'):
     
		if self.cashflow is not None:
			return npv_cashflows(self.cashflow, rates,freq_rate,freq_cashflow)

		else:
			raise ValueError('Cashflow has not been defined')
  
	def irr(self, freq_output:str=None):
		return irr_cashflows(self.cashflow, freq_output)

	def to_file(self, file:str, format='yaml'):
		with open(f'{file}.{format}','w') as f:
			if format=='yaml':
				yaml.safe_dump(json.loads(self.json(exclude_none=True)), f)
			if format=='json':
				f.write(self.json(exclude_none=True))
    
	#def tree(self):
	#	node_tree = Tree(self.name)
	def get_db(self,key:str, cred:Credential):
		end_point = f'api/v1/models/{self.type.value}/'
		headers = {
			'accept': 'application/json',
			'Authorization': f'Bearer {cred.token}'
		}	
		try:
			r = requests.get(f'{cred.url}{end_point}{key}', headers=headers)
			r.raise_for_status()
			data = json.loads(r.text)
			dict_data = data['case']
			for i in dict_data:
				setattr(self,i,dict_data[i]) 
		except requests.exceptions.HTTPError as err:
			print(err)
		else:
			self.id = key 
  
	def insert_db(self,cred:Credential, description:str=None):
		end_point = f'api/v1/models/{self.type.value}'
		headers = {
			'accept': 'application/json',
			'Authorization': f'Bearer {cred.token}',
			'Content-Type':'application/json'
		}
		model = json.loads(self.json(exclude_unset=True))
		data = {'model':model}
		if description:
			data['description'] = description
		try:
			r = requests.post(f'{cred.url}{end_point}', headers=headers, json=data)
			r.raise_for_status()
			data = json.loads(r.text)
			
		except requests.exceptions.HTTPError as err:
			print(err)
		else:
			self.id = data['id']
			return data['id']

	def update_db(self, cred:Credential, description:str=None):
		if self.id is None:
			raise ValueError('Model has no Key')
		end_point = f'api/v1/models/{self.type.value}/'
		headers = {
			'accept': 'application/json',
			'Authorization': f'Bearer {cred.token}'
		}
		model = json.loads(self.json(exclude_unset=True))
		data = {'model':model}
		if description:
			data['description'] = description
		try:
			r = requests.put(f'{cred.url}{end_point}{self.id}', headers=headers, json=data)
			r.raise_for_status()
			data = json.loads(r.text)
		except requests.exceptions.HTTPError as err:
			print(err)
		else:
			return data['id']
			
   
	def delete_db(self, cred:Credential, description:str=None):
		if self.id is None:
			raise ValueError('Model has no Key')
		end_point = f'api/v1/models{self.type.value}/'
		headers = {
			'accept': 'application/json',
			'Authorization': f'Bearer {cred.token}'
		}
		model = json.loads(self.json(exclude_unset=True))
		data = {'model':model}
		if description:
			data['description'] = description
		try:
			r = requests.delete(f'{cred.url}{end_point}{self.id}', headers=headers, json=data)
			r.raise_for_status()
			data = json.loads(r.text)
		except requests.exceptions.HTTPError as err:
			print(err)
		else:
			return data['id']
  
class Period(ScheduleBase):
	dca : union_classes_dca = Field(None)
	start: Union[int,date] = Field(None)
	end: Optional[Union[int,date]] = Field(None)
	time_list : Optional[List[Union[int,date]]] = Field(None)
	freq_input: FreqEnum = Field('D')
	freq_output: FreqEnum = Field('D')
	rate_limit: Optional[float] = Field(None, ge=0)
	cum_limit: Optional[float] = Field(None, ge=0)
	depends: Optional[Depends] = Field(None)
	type: SchemasEnum = Field(SchemasEnum.period, const=True)

	# @validator('end')
	# def start_end_match_type(cls,v,values):
	#     if type(v) != type(values['start']):
	#         raise ValueError('start and end must be the same type')
	#     return v

	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True

	def date_mode(self):
		if isinstance(self.start,date):
			return True
		if isinstance(self.start,int):
			return False

	def generate_forecast(self, freq_output=None, iter=None, seed=None, ppf=None):
		#If freq_output is not defined in the method. 
  		# Use the freq_out defined in the class
		if freq_output is None:
			freq_output = self.freq_output

		#If freq_output is not defined in the method. 
  		# Use the freq_out defined in the class
		if iter is None:
			iter = self.iter

		if seed is None:
			seed = self.seed
   
		if ppf is None:
			ppf = self.ppf
   
		_forecast = self.dca.forecast(
			time_list = self.time_list,start=self.start, end=self.end, freq_input=self.freq_input, 
			freq_output=freq_output, rate_limit=self.rate_limit, 
   			cum_limit=self.cum_limit, iter=iter, ppf=self.ppf, seed=seed
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

	def generate_cashflow(self, freq_output=None, add_name=None, seed=None, ppf=None,add_cash_params:list=None):
		if freq_output is None:
			freq_output = self.freq_output
   
		if seed is None:
			seed = self.seed

		if ppf is None:
			ppf = self.ppf

		if self.forecast is not None and any([self.cashflow_params is not None,add_cash_params is not None]):

			_forecast = self.forecast.df()

			is_date_mode = self.date_mode()
			#Format date

			list_cashflow_model = []
   
			#Broadcast the number of iterations between the forecast and the cashflows to be consistent.
			#Example: If the Forecast have 10 iterations the cashflow params must have either 10 or 1 iterations.
   
			shapes_to_broadcast = []
   
			#forecast iterations
			forecast_iterations = _forecast['iteration'].unique()
			shapes_to_broadcast.append(len(forecast_iterations))

			#Forecast iterations shape.
			#Example. If there's only one iteration in Forecast 
			# the variable forecast_iterations would be = np.array([0]). 
			# At the same time if the broadcasted shape is (10,) due to 10 iterations in cashflows params
			# the iterate_new_shape would be np.array([0,0,0,0,0,0,0,0,0,0]). 
			# This is done to make the 10 different cashflow models.
			
			#Iterate over list of cases
			if self.cashflow_params is None:
				cashflow_params = []
			else:
				cashflow_params = self.cashflow_params.copy()
			if add_cash_params:
				cashflow_params.extend(add_cash_params)

			#Cashflows Iterations
			for p in cashflow_params:
				shapes_to_broadcast.append(p.iter)
    
			#shapes broadcast
			shapes = np.broadcast_shapes(*shapes_to_broadcast)
			iterate_new_shape = forecast_iterations * np.ones(shapes)
    
			if len(cashflow_params)==0:
				raise ValueError('No Cashflow Params are set')
			for i in range(shapes[0]):

				_forecast_i = _forecast[_forecast['iteration']==iterate_new_shape[i]]

				cashflow_model_dict = {'name':self.name + '_' + str(i)}
				for param in cashflow_params:
					#initialize the individual cashflow dict

					if param.target not in cashflow_model_dict.keys():
						cashflow_model_dict[param.target] = []

					cashflow_dict = {}
					
					if add_name is None:
						csh_name = self.name
					else:
						csh_name = add_name + '-' + self.name
					#set the name
					cashflow_dict.update({
						'name':f'{param.name}_{csh_name}',
						'start':_forecast_i.index.min().strftime('%Y-%m-%d') if is_date_mode else _forecast_i.index.min()*converter_factor(freq_output,self.freq_input),
						'end':_forecast_i.index.max().strftime('%Y-%m-%d') if is_date_mode else _forecast_i.index.max()*converter_factor(freq_output,self.freq_input),
						'freq_output':freq_output,'freq_input':freq_output
					})
					#p_range = pd.period_range(start=cashflow_dict['start'], end=cashflow_dict['end'], freq=freq_output)
					#steps = len(p_range)
					param_value = param.get_value(i,freq_output=freq_output, seed=seed, ppf=ppf)
					param_wi = param.get_wi(i,freq_output=freq_output, seed=seed, ppf=ppf)
     
					if param.freq_value:
						freq_conv = converter_factor(param.freq_value,freq_output)
					else:
						freq_conv = 1
      
					if isinstance(param_wi,ChgPts):
						idx_wi = pd.to_datetime(param_wi.date).to_period(freq_output) if is_date_mode  else param.array_values.date
						values_series_wi = pd.Series(param_wi.value, index=idx_wi)
					else:
						values_series_wi = param_wi
					if param.multiply:
						#Forecast Column name to multiply the param
						#Check if the column exist in the forecast pandas dataframe
						if param.multiply in _forecast_i.columns:
							multiply_col = param.multiply
						else:
							print(f'{param.multiply} is not in forecast columns. {_forecast_i.columns}')
							continue

						if isinstance(param_value,ChgPts):
							#If the array values date is a datetime.date convert to output frecuency
							#to be consistent with the freq of the forecast when multiply
							idx = pd.to_datetime(param_value.date).to_period(freq_output) if is_date_mode  else param_value.date
							values_series = pd.Series(param_value.value, index=idx).groupby(level=0).agg(param.agg)
							_array_values = _forecast_i[multiply_col].multiply(values_series).multiply(values_series_wi).dropna()

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
							_const_value = _forecast_i[multiply_col].multiply(param_value*freq_conv).multiply(values_series_wi)
							cashflow_dict.update({'const_value':_const_value.tolist()})

					else:
						if isinstance(param_value,ChgPts):
							idx = pd.to_datetime(param_value.date).to_period(freq_output) if is_date_mode  else param_value.date
							values_series = pd.Series(param_value.value, index=idx).groupby(level=0).agg(param.agg)

							_array_values = values_series.multiply(values_series_wi).dropna()
							cashflow_dict.update({
								'chgpts': ChgPts(date = _array_values.index.strftime('%Y-%m-%d').tolist(), value = _array_values.tolist())
							})
						else:
							cashflow_dict.update({
								'const_value':param_value * freq_conv * values_series_wi,
								'periods':param.periods
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

	def tree(self, style='bold', guide_style='bold',show_emoji=True):
		emoji = ':chart_with_downwards_trend:'
		tree_text = emoji+self.name if show_emoji else self.name
		node_tree = Tree(tree_text, style=style, guide_style=guide_style)

		return node_tree

	def layout(self, emoji=':chart_with_downwards_trend:', title_style = 'bold green'):
		text = yaml.dump(self.dict(exclude_unset=True, exclude_none=True))  

		panel_text = f'{emoji}\n' + text
		panel = Panel(panel_text,title=f'[{title_style}]{self.name}[/{title_style}]')
		return panel

class Scenario(ScheduleBase):
	periods: Union[List[Period],Dict[str,Period]] = Field(None)
	freq_output: str = Field('D')
	type: SchemasEnum = Field(SchemasEnum.scenario, const=True)
 
	@validator('periods')
	def match_periods_freqs(cls,v):
		if isinstance(v,list):
			v = {i.name:i for i in v}
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

	def generate_forecast(self, periods:list = None, freq_output=None, iter=None, seed=None, ppf=None):
		#if freq_output is None:
		#	freq_output = self.freq_output
		
		#Make filter
		if periods:
			_periods = [i for i in self.periods if i in periods]
		else:
			_periods = list(self.periods.keys())
   
		if iter is None:
			iter = self.iter

		if seed is None:
			seed = self.seed
   
		if ppf is None:
			ppf = self.ppf

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
			_f = self.periods[p].generate_forecast(freq_output=freq_output, iter=iter, seed=seed, ppf=ppf)
			
			#try:
			#	_f = self.periods[p].generate_forecast()
			#except Exception as e:
			#	print(e)
			#	listself.periods_errors.append(self.periods[p].name)
			#else:
			list_forecast.append(_f)


		scenario_forecast = pd.concat(list_forecast, axis=0)
		scenario_forecast['scenario'] = self.name

		fr_freq = freq_output
		#fr_freq = scenario_forecast.index.freqstr[0]

		if isinstance(scenario_forecast.index[0],pd.Period):
			self.forecast = Forecast(freq=fr_freq,**scenario_forecast.to_timestamp().reset_index().to_dict(orient='list'))
		else:
			self.forecast = Forecast(freq=fr_freq,**scenario_forecast.reset_index().to_dict(orient='list'))

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


	def generate_cashflow(self,periods:list = None, freq_output=None, add_name=None, seed=None, ppf=None, add_cash_params:list=None):
		if freq_output is None:
			freq_output = self.freq_output
		#Make filter
		if periods:
			_periods = [i for i in self.periods if i in periods]
		else:
			_periods = list(self.periods.keys())

		n = self._iterations(periods = periods)
		#print(n)
  
		if seed is None:
			seed = self.seed
   
		if ppf is None:
			ppf = self.ppf

		cashflow_models = [CashFlowModel(name=f'{self.name}_{i}') for i in range(n)]
		list_periods_errors = []
		pass_cashflow_params = []     #Cashflow to pass to periods
		general_cashflow_params = []   #General cashflow for scenario
  
		if self.cashflow_params is None:
			cashflow_params = []
		else:
			cashflow_params = self.cashflow_params.copy()
		if add_cash_params:
			cashflow_params.extend(add_cash_params)

		if len(cashflow_params)>0:
			for i in cashflow_params:
				if i.general:
					general_cashflow_params.append(i)
				else:
					pass_cashflow_params.append(i) 
		else:	
			pass_cashflow_params = None
		for p in _periods:
			try:
				if add_name is None:
					csh_name = self.name
				else:
					csh_name = add_name + '-' + self.name
				_cf = self.periods[p].generate_cashflow(freq_output=freq_output, add_name=csh_name, seed=seed, ppf=ppf, add_cash_params=pass_cashflow_params)
			except Exception as e:
				print(p,e)
				traceback.print_exc()
				list_periods_errors.append(self.periods[p].name)
			else:
				if len(_cf)==1:
					_cf = [_cf[0] for i in range(n)]
			
				for i in range(n):
					cashflow_models[i].append(_cf[i])
     
		#add scenario cashflow that is not attached to periods
		if len(general_cashflow_params)>0:
			_forecast = self.forecast.df()
			is_date_mode = False if isinstance(_forecast.index[0],int) else True
			cashflow_model_dict = {'name':self.name + '_genral'}
			for gparam in general_cashflow_params:
				if gparam.target not in cashflow_model_dict.keys():
					cashflow_model_dict[gparam.target] = []
				cashflow_dict = {}
				cashflow_dict.update({
					'name':gparam.name,
					'start':_forecast.index.min().strftime('%Y-%m-%d') if is_date_mode else _forecast.index.min()*converter_factor(freq_output,self.freq_input),
					'end':_forecast.index.max().strftime('%Y-%m-%d') if is_date_mode else _forecast.index.max()*converter_factor(freq_output,self.freq_input),
					'freq_output':freq_output, 'freq_input':freq_output
				})
				#p_range = pd.period_range(start=cashflow_dict['start'], end=cashflow_dict['end'], freq=freq_output)
				#steps = len(p_range)
				param_value = gparam.get_value(i,freq_output=freq_output, ppf=ppf, seed=seed)
				param_wi = gparam.get_wi(i,freq_output=freq_output, ppf=ppf, seed=seed)

				if gparam.freq_value:
					freq_conv = converter_factor(gparam.freq_value,freq_output)
				else:
					freq_conv = 1
      
				if isinstance(param_wi,ChgPts):
					idx_wi = pd.to_datetime(param_wi.date).to_period(freq_output) if is_date_mode  else gparam.array_values.date
					values_series_wi = pd.Series(param_wi.value, index=idx_wi)
				else:
					values_series_wi = param_wi

				if isinstance(param_value,ChgPts):
					idx = pd.to_datetime(param_value.date).to_period(freq_output) if is_date_mode  else param_value.date
					values_series = pd.Series(param_value.value, index=idx)

					_array_values = values_series.multiply(values_series_wi).dropna()
					cashflow_dict.update({
						'chgpts': ChgPts(date = _array_values.index.strftime('%Y-%m-%d').tolist(), value = _array_values.tolist())
					})
				else:
					cashflow_dict.update({
						'const_value':param_value * freq_conv * values_series_wi,
						'periods':gparam.periods
					})

				cashflow_model_dict[gparam.target].append(cashflow_dict)
    
			for key in cashflow_model_dict:
				if len(cashflow_model_dict[key]) == 0:
					del cashflow_model_dict[key]
			
			cashflow_model_gen = CashFlowModel(**cashflow_model_dict)

			for c in cashflow_models:
				c.append(cashflow_model_gen)


		self.cashflow = cashflow_models

		return cashflow_models

	def tree(self, style='bold', guide_style='bold',show_emoji=True):
		emoji = ':twisted_rightwards_arrows:'
		tree_text = emoji+self.name if show_emoji else self.name
		node_tree = Tree(tree_text, style=style, guide_style=guide_style)

		for p in self.periods:
			node_tree.add(self.periods[p].tree(style=style, guide_style=guide_style,show_emoji=show_emoji))
		return node_tree

	def layout(self, emoji=':twisted_rightwards_arrows:', title_style = 'bold cyan',period_kw={}):
		
		if self.periods:
			layout = Layout()
   
			#list of period layouts
			list_layouts = []
			for p in self.periods:
				lay_p = self.periods[p].layout(**period_kw)
				list_layouts.append(Layout(lay_p,name=self.periods[p].name))

			layout.split_column(*list_layouts)
			panel = Panel.fit(layout,title=f'[{title_style}]{self.name}[/{title_style}]')
			return panel

class Well(ScheduleBase):
	scenarios : Union[List[Scenario],Dict[str,Scenario]] = Field(None)
	type: SchemasEnum = Field(SchemasEnum.well, const=True)
	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True

	@validator('scenarios')
	def match_periods_freqs(cls,v):
		if isinstance(v,list):
			v = {i.name:i for i in v}
		format_list = []
		freq_list = []
		for i in v:
			for j in v[i].periods:
				format_list.append(v[i].periods[j].dca.format())
				freq_list.append(v[i].periods[j].freq_output)

		if all(i==format_list[0] for i in format_list)&all(i==freq_list[0] for i in freq_list):
			return v 
		raise ValueError(f'The format of the periods are different {format_list}')

	def generate_forecast(self, scenarios:Union[list,dict] = None, freq_output=None, iter=None, seed=None, ppf=None):
		#Make filter
		if scenarios:
			scenarios_list = scenarios if isinstance(scenarios,list) else list(scenarios.keys())
			_scenarios = [i for i in self.scenarios if i in scenarios_list]
		else:
			_scenarios = list(self.scenarios.keys())
   
		list_forecast = []
  
		if iter is None:
			iter = self.iter

		if seed is None:
			seed = self.seed
   
		if ppf is None:
			ppf = self.ppf
  
		for s in _scenarios:
			periods = scenarios[s] if isinstance(scenarios,dict) else None
			_f = self.scenarios[s].generate_forecast(periods = periods, freq_output=freq_output, iter=iter, seed=seed, ppf=ppf)

			list_forecast.append(_f)
   
		well_forecast = pd.concat(list_forecast, axis=0)
		well_forecast['well'] = self.name
		fr_freq = freq_output
		#fr_freq = well_forecast.index.freqstr[0]
		if isinstance(well_forecast.index[0],pd.Period):
			self.forecast = Forecast(freq=fr_freq,**well_forecast.to_timestamp().reset_index().to_dict(orient='list'))
		else:
			self.forecast = Forecast(freq=fr_freq,**well_forecast.reset_index().to_dict(orient='list'))

		return well_forecast

	def generate_cashflow(self, scenarios:Union[list,dict] = None, freq_output=None, add_name=None, seed=None, ppf=None,add_cash_params:list=None):
		if scenarios:
			scenarios_list = scenarios if isinstance(scenarios,list) else list(scenarios.keys())
			_scenarios = [i for i in self.scenarios if i in scenarios_list]
		else:
			_scenarios = list(self.scenarios.keys())
   
		list_cashflows = []
  
		if seed is None:
			seed = self.seed
   
		if ppf is None:
			ppf = self.ppf

		pass_cashflow_params = []     #Cashflow to pass to periods
		general_cashflow_params = []   #General cashflow for scenario
		if self.cashflow_params is None:
			cashflow_params = []
		else:
			cashflow_params = self.cashflow_params.copy()
		if add_cash_params:
			cashflow_params.extend(add_cash_params)
		if len(cashflow_params)>0:
			for i in cashflow_params:
				if i.general:
					general_cashflow_params.append(i)
				else:
					pass_cashflow_params.append(i) 
		else:
			pass_cashflow_params=None
		for s in _scenarios:
			if add_name is None:
				csh_name = self.name
			else:
				csh_name = add_name + '-' + self.name
			periods = scenarios[s] if isinstance(scenarios,dict) else None
			cash_s = self.scenarios[s].generate_cashflow(periods=periods, freq_output=freq_output, add_name=csh_name, seed=seed, ppf=ppf, add_cash_params=pass_cashflow_params)

			list_cashflows.extend(cash_s)

		#add scenario cashflow that is not attached to periods
		if len(general_cashflow_params)>0:
			_forecast = self.forecast.df()
			is_date_mode = False if isinstance(_forecast.index[0],int) else True
			cashflow_model_dict = {'name':self.name + '_genral'}
			for gparam in general_cashflow_params:
				if gparam.target not in cashflow_model_dict.keys():
					cashflow_model_dict[gparam.target] = []
				cashflow_dict = {}
				cashflow_dict.update({
					'name':gparam.name,
					'start':_forecast.index.min().strftime('%Y-%m-%d') if is_date_mode else _forecast.index.min()*converter_factor(freq_output,self.freq_input),
					'end':_forecast.index.max().strftime('%Y-%m-%d') if is_date_mode else _forecast.index.max()*converter_factor(freq_output,self.freq_input),
					'freq_output':freq_output, 'freq_input':freq_output
				})
				#p_range = pd.period_range(start=cashflow_dict['start'], end=cashflow_dict['end'], freq=freq_output)
				#steps = len(p_range)
				param_value = gparam.get_value(i,freq_output=freq_output, ppf=ppf, seed=seed)
				param_wi = gparam.get_wi(i,freq_output=freq_output, ppf=ppf, seed=seed)
    
				if gparam.freq_value:
					freq_conv = converter_factor(gparam.freq_value,freq_output)
				else:
					freq_conv = 1
     
				if isinstance(param_wi,ChgPts):
					idx_wi = pd.to_datetime(param_wi.date).to_period(freq_output) if is_date_mode  else gparam.array_values.date
					values_series_wi = pd.Series(param_wi.value, index=idx_wi)
				else:
					values_series_wi = param_wi

				if isinstance(param_value,ChgPts):
					idx = pd.to_datetime(param_value.date).to_period(freq_output) if is_date_mode  else param_value.date
					values_series = pd.Series(param_value.value, index=idx)

					_array_values = values_series.multiply(values_series_wi).dropna()
					cashflow_dict.update({
						'chgpts': ChgPts(date = _array_values.index.strftime('%Y-%m-%d').tolist(), value = _array_values.tolist())
					})
				else:
					cashflow_dict.update({
						'const_value':param_value * freq_conv * values_series_wi,
						'periods':gparam.periods
					})

				cashflow_model_dict[gparam.target].append(cashflow_dict)
    
			for key in cashflow_model_dict:
				if len(cashflow_model_dict[key]) == 0:
					del cashflow_model_dict[key]
			
			cashflow_model_gen = CashFlowModel(**cashflow_model_dict)

			for c in list_cashflows:
				c.append(cashflow_model_gen)
   
		self.cashflow = list_cashflows

		return list_cashflows

	def tree(self, style='bold', guide_style='bold',show_emoji=True):
		emoji = ':tokyo_tower:'
		tree_text = emoji+self.name if show_emoji else self.name
		node_tree = Tree(tree_text, style=style, guide_style=guide_style)

		for p in self.scenarios:
			node_tree.add(self.scenarios[p].tree(style=style, guide_style=guide_style,show_emoji=show_emoji))
		return node_tree

	def layout(self, emoji=':tokyo_tower:', title_style = 'bold magenta',period_kw={},scenario_kw={}):
		
		if self.scenarios:
			layout = Layout()
   
			#list of period layouts
			list_layouts = []
			for p in self.scenarios:
				lay_p = self.scenarios[p].layout(period_kw=period_kw,**scenario_kw)
				list_layouts.append(Layout(lay_p,name=self.scenarios[p].name))

			layout.split_row(*list_layouts)
			panel = Panel.fit(layout,title=f'[{title_style}]{self.name}[/{title_style}]')
			return panel

   
class WellsGroup(ScheduleBase):
	wells : Union[List[Well],Dict[str,Well]] = Field(None)
	type: SchemasEnum = Field(SchemasEnum.wellsgroup, const=True)

	class Config:
		arbitrary_types_allowed = True
		validate_assignment = True

	@validator('wells')
	def match_periods_freqs(cls,v):
		if isinstance(v,list):
			v = {i.name:i for i in v}
		format_list = []
		freq_list = []
		for i in v:
			for j in v[i].scenarios:
				for k in v[i].scenarios[j].periods:
					format_list.append(v[i].scenarios[j].periods[k].dca.format())
					freq_list.append(v[i].scenarios[j].periods[k].freq_output)

		if all(i==format_list[0] for i in format_list)&all(i==freq_list[0] for i in freq_list):
			return v 
		raise ValueError(f'The format of the periods are different {format_list}')


	def generate_forecast(self, wells:Union[list,dict] = None, freq_output=None, iter=None, seed=None, ppf=None):
		#Make filter
		if wells:
			wells_list = wells if isinstance(wells,list) else list(wells.keys())
			_wells = [i for i in self.wells if i in wells_list]
		else:
			_wells = self.wells
   
		list_forecast = []
  
		if iter is None:
			iter = self.iter

		if seed is None:
			seed = self.seed
   
		if ppf is None:
			ppf = self.ppf
  
		for w in _wells:
			scenarios = wells[w] if isinstance(wells,dict) else None
			_f = self.wells[w].generate_forecast(scenarios = scenarios, freq_output=freq_output, iter=iter, seed=seed, ppf=ppf)

			list_forecast.append(_f)
   
		wells_forecast = pd.concat(list_forecast, axis=0)

		fr_freq = freq_output
		if isinstance(wells_forecast.index[0],pd.Period):
			self.forecast = Forecast(freq=fr_freq,**wells_forecast.to_timestamp().reset_index().to_dict(orient='list'))
		else:
			self.forecast = Forecast(freq=fr_freq,**wells_forecast.reset_index().to_dict(orient='list'))

		return wells_forecast

	def generate_cashflow(self, wells:Union[list,dict] = None, freq_output=None, add_name=None, seed=None, ppf=None, add_cash_params:list=None):
		if wells:
			wells_list = wells if isinstance(wells,list) else list(wells.keys())
			_wells = [i for i in self.wells if i in wells_list]
		else:
			_wells = list(self.wells.keys())
   
		if seed is None:
			seed = self.seed

		if ppf is None:
			ppf = self.ppf
   
		list_cashflows = []
		len_cashflows = []
		pass_cashflow_params = []     #Cashflow to pass to periods
		general_cashflow_params = []   #General cashflow for scenario
  
		if self.cashflow_params is None:
			cashflow_params = []
		else:
			cashflow_params = self.cashflow_params.copy()
		if add_cash_params:
			cashflow_params.extend(add_cash_params)
   
		if len(cashflow_params)>0:
			for i in self.cashflow_params:
				if i.general:
					general_cashflow_params.append(i)
				else:
					pass_cashflow_params.append(i)   
		else:
			pass_cashflow_params = None
      
		for w in _wells:
			if add_name is None:
				csh_name = self.name
			else:
				csh_name = add_name + '-' + self.name
			scenarios = wells[w] if isinstance(wells,dict) else None
			cash_s = self.wells[w].generate_cashflow(scenarios=scenarios, freq_output=freq_output, add_name=csh_name, seed=seed, ppf=ppf, add_cash_params=pass_cashflow_params)

			len_cashflows.append(len(cash_s))
   
			list_cashflows.append(cash_s)

		broadcast_shape = np.broadcast_shapes(*len_cashflows)[0]

		list_cashflows_merged = [CashFlowModel(name=f'{self.name}_{i}') for i in range(broadcast_shape)]
		for ch in list_cashflows:
			if len(ch)==1:
				ch = [ch[0] for i in range(broadcast_shape)]

			for i in range(broadcast_shape):
				list_cashflows_merged[i].append(ch[i])  

		#add scenario cashflow that is not attached to periods
		if len(general_cashflow_params)>0:
			_forecast = self.forecast.df()
			is_date_mode = False if isinstance(_forecast.index[0],int) else True
			cashflow_model_dict = {'name':self.name + '_genral'}
			for gparam in general_cashflow_params:
				if gparam.target not in cashflow_model_dict.keys():
					cashflow_model_dict[gparam.target] = []
				cashflow_dict = {}
				cashflow_dict.update({
					'name':gparam.name,
					'start':_forecast.index.min().strftime('%Y-%m-%d') if is_date_mode else _forecast.index.min()*converter_factor(freq_output,self.freq_input),
					'end':_forecast.index.max().strftime('%Y-%m-%d') if is_date_mode else _forecast.index.max()*converter_factor(freq_output,self.freq_input),
					'freq_output':freq_output, 'freq_input':freq_output
				})
				#p_range = pd.period_range(start=cashflow_dict['start'], end=cashflow_dict['end'], freq=freq_output)
				#steps = len(p_range)
				param_value = gparam.get_value(i,freq_output=freq_output, ppf=ppf, seed=seed)
				param_wi = gparam.get_wi(i,freq_output=freq_output, ppf=ppf, seed=seed)

				if gparam.freq_value:
					freq_conv = converter_factor(gparam.freq_value,freq_output)
				else:
					freq_conv = 1

				if isinstance(param_wi,ChgPts):
					idx_wi = pd.to_datetime(param_wi.date).to_period(freq_output) if is_date_mode  else gparam.array_values.date
					values_series_wi = pd.Series(param_wi.value, index=idx_wi)
				else:
					values_series_wi = param_wi

				if isinstance(param_value,ChgPts):
					idx = pd.to_datetime(param_value.date).to_period(freq_output) if is_date_mode  else param_value.date
					values_series = pd.Series(param_value.value, index=idx)

					_array_values = values_series.multiply(values_series_wi).dropna()
					cashflow_dict.update({
						'chgpts': ChgPts(date = _array_values.index.strftime('%Y-%m-%d').tolist(), value = _array_values.tolist())
					})
				else:
					cashflow_dict.update({
						'const_value':param_value * freq_conv *  values_series_wi,
						'periods':gparam.periods
					})

				cashflow_model_dict[gparam.target].append(cashflow_dict)
    
			for key in cashflow_model_dict:
				if len(cashflow_model_dict[key]) == 0:
					del cashflow_model_dict[key]
			
			cashflow_model_gen = CashFlowModel(**cashflow_model_dict)

			for c in list_cashflows_merged:
				c.append(cashflow_model_gen)
   
		self.cashflow = list_cashflows_merged

		return list_cashflows_merged

	def scenarios_maker(self,wells:Union[list,dict]=None, reduce:int=1):
		if wells:
			wells_list = wells if isinstance(wells,list) else list(wells.keys())
			_wells = [i for i in self.wells if i in wells_list]
		else:
			_wells = list(self.wells.keys())
   
		levels = []
		wells_dict = {}
		for w in _wells:
			if isinstance(wells,dict):
				list_scenarios = [i for i in list(self.wells[w].scenarios.keys()) if i in wells[w]]
			else:
				list_scenarios = list(self.wells[w].scenarios.keys())
   
			levels.append(len(list_scenarios))
			wells_dict.update({w:list_scenarios})

		# Escenarios Array
		escenarios_array = ed.fullfact(levels) if reduce==1 else ed.gsd(levels,reduce)
  
		scenarios_list = []
		for escenario in escenarios_array:
			esc = {_wells[i]:[wells_dict[_wells[i]][int(v)]] for i,v in enumerate(escenario)}

			scenarios_list.append(esc)

		return scenarios_list

	def tree(self, style='bold', guide_style='bold',show_emoji=True):
		emoji = ':factory:'
		tree_text = emoji+self.name if show_emoji else self.name
		node_tree = Tree(tree_text, style=style, guide_style=guide_style)

		for p in self.wells:
			node_tree.add(self.wells[p].tree(style=style, guide_style=guide_style,show_emoji=show_emoji))
		return node_tree
 
def model_from_dict(d:dict):
    
    if 'dca' in d.keys():
        return Period(**d)
    if 'periods' in d.keys():
        return Scenario(**d)
    if 'scenarios' in d.keys():
        return Well(**d)
    if 'wells' in d.keys():
        return WellsGroup(**d)