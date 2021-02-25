from abc import ABC, abstractmethod 
from pydantic import BaseModel, Field
import pandas as pd
from typing import List, Optional,Literal, Union
from datetime import date

class DCA(ABC):
    """ 
    Declare the DCA abstract Class that can be subclassed by the all Diferent 
    declination types
    """
    @abstractmethod
    def __str__(self):
        pass 
    
    @abstractmethod
    def __repr__(self):
        pass   
    
    @abstractmethod
    def forecast(self):
        pass     


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