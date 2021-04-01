import unittest
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import os
from datetime import date
from dcapy import dca
from dcapy.models import Period

class TestArpsBasic(unittest.TestCase):
    def setUp(self):
        workdir = os.path.dirname(__file__)
        self.df1 = pd.read_csv(os.path.join(workdir,'data','wor_test_1.csv'), index_col=0)
        self.df2 = pd.read_csv(os.path.join(workdir,'data','wor_test_2.csv'), index_col=0,parse_dates=True).to_period('D')
    def test_wor_forecast(self):
        time1 = np.arange(0,10,1)
        qi1 = 500,
        slope = 3e-6
        bswi = 0.5
        wori = dca.bsw_to_wor(bswi)
        fluid_rate = [5000]*10
        f1 = dca.wor_forecast(time1,fluid_rate,slope,wori, rate_limit=None, wor_limit=None, cum_limit=1e5)
        assert_frame_equal(f1, self.df1)
        
    def test_wor_class(self):
        bsw = 0.5
        slope = [3.5e-6,3e-6,4e-6]
        ti =  date(2021,1,1)
        w1 = dca.Wor(bsw=bsw,slope=slope,ti=ti, glr=0.3, fluid_rate = 1000,)
        data = dict(
            start = date(2021,1,1),
            end = date(2021,1,10),
            freq_input = 'D',
            freq_output = 'D',
            rate_limit = 480,
        )
        print(w1.forecast(**data))
        f1 = w1.forecast(**data)
        
        assert_frame_equal(f1, self.df2)
        
    def test_period_wor(self):
        data = {
            'name':'pdp',
            'dca': {
                'ti':'2021-01-01',
                'bsw':0.3,
                'slope':[1e-5,1e-7],
                'fluid_rate':1000,
                'gor':0.3
            },
            'start':'2021-01-01',
            'end':'2021-06-01',
            'freq_input':'D',
            'freq_output':'M',
            'cashflow_params':
                [
                    {
                        'name':'oil_var_opex',
                        'const_value':7,
                        'multiply':'oil_volume',
                        'target':'opex'
                    },
                    {
                        'name':'income',
                        'array_values':{
                            'date':['2021-01-01','2021-02-01','2021-03-01','2021-04-01','2021-05-01','2021-06-01'],
                            'value':[38,42,45,50,55,39]
                        },
                        'multiply':'oil_volume',
                        'target':'income'
                    }
                ]
        }


        p1 = Period(**data)

        p1.generate_forecast()
        p1.generate_cashflow()
        np.testing.assert_allclose(p1.forecast.df()['oil_rate'],[700.,563.45097851, 387.34433853, 236.15090819, 134.126415, 700.,698.48264692, 695.60681771, 691.25062092, 685.49867539])
        np.testing.assert_allclose(p1.forecast.df()['water_rate'],[300.,436.54902149, 612.65566147, 763.84909181, 865.873585, 300.,301.51735308, 304.39318229, 308.74937908, 314.50132461])
        np.testing.assert_allclose(p1.forecast.df()['gas_rate'],[210.,169.03529355, 116.20330156,  70.84527246,  40.2379245,210.,209.54479408, 208.68204531, 207.37518627, 205.64960262])
        np.testing.assert_allclose(p1.cashflow[0].fcf()['fcf'].values,[976500.,773054.74252052, 624399.07370503, 403818.05299662, 257790.96962859])
        #np.testing.assert_allclose(p1.cashflow[1].fcf()['fcf'].values,[976500.,958318.19157906, 1121318.19015604, 1182038.56176468,317528.45410345])
