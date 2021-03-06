# -*- coding: utf-8 -*-
"""
Created on Thu Jun 09 23:35:58 2016

@author: dan
"""

import json

if __name__ == '__main__':
    shared = {'Discount rate': {'dist': 'array', 'val': [0.02, 0.03, 0.02, 0.02, 0.03, 0.03, 0.02, 0.03, 0.03, 0.02, 0.05, 0.02]}, \
        '1 DALY averted is equivalent to increasing ln(consumption) by one unit for one individual for how many years?': {'dist': 'array', 'val': [2.0, 4.0, 4.0, 4.0, 3.0, 4.0, 2.0, 3.0, 3.0, 2.5, 1.6, 2.0]}}
        
    deworming = {'Number of household members that benefit - Deworming': {'dist': 'array', 'val': [2.2, 2.0, 2.2, 2.0, 2.0, 2.0, 2.2, 2.2, 2.2, 1.7, 2.2, 2.2]}, \
        'Proportion of child-years that are as helpful (in terms of developmental effects) as the years in Baird et al.': {'dist': 'array', 'val': [0.5, 0.5, 0.7, 0.75, 0.5, 0.5, 0.65, 0.5, 0.5, 0.5, 0.41, 0.5]}, \
        'Replicability adjustment for deworming': {'dist': 'array', 'val': [0.2, 0.15, 0.1, 0.1, 0.2, 0.5, 0.2, 0.12, 0.17, 0.1, 0.04, 0.23]}, \
        'Adjustment for El Nino': {'dist': 'array', 'val': [0.71, 0.71, 0.71, 0.71, 0.71, 0.54, 0.71, 0.71, 0.71, 0.71, 0.71, 0.71]}, \
        'Duration of long term benefits of deworming (in years)': {'dist': 'array', 'val': [25.0, 25.0, 40.0, 45.0, 40.0, 20.0, 30.0, 30.0, 40.0, 40.0, 30.0, 25.0]}, \
        'Average number of years between deworming and the beginning of long term benefits': {'dist': 'array', 'val': [8.0, 8.0, 5.0, 8.0, 8.0, 5.0, 5.0, 8.0, 8.0, 8.0, 5.0, 5.0]}, \
        'Proportion of dewormed children that benefited from long term gains in Baird et al.': {'dist': 'array', 'val': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.75, 1.0, 1.0, 1.0]}, \
        'Short term health benefits of deworming (DALYs averted per person treated)': {'dist': 'array', 'val': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}, \
        'Treatment effect of deworming on ln(consumption)': {'dist': 'array', 'val': [0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14]}, \
        'Deworming alternate funders adjustment': {'dist': 'array', 'val': [0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.89]}, \
        'Additional years of treatment assigned to Baird\'s treatment group': {'dist': 'array', 'val': [2.41, 2.41, 2.41, 2.41, 2.41, 2.41, 2.41, 2.41, 2.41, 2.41, 2.41, 2.41]}}
            
    dtw = {'Prevalence/intensity adjustment': {'dist': 'array', 'val': [0.15, 0.17, 0.12, 0.12, 0.12, 0.09, 0.21, 0.17, 0.17, 0.09, 0.17, 0.1]}, \
        'Adjustment for benefit varying by treatment frequency': {'dist': 'array', 'val': [0.81, 0.81, 0.77, 0.9, 1.0, 0.81, 0.81, 1.0, 1.0, 1.0, 0.87, 1.0]}, \
        'Leverage (dollars of impact per dollar spent)': {'dist': 'array', 'val': [1.0, 1.0, 1.0, 1.17, 1.0, 1.0, 1.17, 1.0, 1.1, 1.0, 1.0, 1.17]}, \
        'Proportion of deworming going to children': {'dist': 'array', 'val': [1.0, 1.0, 1.0, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, \
        'Cost per person dewormed (per year)': {'dist': 'array', 'val': [0.65, 0.5, 0.53, 0.5, 0.5, 0.8, 0.65, 0.67, 0.5, 0.65, 0.5, 0.53]}}
        
    sci = {'Leverage (dollars of impact per dollar spent)': {'dist': 'array', 'val': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, \
        'Prevalence/intensity adjustment': {'dist': 'array', 'val': [0.18, 0.2, 0.12, 0.09, 0.11, 0.18, 0.17, 0.12, 0.2, 0.1, 0.2, 0.12]}, \
        'Cost per person dewormed (per year)': {'dist': 'array', 'val': [0.67, 0.67, 0.49, 0.67, 0.67, 0.67, 0.84, 0.67, 0.67, 1.19, 0.84, 0.67]}, \
        'Adjustment for benefit varying by treatment frequency': {'dist': 'array', 'val': [1.0, 1.0, 0.77, 0.9, 1.0, 0.81, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, \
        'Proportion of deworming going to children': {'dist': 'array', 'val': [0.85, 0.85, 0.83, 0.85, 0.85, 0.85, 0.85, 0.85, 0.85, 0.85, 0.85, 0.85]}}

    ss = {'Leverage (dollars of impact per dollar spent)': {'dist': 'array', 'val': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, \
        'Prevalence/intensity adjustment': {'dist': 'array', 'val': [0.1, 0.11, 0.09, 0.11, 0.12, 0.2, 0.1, 0.1, 0.12]}, \
        'Cost per person dewormed (per year)': {'dist': 'array', 'val': [0.89, 1.04, 1.04, 0.89, 1.04, 0.89, 1.31, 1.04, 1.31]}, \
        'Adjustment for benefit varying by treatment frequency': {'dist': 'array', 'val': [1.0, 0.77, 0.9, 1.0, 0.81, 1.0, 1.0, 0.94, 1.0]}, \
        'Proportion of deworming going to children': {'dist': 'array', 'val': [0.9, 0.9, 0.9, 0.85, 0.9, 0.8, 0.9, 0.9, 0.9]}}

    gd = {'Percentage of transfers invested - Standard program': {'dist': 'array', 'val': [0.4, 0.39, 0.39, 0.3, 0.39, 0.5, 0.39, 0.39, 0.39, 0.33, 0.39, 0.39]}, \
        'Return on investment - Standard program': {'dist': 'array', 'val': [0.1, 0.15, 0.1, 0.1, 0.1, 0.1, 0.1, 0.12, 0.1, 0.1, 0.1, 0.1]}, \
        'Duration of investment benefits (in years) - Standard program': {'dist': 'array', 'val': [20.0, 15.0, 10.0, 8.0, 20.0, 10.0, 20.0, 10.0, 20.0, 10.0, 10.0, 10.0]}, \
        'Percent of investment returned when benefits end - Standard program': {'dist': 'array', 'val': [0.3, 0.25, 0.0, 0.3, 0.25, 0.25, 0.1, 0.1, 0.1, 0.25, 0.25, 0.3]}, \
        'Transfers as a percentage of total cost - Standard program': {'dist': 'array', 'val': [0.81, 0.82, 0.81, 0.83, 0.81, 0.81, 0.83, 0.81, 0.82, 0.8, 0.81, 0.82]}, \
        'Weight of standard program in overall cost-effectiveness of GiveDirectly': {'dist': 'array', 'val': [1.0, 0.9, 1.0, 0.85, 1.0, 1.0, 1.0, 0.8, 1.0, 1.0, 1.0, 1.0]}}
    
    ubi = {'Percentage of transfers invested - UBI': {'dist': 'array', 'val': [0.26, 0.05, 0.05, 0.26, 0.0, 0.26, 0.1, 0.26, 0.26, 0.1, 0.13, 0.13]}, \
        'Return on investment - UBI': {'dist': 'array', 'val': [0.1, 0.1, 0.1, 0.1, 0.0, 0.1, 0.1, 0.07, 0.1, 0.05, 0.1, 0.1]}, \
        'Expected annual consumption increase (without the UBI program)': {'dist': 'array', 'val': [0.02, 0.03, 0.03, 0.02, 0.02, 0.02, 0.03, 0.02, 0.02, 0.02, 0.01, 0.02]}, \
        'Work participation adjustment': {'dist': 'array', 'val': [1.0, 1.0, 1.0, 1.0, 0.95, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.95]}, \
        'Duration of investment benefits (in years) - UBI': {'dist': 'array', 'val': [5.0, 10.0, 10.0, 6.0, 0.0, 10.0, 10.0, 10.0, 20.0, 10.0, 10.0, 15.0]}, \
        'Percent of investment returned when benefits end - UBI': {'dist': 'array', 'val': [0.25, 0.25, 0.0, 0.3, 0.0, 0.25, 0.25, 0.1, 0.1, 0.25, 0.25, 0.25]}}
    
    smc = {'DALYs averted per death of a 3- to 59-month old child averted - SMC': {'dist': 'array', 'val': [5.0, 12.0, 28.0, 5.5, 22.5, 3.0, 15.0, 15.0, 18.0, 3.5, 3.7, 6.0]}, \
        'Replicability adustment - SMC': {'dist': 'array', 'val': [0.9, 0.9, 0.9, 0.7, 0.9, 0.8, 0.9, 0.9, 0.85, 0.85, 0.9, 0.8]}, \
        'External validity adjustment - SMC': {'dist': 'array', 'val': [0.9, 0.9, 1.0, 0.7, 1.0, 0.8, 0.9, 0.9, 0.85, 0.85, 0.9, 0.85]}, \
        'Alternate funders adjustment - SMC': {'dist': 'array', 'val': [0.78, 0.95, 0.95, 0.95, 0.9, 0.78, 0.9, 0.9, 0.95, 0.95, 0.9, 0.78]}, \
        'Relative value of a year of deworming in Baird to development benefits from 4-months of SMC coverage': {'dist': 'array', 'val': [24.0, 6.0, 2.4, 20.0, 5.0, 2.0, 12.0, 15.0, 5.0, 20.0, 20.0, 20.0]}, \
        'If malaria were eliminated, the fraction of all-cause mortality that would be averted in 3- to 59-month olds in ACCESS-SMC countries': {'dist': 'array', 'val': [0.43, 0.52, 0.4, 0.4, 0.4, 0.52, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]}, \
        'Ratio of the reduction in malaria mortality to the reduction in malaria incidence': {'dist': 'array', 'val': [1.0, 0.8, 0.8, 0.8, 1.0, 0.75, 1.0, 1.0, 1.0, 0.9, 0.87, 1.0]}, \
        'Relative risk for malaria outcome, intention to treat effect': {'dist': 'array', 'val': [0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29]}}
    
    amf = {'Relative value of a year of deworming in Baird to development benefits from a year of ITN coverage': {'dist': 'array', 'val': [20.0, 5.0, 2.0, 20.0, 5.0, 2.0, 10.0, 15.0, 5.0, 20.0, 20.0, 20.0]}, \
        'DALYs averted per death of an under-5 averted - AMF': {'dist': 'array', 'val': [4.0, 8.0, 26.0, 4.0, 15.0, 3.0, 12.0, 13.0, 15.0, 3.0, 3.7, 5.0]}, \
        'Value of an adult malaria death prevented relative to that of a young child': {'dist': 'array', 'val': [4.0, 3.0, 2.0, 6.0, 4.0, 10.0, 3.0, 3.0, 3.5, 5.0, 4.3, 6.0]}, \
        'Relative efficacy of ITNs for reducing adult mortality': {'dist': 'array', 'val': [0.5, 0.4, 0.5, 0.5, 0.5, 0.25, 0.5, 0.5, 0.6, 0.25, 0.05, 0.5]}, \
        'Replicability adjustment - ITNs': {'dist': 'array', 'val': [0.9, 0.95, 0.95, 0.7, 0.95, 0.85, 1.0, 0.9, 0.95, 0.85, 0.87, 0.95]}, \
        'ITN alternative funders adjustment': {'dist': 'array', 'val': [0.78, 0.78, 0.78, 0.6, 0.78, 0.78, 0.78, 0.78, 0.78, 0.78, 0.78, 0.75]}, \
        'External validity adjustment for declines in malaria mortality (to make ITN model consistent with SMC model) - Autocalculated': {'dist': 'array', 'val': [0.83, 1.0, 0.77, 0.77, 0.77, 1.0, 0.77, 0.77, 0.77, 0.77, 0.77, 0.77]}}
    
    # added random iodine parameters for six missing gw staff (from mid-2016 update)
    iodine = {'Cost per person per year': {'dist': 'array', 'val': [0.1, 0.1, 0.08, 0.08, 0.08, 0.08, 0.05, 0.05, 0.1, 0.1]}, \
        'Replicability': {'dist': 'array', 'val': [0.8, 0.7, 0.9, 0.8, 0.8, 0.8, 0.6, 0.6, 0.7, 0.7]}, \
        'External validity': {'dist': 'array', 'val': [0.7, 0.7, 0.7, 0.7]}, \
        'Leverage (dollars of impact per dollars spent)': {'dist': 'array', 'val': [1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0]}, \
        '% of benefit of iodine that lasts for the long term': {'dist': 'array', 'val': [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.0, 1.0, 0.4, 0.4]}, \
        'Probability that GAIN/ICCIDD has an impact': {'dist': 'array', 'val': [0.5, 0.25, 0.5, 0.5, 0.5, 0.5, 0.75, 0.75, 0.25, 0.25]}, \
        '% of children that benefit': {'dist': 'array', 'val': [0.8, 0.8, 0.8, 1.0, 0.8, 0.8, 1.0, 1.0, 0.332, 0.332]}, \
        'Equivalent increase in wages from having iodine throughout childhood': {'dist': 'array', 'val': [0.036, 0.036, 0.036, 0.036, 0.036, 0.036, 0.027, 0.027, 0.054, 0.054]}, \
        'Years of Childhood (for iodine)': {'dist': 'const', 'val': 15.0}, \
        'Percent of population under 15': {'dist': 'const', 'val': 0.431}}    
    
    params = {'Shared': shared, 'Deworming': deworming, 'SCI': sci, 'DtW': dtw, 'SS': ss, 'GD': gd, 'UBI': ubi, 'SMC': smc, 'AMF': amf, 'Iodine': iodine}
    
    with open('params.json', 'w') as fp:
        json.dump(params, fp, indent=4)