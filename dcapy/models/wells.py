#External Imports
from pydantic import BaseModel
from typing import List

#Local imports
from .schedule import Schedule 

class Well(BaseModel):
    name : str 
    schedule : Schedule
    
class WellsGroup(BaseModel):
    name : str 
    wells : List[Well]
