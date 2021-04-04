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
                'slope':[2e-5,1e-5],
                'fluid_rate':1000,
                'gor':0.3
            },
            'start':'2021-01-01',
            'end':'2021-01-10',
            'freq_input':'D',
            'freq_output':'D',
            'cashflow_params':[
                    {
                        'name':'fix_opex',
                        'const_value':-5000,
                        'target':'opex',
                    },
                    {
                        'name':'var_opex',
                        'const_value':-5,
                        'target':'opex',
                        'multiply':'oil_volume'
                    },
                    {
                        'name':'income',
                        'const_value':60,
                        'target':'income',
                        'multiply':'oil_volume'
                    }
                ]
        }


        p1 = Period(**data)

        p1.generate_forecast()
        p1.generate_cashflow()
        np.testing.assert_allclose(p1.forecast.df()['oil_rate'],[700.        , 697.05179317, 694.09979475, 691.14438035,
            688.18592425, 685.22479918, 682.26137612, 679.2960241 ,
            676.32910996, 673.36099822, 700.        , 698.52794513, 697.05490171,
            695.58091663, 694.1060367 , 692.63030868, 691.15377923,
            689.6764949 , 688.19850219, 686.71984744])
        np.testing.assert_allclose(p1.forecast.df()['water_rate'],[300.        , 302.94820683, 305.90020525, 308.85561965,
            311.81407575, 314.77520082, 317.73862388, 320.7039759 ,
            323.67089004, 326.63900178,300.        , 301.47205487, 302.94509829,
            304.41908337, 305.8939633 , 307.36969132, 308.84622077,
            310.3235051 , 311.80149781,313.28015256])
        np.testing.assert_allclose(p1.forecast.df()['gas_rate'],[210.        , 209.11553795, 208.22993843, 207.3433141 ,
            206.45577727, 205.56743975, 204.67841284, 203.78880723,
            202.89873299, 202.00829946, 210.        , 209.55838354, 209.11647051,
            208.67427499, 208.23181101, 207.7890926 , 207.34613377,
            206.90294847, 206.45955066, 206.01595423])
        np.testing.assert_allclose(p1.cashflow[0].fcf()['fcf'].values,[33337.848625, 33256.668668, 33094.214815, 32931.583376,
            32768.794894, 32605.869821, 32442.828506, 32279.691186,
            32116.477975, 32034.854902])
        #np.testing.assert_allclose(p1.cashflow[1].fcf()['fcf'].values,[976500.,958318.19157906, 1121318.19015604, 1182038.56176468,317528.45410345])
