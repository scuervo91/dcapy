import numpy as np 
import pandas as pd
from scipy import stats
from ..dca import list_freq, converter_factor

class Weiner:
    def __init__(self,initial_condition=0,generator=stats.norm,
                 mu=0, freq_mu='D', seed = None, arg_generator=[],
                 kw_generator={}):
        self.initial_condition = initial_condition
        self.generator = generator
        self.mu = mu
        self.freq_mu = freq_mu
        self.seed = seed
        self.arg_generator = arg_generator
        self.kw_generator = kw_generator
        
        
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

    @property
    def arg_generator(self):
        return self._arg_generator
    
    @arg_generator.setter
    def arg_generator(self,value):
        assert isinstance(value,list)
        self._arg_generator = value 

    def weiner_generator(self,steps,processes):
        for i in [steps,processes]:
            assert isinstance(i,int)
        
        #Generate random time normalized
        epsilon = self.generator.rvs(*self.arg_generator,size=(processes,steps),
                                     random_state=self.seed,
                                     **self.kw_generator)

        return epsilon
    
    def weiner_confidence_interval(self,steps,processes,interval=0.66):
        
        half = (1-interval)/2
        
        min_x = half 
        max_x = 1-half 
        
        n_vector = np.linspace(min_x,max_x,processes)
        n_array = np.broadcast_to(n_vector,(steps,processes)).T
        
        epsilon = self.generator.ppf(n_array,
                                     *self.arg_generator,
                                     **self.kw_generator)
        
        return epsilon
        

    def brownian_motion(self,steps,processes, freq='D',interval=None):
        
        if interval is not None:
            assert all([interval>=0,interval<=1])
            epsilon = self.weiner_confidence_interval(steps,processes,interval)
        else:
            epsilon = self.weiner_generator(steps,processes)
        
        #Create zeros arrays for Weiner Process. Rows number of process, Columns Steps
        w = np.zeros((processes,steps))
        w[:,0] = self.initial_condition

        #Drift for the Brownian Process
        mu = self.mu * converter_factor(self.freq_mu,freq)
        
        # Time Step size
        dt = converter_factor(self.freq_mu,freq)

        #Weiner Process
        for n in range(processes):
            for t in range(1,steps):
                w[n,t] = w[n,t-1] + mu + (epsilon[n,t]*np.sqrt(dt))
                
        return pd.DataFrame(w.T, index=range(steps),columns=range(processes))
    
    def geometric_brownian_motion(self,steps,processes, freq='D',interval=None):

        if interval is not None:
            assert all([interval>=0,interval<=1])
            epsilon = self.weiner_confidence_interval(steps,processes,interval)
        else:
            epsilon = self.weiner_generator(steps,processes)
        
        #Create zeros arrays for Weiner Process. Rows number of process, Columns Steps
        w = np.zeros((processes,steps))
        w[:,0] = self.initial_condition
        
        #Drift for the Brownian Process
        mu = self.mu * converter_factor(self.freq_mu,freq)
        var = np.power(self.kw_generator['scale'],2) * converter_factor(self.freq_mu,freq)
        # Time Step size
        dt = converter_factor(self.freq_mu,freq)
               
        drift = mu - var/2

        #Weiner Process
        for n in range(processes):
            for t in range(1,steps):
                w[n,t] = w[n,t-1]*np.exp(drift + (epsilon[n,t]*np.sqrt(dt)))
                
        return pd.DataFrame(w.T, index=range(steps),columns=range(processes))
        
        
        
        
        
        
        
    
        
     
     