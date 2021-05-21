# External Imports
import numpy as np 
import pandas as pd
from scipy import stats
from pydantic import BaseModel, Field, Extra
from typing import List, Union, Optional
from datetime import date
#Local Imports
from ..dca import list_freq, converter_factor, ProbVar
from ..dca import FreqEnum
#from ..models import ChgPts

class Weiner(BaseModel):
    initial_condition:  Union[float,List[float]] = Field(0)
    ti: Union[int,date] = Field(0)
    steps: int = Field(1, gt=0)
    processes: int = Field(1, gt=0)
    generator: ProbVar = Field(ProbVar())
    freq_input: FreqEnum = Field('D')
    freq_output: FreqEnum = Field('D')

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        extra = Extra.forbid

    def weiner_generator(self,steps:int=None,processes:int=None,interval=None, seed=None):       
        for i in [steps,processes]:
            assert isinstance(i,int)
            
        if interval:
            half = (1-interval)/2
            
            min_x = half 
            max_x = 1-half 
            
            n_vector = np.linspace(min_x,max_x,processes)
            ppf = np.broadcast_to(n_vector,(steps,processes)).T
            
            size = None 
        else:
            size = (processes,steps)
            ppf=None
                
        return self.generator.get_sample(size=size, seed=seed, ppf=ppf)     
    
    def get_index_array(self, steps:int, freq_output:str):
        if isinstance(self.ti,date):
            return pd.period_range(start=self.ti,periods=steps,freq=freq_output)
            #idx = [i.to_timestamp().strftime('%Y-%m-%d') for i in pr]
        else:
            return np.arange(0,steps,1).tolist()

class Brownian(Weiner):
    drift : float = Field(0)
    
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        extra = Extra.forbid

    def generate(self,steps=None,processes=None, freq_output=None,interval=None, seed=None):
        """brownian_motion [summary]

        Args:
            steps ([type]): [description]
            processes ([type]): [description]
            freq_output (str, optional): [description]. Defaults to 'D'.
            interval ([type], optional): [description]. Defaults to None.
            seed ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        if steps is None:
            steps = self.steps
 
        if processes is None:
            processes = self.processes    

        if freq_output is None:
            if self.freq_output is None:
                freq_output = self.freq_input
            else:
                freq_output = self.freq_output
            
        if interval is not None:
            assert all([interval>=0,interval<=1])
            epsilon = self.weiner_generator(steps,processes,interval=interval)
        else:
            epsilon = self.weiner_generator(steps,processes, seed=seed)
        
        #Create zeros arrays for Weiner Process. Rows number of process, Columns Steps
        w = np.zeros((processes,steps))
        w[:,0] = self.initial_condition

        # Time Step size
        dt = converter_factor(self.freq_input,freq_output)

        #Drift for the Brownian Process
        mu = self.drift * dt       

        #Weiner Process
        for n in range(processes):
            for t in range(1,steps):
                w[n,t] = w[n,t-1] + mu + (epsilon[n,t]*np.sqrt(dt))
        
        idx = self.get_index_array(steps,freq_output)
        
        return pd.DataFrame(w.T, index=idx,columns=range(processes))

class GeometricBrownian(Weiner):
    drift : float = Field(0)
    
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        extra = Extra.forbid

    def generate(self,steps=None,processes=None, freq_output=None,interval=None, seed=None):
        """geometric_brownian_motion [summary]

        Args:
            steps ([type]): [description]
            processes ([type]): [description]
            freq_output (str, optional): [description]. Defaults to 'D'.
            interval ([type], optional): [description]. Defaults to None.
            seed ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        if steps is None:
            steps = self.steps
 
        if processes is None:
            processes = self.processes    

        if freq_output is None:
            if self.freq_output is None:
                freq_output = self.freq_input
            else:
                freq_output = self.freq_output
 
        if interval is not None:
            assert all([interval>=0,interval<=1])
            epsilon = self.weiner_generator(steps,processes,interval=interval)
        else:
            epsilon = self.weiner_generator(steps,processes, seed=seed)
        
        #Create zeros arrays for Weiner Process. Rows number of process, Columns Steps
        w = np.zeros((processes,steps))
        w[:,0] = self.initial_condition
        
        # Time Step size
        dt = converter_factor(self.freq_input,freq_output)
        
        #Drift for the Brownian Process
        mu = self.drift * dt
        var = np.power(self.generator.kw['scale'],2) * dt

               
        drift = mu - var/2

        #Weiner Process
        for n in range(processes):
            for t in range(1,steps):
                w[n,t] = w[n,t-1]*np.exp(drift + (epsilon[n,t]*np.sqrt(dt)))
        
        idx = self.get_index_array(steps,freq_output)
        
        return pd.DataFrame(w.T, index=idx,columns=range(processes))

class MeanReversion(Weiner):
    m : float = Field(0)
    eta : float = Field(0)
    
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        extra = Extra.forbid
        
    def generate(self,steps=None,processes=None, freq_output=None,interval=None, seed=None):
        """mean_reversion [summary]

        Args:
            steps ([type]): [description]
            processes ([type]): [description]
            freq_output (str, optional): [description]. Defaults to 'D'.
            interval ([type], optional): [description]. Defaults to None.
            seed ([type], optional): [description]. Defaults to None.
        """
        if steps is None:
            steps = self.steps
 
        if processes is None:
            processes = self.processes    

        if freq_output is None:
            if self.freq_output is None:
                freq_output = self.freq_input
            else:
                freq_output = self.freq_output
 
        epsilon = self.weiner_generator(steps,processes, seed=seed)
        
        #Create zeros arrays for Weiner Process. Rows number of process, Columns Steps
        w = np.zeros((processes,steps))
        w[:,0] = self.initial_condition
        
        # Time Step size
        dt = converter_factor(self.freq_input,freq_output)
        
        m = self.m 
        eta = self.eta
        
        #Weiner Process
        for n in range(processes):
            for t in range(1,steps):
                w[n,t] = m * (1 - np.exp(-eta)) + (np.exp(-eta) - 1) * w[n,t-1] + epsilon[n,t] + w[n,t-1]

        idx = self.get_index_array(steps,freq_output)
        
        return pd.DataFrame(w.T, index=idx,columns=range(processes))