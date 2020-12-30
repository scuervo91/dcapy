import numpy as np 
import pandas as pd
from scipy import stats
from ..dca import list_freq, converter_factor

class Weiner:
    def __init__(self,initial_condition=0,generator=stats.norm,
                 mu=0, freq_mu='D', seed = None, kw_generator={},arg_generator=[]):
        self.initial_condition = initial_condition
        self.generator = generator
        self.mu = mu
        self.freq_mu = freq_mu
        self.seed = seed
        self.kw_generator = kw_generator
        self.arg_generator= arg_generator
        
    ## Properties
    @property
    def initial_condition(self):
        return self._initial_condition
    
    @initial_condition.setter
    def initial_condition(self,value):
        assert isinstance(value,(int,float,list,np.ndarray))
        self._initial_condition = float(value)
        
    @property
    def generator(self):
        return self._generator
    
    @generator.setter
    def generator(self,value):
        assert issubclass(type(value),(stats.rv_continuous,stats.rv_discrete))
        self._generator = value

    @property
    def mu(self):
        return self._mu
    
    @mu.setter
    def mu(self,value):
        assert isinstance(value,(int,float))
        self._mu = float(value)   
        
    @property
    def freq_mu(self):
        return self._freq_mu
    
    @freq_mu.setter
    def freq_mu(self,value):
        assert value in list_freq
        self._freq_mu = value  
        
    @property
    def seed(self):
        return self._seed
    
    @seed.setter
    def seed(self,value):
        if value is not None:
            assert isinstance(value,int)
        self._seed = value  
        
    @property
    def kw_generator(self):
        return self._kw_generator
    
    @kw_generator.setter
    def kw_generator(self,value):
        assert isinstance(value,dict)
        self._kw_generator = value  
        
    def brownian_motion(self,steps,processes, freq='D'):
        
        for i in [steps,processes]:
            assert isinstance(i,int)
        
        #Create zeros arrays for Weiner Process. Rows number of process, Columns Steps
        w = np.zeros((processes,steps))
        w[:,0] = self.initial_condition
        
        #Drift for the Brownian Process
        mu = self.mu * converter_factor(self.freq_mu,freq)
        #Generate random time normalized
        epsilon = self.generator.rvs(size=(processes,steps),random_state=self.seed,*self.arg_generator,**self.kw_generator)
        
        dt = converter_factor(self.freq_mu,freq)

        #Weiner Process
        for n in range(processes):
            for t in range(1,steps):
                w[n,t] = mu + w[n,t-1] + (epsilon[n,t]*np.sqrt(dt))
                
        return pd.DataFrame(w.T, index=range(steps),columns=range(processes))
            
        
        
        
        
    
        
     
     