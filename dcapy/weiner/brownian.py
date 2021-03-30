# External Imports
import numpy as np 
import pandas as pd
from scipy import stats
from pydantic import BaseModel, Field
from typing import List, Union, Optional, Literal

#Local Imports
from ..dca import list_freq, converter_factor, ProbVar

class Weiner(BaseModel):
    initial_condition:  Union[float,List[float]] = Field(0)
    generator: ProbVar = Field(ProbVar())
    freq: Literal['M','D','A'] = Field('M')
    drift : float = Field(0)
    
    def weiner_generator(self,steps:int,processes:int,interval=None, seed=None):
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

    def brownian_motion(self,steps,processes, freq_output='D',interval=None, seed=None):
        
        if interval is not None:
            assert all([interval>=0,interval<=1])
            epsilon = self.weiner_generator(steps,processes,interval=interval)
        else:
            epsilon = self.weiner_generator(steps,processes, seed=seed)
        
        #Create zeros arrays for Weiner Process. Rows number of process, Columns Steps
        w = np.zeros((processes,steps))
        w[:,0] = self.initial_condition

        # Time Step size
        dt = converter_factor(self.freq,freq_output)

        #Drift for the Brownian Process
        mu = self.drift * dt       

        #Weiner Process
        for n in range(processes):
            for t in range(1,steps):
                w[n,t] = w[n,t-1] + mu + (epsilon[n,t]*np.sqrt(dt))
                
        return pd.DataFrame(w.T, index=range(steps),columns=range(processes))
    
    def geometric_brownian_motion(self,steps,processes, freq_output='D',interval=None, seed=None):

        if interval is not None:
            assert all([interval>=0,interval<=1])
            epsilon = self.weiner_generator(steps,processes,interval=interval)
        else:
            epsilon = self.weiner_generator(steps,processes, seed=seed)
        
        #Create zeros arrays for Weiner Process. Rows number of process, Columns Steps
        w = np.zeros((processes,steps))
        w[:,0] = self.initial_condition
        
        # Time Step size
        dt = converter_factor(self.freq,freq_output)
        
        #Drift for the Brownian Process
        mu = self.drift * dt
        var = np.power(self.generator.kw['scale'],2) * dt

               
        drift = mu - var/2

        #Weiner Process
        for n in range(processes):
            for t in range(1,steps):
                w[n,t] = w[n,t-1]*np.exp(drift + (epsilon[n,t]*np.sqrt(dt)))
                
        return pd.DataFrame(w.T, index=range(steps),columns=range(processes))
        
        
        
        
        
        
        
    
        
     
     