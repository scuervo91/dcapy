import unittest
import numpy as np
from datetime import date
from pandas.testing import assert_frame_equal
import pandas as pd
import os 
import yaml

from dcapy.wiener import Brownian, GeometricBrownian,MeanReversion
from dcapy.dca import ProbVar
from dcapy.schedule import Period, Scenario, Well, model_from_dict
from dcapy.cashflow import CashFlowParams

class TestSchedule(unittest.TestCase):
    def test_period(self):
        p3cash_dict = {
            'name':'Period-1',
            'dca': {
                'ti':'2021-01-01',
                'di':0.3,
                'freq_di':'A',
                'qi':700,
                'b':0,
                'fluid_rate':250
            },
            'start':'2021-01-01',
            'end':'2022-01-01',
            'freq_output':'M',
            'rate_limit': 70,

            #Cashflow params keyword. It accept a list
            'cashflow_params':[
                    {
                        'name':'fix_opex',
                        'value':-5000,       #Fix opex of U$ 5000 monthly
                        'target':'opex',     #The cashflow generated is going to be an Opex in the cashflow model
                        'freq_value':'M'     #The frequency of the value is in Months
                    },
                    {
                        'name':'var_opex',
                        'value':-12,    #Variable Opex 12 USD/bbl of oil
                        'target':'opex', #The cashflow generated is going to be an Opex in the cashflow model
                        'multiply':'oil_volume'  #Multiply the 12 USD/bbl by the oil_volume Column which is the monthly cumulative oil
                    },
                    {
                        'name':'income',
                        'value':[20,30,40,60,80],             #Oil price 60 usd/bbl
                        'target':'income',      #The cashflow generated is going to be an Income in the cashflow model
                        'multiply':'oil_volume',  # Multiply the 60 USD/bbl by the oil_volume column
                        'wi':0.9, #working Interest. In this case represent 10% royalties 
                    },
                    {
                        'name':'capex_drill',
                        'value':-3000000,             # 3 Million dollar of capex
                        'target':'capex',      #The cashflow generated is going to be aCapex in the cashflow model
                        'periods':1,  # repeat the value only one period
                    }
                ]

        }
        p3_cash = Period(**p3cash_dict)

        p3_forecast = p3_cash.generate_forecast()
        p3_cashflow = p3_cash.generate_cashflow()
        
        r = {'index': {0: 0.007974140428903764,
            1: 0.007974140428903764,
            2: 0.007974140428903764,
            3: 0.007974140428903764,
            4: 0.007974140428903764},
            'npv': {0: -1687330.1822611464,
            1: 374678.20306711417,
            2: 2436686.588395375,
            3: 6560703.359051896,
            4: 10684720.129708419},
            'iteration': {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}}
        
        assert_frame_equal(p3_cash.npv([0.1], freq_rate='A', freq_cashflow='M').reset_index(), pd.DataFrame(r))
    
    def test_scenario(self):
        p3_dict = {
            'name':'pdp',
            'dca': {
                'ti':'2021-01-01',
                'di':0.025,
                'freq_di':'M',
                'qi':{'dist':'norm', 'kw':{'loc':1500,'scale':200}}, #[800,1000],
                'b':0,
            },
            'start':'2021-01-01',
            'end':'2027-01-01',
            'freq_output':'A',
            'rate_limit': 300,
            'cashflow_params':[
                {
                    'name':'capex',
                    'value':{
                        'date':['2021-01-01'],
                        'value':[-5000000]
                        },
                    'target':'capex'
                }
            ]
        }

        p4_dict = {
            'name':'pud',
            'dca': {
                'ti':'2022-01-01',
                'di':0.3,
                'freq_di':'A',
                'qi':3000,
                'b':0,
            },
            'start':'2022-01-01',
            'end':'2027-01-01',
            'freq_output':'A',
            'depends':{'period':'pdp'},
            'cashflow_params':[
                {
                    'name':'wo',
                    'value':-500000,
                    'period':1,
                    'target':'capex'
                },
                {
                    'name':'abandon',
                    'value':-300000,
                    'period':-1,
                    'target':'capex'
                },
            ]
        }
        cashflow_params = [
                    {
                        'name':'fix_opex',
                        'value':-5000,
                        'target':'opex',
                    },
                    {
                        'name':'var_opex',
                        'value':-5,
                        'target':'opex',
                        'multiply':'oil_volume',
                    },
                    {
                        'name':'income',
                        'value':60,
                        'target':'income',
                        'multiply':'oil_volume',
                    }]

        s2_dict = {
            'name':'Dependency',
            'periods':[
                p3_dict,
                p4_dict
            ],
            'cashflow_params': cashflow_params,
            'iter':10
        }
        s2 = Scenario(**s2_dict)
        s2_f = s2.generate_forecast(iter=10, seed=21)
        s2_c = s2.generate_cashflow(freq_output='A')
        
        r = {'index': {0: 0.1499999999999999,
            1: 0.1499999999999999,
            2: 0.1499999999999999,
            3: 0.1499999999999999,
            4: 0.1499999999999999,
            5: 0.1499999999999999,
            6: 0.1499999999999999,
            7: 0.1499999999999999,
            8: 0.1499999999999999,
            9: 0.1499999999999999},
            'npv': {0: 118811426.89296526,
            1: 118384137.98344353,
            2: 126701647.33251372,
            3: 142919902.51684964,
            4: 124563398.50653106,
            5: 139933055.11113936,
            6: 117701215.5077205,
            7: 117494128.37086296,
            8: 127324542.79593939,
            9: 119095207.19614205},
            'iteration': {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9}}
        
        assert_frame_equal(s2.npv([0.15], freq_rate='A',freq_cashflow='A').reset_index(),pd.DataFrame(r))
        
    def test_wells(self):
        #First Period First Scenario

        p1a_dict = {
            'name':'pdp',
            'dca': {
                'ti':'2021-01-01',
                'di':0.025,
                'freq_di':'M',
                'qi':1500,
                'b':0,
            },
            'start':'2021-01-01',
            'end':'2040-01-01',
            'freq_output':'A',
            'rate_limit': 300,
            'cashflow_params':[
                {
                    'name':'capex',
                    'value':{
                        'date':['2021-01-01'],
                        'value':[-5000000]
                        },
                    'target':'capex'
                }
            ]
        }

        #Second Period First Scenario

        p2a_dict = {
            'name':'pud',
            'dca': {
                'ti':'2022-01-01',
                'di':0.3,
                'freq_di':'A',
                'qi':3000,
                'b':0,
            },
            'start':'2022-01-01',
            'end':'2040-01-01',
            'freq_output':'A',
            'rate_limit': 100,
            'depends':{'period':'pdp'},
            'cashflow_params':[
                {
                    'name':'wo',
                    'value':-500000,
                    'periods':1,
                    'target':'capex'
                },
                {
                    'name':'abandon',
                    'value':-300000,
                    'periods':-1,
                    'target':'capex'
                },
            ]
        }
        s1_dict = {
            'name':'first',
            'periods':[
                p1a_dict,
                p2a_dict
            ],
        }
        s1 = Scenario(**s1_dict)
        
        #First Period Second Scenario

        p1b_dict = {
            'name':'pdp',
            'dca': {
                'ti':'2021-01-01',
                'di':0.025,
                'freq_di':'M',
                'qi':1500,
                'b':0,
            },
            'start':'2021-01-01',
            'end':'2040-01-01',
            'freq_output':'A',
            'rate_limit': 700,
            'cashflow_params':[
                {
                    'name':'capex',
                    'value':{
                        'date':['2021-01-01'],
                        'value':[-6500000]
                        },
                    'target':'capex'
                }
            ]
        }

        #Second Period Second Escenario

        p2b_dict = {
            'name':'pud',
            'dca': {
                'ti':'2022-01-01',
                'di':0.3,
                'freq_di':'A',
                'qi':3000,
                'b':0,
            },
            'start':'2022-01-01',
            'end':'2040-01-01',
            'freq_output':'A',
            'rate_limit': 100,
            'depends':{'period':'pdp'},
            'cashflow_params':[
                {
                    'name':'wo',
                    'value':-50000,
                    'periods':1,
                    'target':'capex'
                },
                {
                    'name':'abandon',
                    'value':-300000,
                    'periods':-1,
                    'target':'capex'
                },
            ]
        }

        s2_dict = {
            'name':'second',
            'periods':[
                p1b_dict,
                p2b_dict
            ],
        }
        s2 = Scenario(**s2_dict)
        
        well_1 = Well(
            name = 'well_1',
            scenarios = [s1,s2],
            cashflow_params = [
                CashFlowParams(
                    name = 'fix_opex',
                    value = -5000,   # 5 KUSD per well per month
                    freq_value = 'M',
                    target = 'opex',
                ),
                CashFlowParams(
                    name = 'var_opex',
                    value = -10,     # 10 USD per barrel of oil
                    multiply = 'oil_volume',
                    target = 'opex',
                ),
                CashFlowParams(
                    name = 'Sells',
                    value = 50,     # 50 USD per barrel of oil
                    multiply = 'oil_volume',
                    target = 'income',
                    wi = 0.94,
                )
            ]
        )

        well1_forecast = well_1.generate_forecast(freq_output='A')
        well1_cashflow = well_1.generate_cashflow(freq_output='A')
        
        
        r = {'index': {0: 0.10000000000000009, 1: 0.10000000000000009},
            'npv': {0: 173707979.0951442, 1: 410346460.74559057},
            'iteration': {0: 0, 1: 1}}
        
        assert_frame_equal(well_1.npv([0.1], freq_rate='A', freq_cashflow='A').reset_index(),pd.DataFrame(r))
        
    def test_group_wells(self):
        workdir = os.path.dirname(__file__)
        with open(os.path.join(workdir,'data','FDP_example1.yml'),'r') as file:
            lp_dict = yaml.load(file)
        
        lp = model_from_dict(lp_dict)
        
        sc = lp.scenarios_maker()
        
        fwn= lp.generate_forecast(wells=sc[3],freq_output='A',iter=2, seed=21)
        
        cwn= lp.generate_cashflow(wells=sc[3],freq_output='A')
        
        r = np.array([-2.9937035e+07,  1.6341351e+08,  2.7990174e+08,  5.5133251e+08,
            7.0597109e+08,  8.3752614e+08,  8.9858655e+08,  9.3667778e+08,
            9.8614312e+08,  9.8296585e+08])
        
        assert_frame_equal(pd.DataFrame(cwn[0].fcf()['cum_fcf'].values), pd.DataFrame(r))

            