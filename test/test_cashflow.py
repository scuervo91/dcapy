import unittest
import numpy as np
from datetime import date
from pandas.testing import assert_frame_equal
import pandas as pd

from dcapy.cashflow import CashFlow, CashFlowModel

class TestCashFlow(unittest.TestCase):
    def test_npv(self):
        oil_sell = CashFlow(
            name = 'oil_sell',
            const_value= [10000,5000,8000,12000,30000],
            start = date(2021,1,1),
            end = date(2021,5,1),
            freq_input = 'M'
        )
        oil_capex = CashFlow(
            name = 'oil_capex',
            const_value= [-50000],
            start = date(2021,1,1),
            end = date(2021,1,1),
            freq_input = 'M'
        )
        cm = CashFlowModel(
            name = 'Example Cashflow Model',
            income=[oil_sell],
            capex=[oil_capex]
        )
        
        assert_frame_equal(cm.npv(0.08), pd.DataFrame({'npv':3065.22267}, index=[0.08])) 
    
    def test_irr(self):
        oil_sell = CashFlow(
            name = 'oil_sell',
            const_value= [40,39,59,55,20],
            start = date(2021,1,1),
            end = date(2021,5,1),
            freq_input = 'M'
        )
        oil_capex = CashFlow(
            name = 'oil_capex',
            const_value= [-140],
            start = date(2021,1,1),
            end = date(2021,1,1),
            freq_input = 'M'
        )
        cm = CashFlowModel(
            name = 'Example Cashflow Model',
            income=[oil_sell],
            capex=[oil_capex]
        )
        print(cm.irr())
        assert 0.28095 == round(cm.irr(),5)