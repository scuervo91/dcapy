
import unittest
import numpy as np

from dcapy import dca

class TestArpsBasic(unittest.TestCase):
    def test_arps_exp_rate(self):
        time1 = [0,2,3,4,10]
        qi1 = 500
        di1 = 0.3 
        result = dca.arps_exp_rate(time1,qi1,di1)
        np.testing.assert_allclose(result,[500., 274.40581805, 203.28482987, 150.59710596,24.89353418])
    
    def test_arps_exp_cumulative(self):
        time1 = [0,2,3,4,10]
        qi1 = 500
        di1 = 0.3 
        result = dca.arps_exp_cumulative(time1,qi1,di1)
        np.testing.assert_allclose(result,[0.,  751.98060651,  989.0505671 , 1164.67631348,1583.68821939])

    def test_arps_hyp_rate(self):
        time1 = [0,2,3,4,10]
        qi1 = 500
        di1 = 0.3 
        b = 0.5
        result = dca.arps_hyp_rate(time1,qi1,di1,b)
        np.testing.assert_allclose(result,[500., 295.85798817, 237.81212842, 195.3125,80.])

    def test_arps_hyp_cum(self):
        time1 = [0,2,3,4,10]
        qi1 = 500
        di1 = 0.3 
        b = 0.5
        result = dca.arps_hyp_cumulative(time1,qi1,di1,b)
        np.testing.assert_allclose(result,[0.,  769.23076923, 1034.48275862, 1250.,2000.])

    def test_arps_arm_rate(self):
        time1 = [0,2,3,4,10]
        qi1 = 500
        di1 = 0.3 
        b = 1
        result = dca.arps_hyp_rate(time1,qi1,di1,b)
        np.testing.assert_allclose(result,[500., 312.5 , 263.15789474, 227.27272727,125.])

    def test_arps_arm_cum(self):
        time1 = [0,2,3,4,10]
        qi1 = 500
        di1 = 0.3 
        b = 1
        result = dca.arps_arm_cumulative(time1,qi1,di1,b)
        np.testing.assert_allclose(result,[0.,  783.33938208, 1069.75647695, 1314.09560061,2310.49060187])

        
if __name__ == '__main__':
    unittest.main()