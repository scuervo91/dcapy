from abc import ABC, abstractmethod 

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
    
    @abstractmethod
    def fit(self):
        pass  
    
    @abstractmethod
    def plot(self):
        pass  
    