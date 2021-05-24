import pandas as pd 
import numpy as np 
from scipy import stats 
from datetime import datetime, date

def zscore(x:np.ndarray,y:np.ndarray,thld:float=2)->np.ndarray:
    """zscore. Filter for time series production. Estimate the first order derivative of
    the natural logaritmic of rate with respect to time. Return a numpy array of zeros with
    the points greater than the threshold with one.

    Parameters
    ----------
    x : np.ndarray
        [description]
    y : np.ndarray
        [description]
    thld : float, optional
        [description], by default 2

    Returns
    -------
    np.ndarray
        [description]
    """
    
    ## Assert x and y have the same shape
    assert x.shape == y.shape
    
    #Create the array for filter
    index = np.zeros(x.shape)
    
    try:
        vtoordinal = np.vectorize(datetime.toordinal)
        x = vtoordinal(x)
    except Exception as e:
        x = x.astype(float)

    
    # Logaritmic of rates
    logy = np.log(y)
    
    #Derivative
    dev = np.gradient(logy) / np.gradient(x)
    #dev = np.append(dev[0],dev)
    #Estimate z Score
    abs_zscore=np.abs(stats.zscore(dev))
    
    index[abs_zscore>thld] = 1
    
    return index


def exp_wgh_avg(y,beta):

    yw = np.zeros(y.shape[0])
    
    for i,r in enumerate(y):
        if i>0:
            yw[i] = (beta*yw[i-1] + (1-beta)*y[i])
            
    bias_correction = 1 - np.power(beta,np.arange(len(yw)))
    
    y = np.nan_to_num(yw / bias_correction)
    
    return y

def beta_from_days(days):
    return 1 - (1/days)
    
     
    
    
    
