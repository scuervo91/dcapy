import unittest
import numpy as np
from datetime import date
from pandas.testing import assert_frame_equal
import pandas as pd

from dcapy.wiener import Brownian, GeometricBrownian,MeanReversion
from dcapy.dca import ProbVar

class TestWiener(unittest.TestCase):
    def test_brownian1(self):
        rw = Brownian()
        steps = 500 
        processes = 20

        df = rw.generate(steps, processes,seed=21)
        
        r = {2: {495: 11.152279625836409,
            496: 10.979194046624608,
            497: 9.004250033237724,
            498: 10.237306317041806,
            499: 10.579619204777698},
            3: {495: -3.6353130098486304,
            496: -4.005152179544146,
            497: -4.802696801815472,
            498: -4.055889508042472,
            499: -4.538951067724309}}
        
        assert_frame_equal(df.iloc[-5:,2:4], pd.DataFrame(r))
        
    def test_brownian2(self):
        rw = Brownian(
            initial_condition=100,
            ti=0,
            drift = 0.2
        )
        steps = 500 
        processes = 20
        df = rw.generate(steps, processes, seed=21)
       
        
        r = {2: {495: 210.152279625832,
            496: 210.17919404662018,
            497: 208.4042500332333,
            498: 209.83730631703736,
            499: 210.37961920477323},
            3: {495: 195.36468699014836,
            496: 195.19484782045282,
            497: 194.5973031981815,
            498: 195.54411049195448,
            499: 195.26104893227264}}
        
        assert_frame_equal(df.iloc[-5:,2:4], pd.DataFrame(r))

    def test_brownian3(self):
        rw = Brownian(
            initial_condition=100,
            ti=0,
            drift = 0.2,
            generator=ProbVar(dist='norm', kw={'loc': 0, 'scale': 3})
        )
        steps = 500 
        processes = 20
        df = rw.generate(steps, processes, seed=21)

        
        
        r = {2: {495: 232.45683887750448,
            496: 232.13758213986907,
            497: 226.4127500997084,
            498: 230.31191895112065,
            499: 231.53885761432832},
            3: {495: 188.09406097045363,
            496: 187.18454346136707,
            497: 184.99190959455308,
            498: 187.43233147587208,
            499: 186.18314679682655}}
        
        assert_frame_equal(df.iloc[-5:,2:4], pd.DataFrame(r))
        
    def test_gbm(self):
        x3 = GeometricBrownian(
            initial_condition=80,
            generator = ProbVar(dist='norm',kw={'loc':0,'scale':0.26}, seed=9113),
            drift=0.01,
            freq_input='A')

        df = x3.generate(12,20, freq_output='A', seed=21)

        r = {2: {7: 230.30942808799614,
            8: 156.92923299033984,
            9: 97.2892180517065,
            10: 105.48791086392494,
            11: 142.36040205521132},
            3: {7: 162.28999454538706,
            8: 201.30367978983656,
            9: 170.0268546017239,
            10: 154.16105729801134,
            11: 114.83181244061205}}
        
        assert_frame_equal(df.iloc[-5:,2:4], pd.DataFrame(r))
        
    def test_mr(self):
        oil_mr = MeanReversion(
            initial_condition = 66,
            ti = 0,
            generator = {'dist':'norm','kw':{'loc':0,'scale':5.13}},
            m=46.77,
            eta=0.112652,
            freq_input = 'A'
        )

        df = oil_mr.generate(12,50, freq_output='A', seed=21)
        
        r ={2: {7: 75.17152947067616,
            8: 65.04597525741526,
            9: 54.13505845726961,
            10: 55.41636945148142,
            11: 60.879395238090595},
            3: {7: 68.96120878051282,
            8: 71.31717910163093,
            9: 65.83984995324853,
            10: 62.34497287513045,
            11: 55.34394126548259}}
        
        assert_frame_equal(df.iloc[-5:,2:4], pd.DataFrame(r))
    