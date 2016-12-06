# -*- coding: utf-8 -*-
"""
Created on Thu Jun 09 23:35:58 2016

@author: dan
"""

import json
import scipy.stats as stats
import numpy as np

import matplotlib.pyplot as plt
plt.style.use('ggplot')

import pandas as pd

def get_rvs(p, n):
    if p['dist'] == 'uniform':
        return stats.uniform.rvs(loc=p['loc'], scale=p['scale'], size=n)
    elif p['dist'] == 'array':
        return np.random.choice(p['val'], n)
    else:
        return p['val']

def calc_npv(r, ubi, inputs, n):
    x = np.zeros((ubi['Years Post Transfer'], n))
    y = np.zeros((ubi['Years Post Transfer'], n))
    
    # iterate through years of benefits
    for j in range(1, ubi['Years Post Transfer'] + 1):
        # sum benefits during program
        if(j < r):
            x[j - 1] += ubi['Expected baseline per capita consumption (nominal USD)']* \
                np.power((1.0 + inputs['UBI']['Expected annual consumption increase (without the UBI program)']), float(j))* \
                inputs['UBI']['Work participation adjustment'] + \
                ubi['Annual quantity of transfer money used for immediate consumtion (pre-discounting)']
        # benefits after program
        else:
            x[j - 1] += ubi['Expected baseline per capita consumption (nominal USD)']* \
                np.power((1.0 + inputs['UBI']['Expected annual consumption increase (without the UBI program)']), float(j))
        
        # investments calculations
        for k in range(n):
            if(j < r + inputs['UBI']['Duration of investment benefits (in years) - UBI'][k]):
                x[j - 1][k] += ubi['Annual return for each year of transfer investments (pre-discounting)'][k]* \
                    np.min([j, inputs['UBI']['Duration of investment benefits (in years) - UBI'][k], \
                    r, (inputs['UBI']['Duration of investment benefits (in years) - UBI'][k] + r - j)])
            
                if(j > r):
                    x[j - 1][k] += ubi['Value eventually returned from one years investment (pre-discounting)'][k]
                    
        # log transform and subtact baseline
        y[j - 1] = np.log(x[j - 1])
        y[j - 1] -= np.log(ubi['Expected baseline per capita consumption (nominal USD)']* \
            np.power((1.0 + inputs['UBI']['Expected annual consumption increase (without the UBI program)']), float(j)))
    
    # npv on yearly data
    z = np.zeros(n)
    for i in range(n):
        z[i] = np.npv(inputs['Shared']['Discount rate'][i], y[:, i])
    return z

def calc_deworming(s, deworming, inputs):
    z = {}
    z['Adjusted total benefits per person dewormed in terms of ln(income)'] = \
        inputs[s]['Adjustment for benefit varying by treatment frequency']* \
        (deworming['Adjusted long term benefits per year of treatment (in terms of ln $), assuming income supports household consumption']* \
        inputs[s]['Proportion of deworming going to children']* \
        inputs[s]['Prevalence/intensity adjustment'] + \
        deworming['Short term health benefits of deworing in terms of ln(income)']* \
        inputs[s]['Prevalence/intensity adjustment'])
    z['Proportional increase in consumption per dollar'] = \
        z['Adjusted total benefits per person dewormed in terms of ln(income)']* \
        inputs[s]['Leverage (dollars of impact per dollar spent)']/ \
        inputs[s]['Cost per person dewormed (per year)']
    z['Cost per equivalent life saved'] = \
        inputs['Shared']['1 DALY averted is equivalent to increasing ln(consumption) by one unit for one individual for how many years?']* \
        inputs['AMF']['DALYs averted per death of an under-5 averted - AMF']/ \
        z['Proportional increase in consumption per dollar']
    return z

if __name__ == '__main__':
    n = 100000
    m = 1000.0
    key = 'DALYs per $' + str(m)
    #key = 'Cost per equivalent life saved'
    
    with open('params.json') as fp:    
        params = json.load(fp)
    
    inputs = {}
    for k in params.keys():
        d = {}
        for p in params[k].keys():
            d[p] = get_rvs(params[k][p], n)
        inputs[k] = d

    cash = {}
    cash['Total size of transfer (in nominal USD)'] = 1000.0    
    cash['Average household size'] = 4.7
    cash['Size of transfer per person'] = cash['Total size of transfer (in nominal USD)']/ \
        cash['Average household size']
    cash['Amount invested'] = cash['Size of transfer per person']* \
        inputs['GD']['Percentage of transfers invested - Standard program']
    cash['Initial increase in consumption'] = (1.0 - inputs['GD']['Percentage of transfers invested - Standard program'])* \
        cash['Size of transfer per person']
    cash['Annual increase in consumption made possible by investment returns'] = cash['Amount invested']* \
        inputs['GD']['Return on investment - Standard program']
    cash['Baseline annual consumption per capita (in nominal USD)'] = 285.922288106034
    cash['Initial increase in ln(consumption)'] = np.log(cash['Initial increase in consumption'] + \
        cash['Baseline annual consumption per capita (in nominal USD)']) - \
        np.log(cash['Baseline annual consumption per capita (in nominal USD)'])
    
    cash['Future annual increase in ln(consumption)'] = np.log(cash['Annual increase in consumption made possible by investment returns'] + \
        cash['Baseline annual consumption per capita (in nominal USD)']) - \
        np.log(cash['Baseline annual consumption per capita (in nominal USD)'])
    cash['Present value of future increase in ln(consumption) (excluding the last year)'] = cash['Future annual increase in ln(consumption)']/ \
        (1.0 + inputs['Shared']['Discount rate'])* \
        (1.0 - 1.0/np.power((1.0 + inputs['Shared']['Discount rate']), (inputs['GD']['Duration of investment benefits (in years) - Standard program'] - 1.0)))/ \
        (1.0 - 1.0/(1.0 + inputs['Shared']['Discount rate']))
    cash['Present value of increased ln(consumption) in the last year'] = \
        (np.log(cash['Baseline annual consumption per capita (in nominal USD)'] + \
        cash['Amount invested']* \
        (inputs['GD']['Return on investment - Standard program'] + inputs['GD']['Percent of investment returned when benefits end - Standard program'])) - \
        np.log(cash['Baseline annual consumption per capita (in nominal USD)'])) / \
        np.power((1.0 + inputs['Shared']['Discount rate']), inputs['GD']['Duration of investment benefits (in years) - Standard program'])
    cash['Present value of total future increase in ln(consumption)'] = cash['Present value of future increase in ln(consumption) (excluding the last year)'] + \
        cash['Present value of increased ln(consumption) in the last year']   
    
    cash['Total present value of cash transfer'] = cash['Present value of total future increase in ln(consumption)'] + \
        cash['Initial increase in ln(consumption)']
    cash['Proportional increase in consumption per dollar'] = cash['Total present value of cash transfer']* \
        inputs['GD']['Transfers as a percentage of total cost - Standard program']/ \
        cash['Size of transfer per person']
    
    ubi = {}
    ubi['Annual transfer size per person over 18 (nominal USD)'] = 0.75*365.25
    ubi['Average number of people over 18 in each household'] = 2.395555556
    ubi['Total amount transfered to each household'] = ubi['Annual transfer size per person over 18 (nominal USD)']* \
        ubi['Average number of people over 18 in each household']
    ubi['Household size'] = 4.7
    ubi['Transfer size per person'] = ubi['Total amount transfered to each household']/ubi['Household size']
    ubi['Annual quantity of transfer money used for immediate consumtion (pre-discounting)'] = \
        ubi['Transfer size per person']*(1.0 - inputs['UBI']['Percentage of transfers invested - UBI'])
    ubi['Size of transfer invested each year'] = ubi['Transfer size per person']*inputs['UBI']['Percentage of transfers invested - UBI']
    ubi['Annual return for each year of transfer investments (pre-discounting)'] = \
        ubi['Size of transfer invested each year']*inputs['UBI']['Return on investment - UBI']
    ubi['Value eventually returned from one years investment (pre-discounting)'] = ubi['Size of transfer invested each year'] * \
        inputs['UBI']['Percent of investment returned when benefits end - UBI']
    ubi['Duration of program - Long Term Arm'] = 12.0
    ubi['Duration of program - Short Term Arm'] = 2.0
    ubi['Baseline consumption per capita'] = 285.922288106034
    ubi['Inflation for lack of targeting'] = (0.86-0.5)/0.5*0.3
    ubi['Expected baseline per capita consumption (nominal USD)'] = ubi['Baseline consumption per capita']* \
        (1.0 + ubi['Inflation for lack of targeting'])
    ubi['Adjusted per capita consumption (nominal USD)'] = ubi['Expected baseline per capita consumption (nominal USD)']* \
        inputs['UBI']['Work participation adjustment']
    ubi['Initial benefit (in terms of ln[consumption])'] = np.log(ubi['Annual quantity of transfer money used for immediate consumtion (pre-discounting)'] + \
        ubi['Adjusted per capita consumption (nominal USD)']) - \
        np.log(ubi['Expected baseline per capita consumption (nominal USD)'])

    ubi['Years Post Transfer'] = 100
    ubi['Net present value of benefits beyond initial year of program (in terms of ln[consumption]) - Long Term Arm'] = \
        calc_npv(ubi['Duration of program - Long Term Arm'], ubi, inputs, n)
    ubi['Net present value of entire program (in terms of ln[consumption]) - Long Term Arm'] = \
        ubi['Net present value of benefits beyond initial year of program (in terms of ln[consumption]) - Long Term Arm'] + \
        ubi['Initial benefit (in terms of ln[consumption])']
    ubi['Efficiency of UBI program relative to standard program'] = 0.93
    ubi['Transfers as a percentage of total cost - UBI'] = inputs['GD']['Transfers as a percentage of total cost - Standard program']* \
        ubi['Efficiency of UBI program relative to standard program']
    ubi['Per capita transfer cost over entire program - Long Term Arm'] = ubi['Transfer size per person']* \
        ubi['Duration of program - Long Term Arm']/ubi['Transfers as a percentage of total cost - UBI']
    ubi['Proportional increase in consumption per dollar - Long Term Arm'] = \
        ubi['Net present value of entire program (in terms of ln[consumption]) - Long Term Arm']/ \
        ubi['Per capita transfer cost over entire program - Long Term Arm']
    
    ubi['Net present value of benefits beyond initial year of program (in terms of ln[consumption]) - Short Term Arm'] = \
        calc_npv(ubi['Duration of program - Short Term Arm'], ubi, inputs, n)
    ubi['Net present value of entire program (in terms of ln[consumption]) - Short Term Arm'] = \
        ubi['Net present value of benefits beyond initial year of program (in terms of ln[consumption]) - Short Term Arm'] + \
        ubi['Initial benefit (in terms of ln[consumption])']
    ubi['Per capita transfer cost over entire program - Short Term Arm'] = ubi['Transfer size per person']* \
        ubi['Duration of program - Short Term Arm']/ubi['Transfers as a percentage of total cost - UBI']
    ubi['Proportional increase in consumption per dollar - Short Term Arm'] =  \
        ubi['Net present value of entire program (in terms of ln[consumption]) - Short Term Arm']/ \
        ubi['Per capita transfer cost over entire program - Short Term Arm']
    
    ubi['Percent of transfers going to short term arm'] = 7.9/30.0
    ubi['Percent of transfers going to long term arm'] = 1.0 - ubi['Percent of transfers going to short term arm']
    ubi['Weighted proportion increase in consumption per dollar'] = ubi['Percent of transfers going to short term arm']* \
        ubi['Proportional increase in consumption per dollar - Short Term Arm'] + \
        ubi['Percent of transfers going to long term arm']*ubi['Proportional increase in consumption per dollar - Long Term Arm']
    
    cash['Weight of UBI program in overall cost-effectiveness of GiveDirectly'] = 1.0 - \
        inputs['GD']['Weight of standard program in overall cost-effectiveness of GiveDirectly']
    cash['Weighted proportional increase in consumption per dollar'] = inputs['GD']['Weight of standard program in overall cost-effectiveness of GiveDirectly']* \
        cash['Proportional increase in consumption per dollar'] + ubi['Weighted proportion increase in consumption per dollar']* \
        cash['Weight of UBI program in overall cost-effectiveness of GiveDirectly']
    cash['Cost per equivalent life saved'] = inputs['AMF']['DALYs averted per death of an under-5 averted - AMF']* \
        inputs['Shared']['1 DALY averted is equivalent to increasing ln(consumption) by one unit for one individual for how many years?']/ \
        cash['Weighted proportional increase in consumption per dollar']
    cash['DALYs per $' + str(m)] = m*inputs['AMF']['DALYs averted per death of an under-5 averted - AMF']/ \
        cash['Cost per equivalent life saved']
    
    # long term effects
    deworming = {}
    deworming['Benefit on one year\'s income (discounted back because of delay between deworming and working for income)'] = \
        inputs['Deworming']['Treatment effect of deworming on ln(consumption)']/ \
        np.power((1.0 + inputs['Shared']['Discount rate']), inputs['Deworming']['Average number of years between deworming and the beginning of long term benefits'])
    deworming['Present value of the sum of the lifetime benefits per worker (in terms of Ln(income))'] =  \
        deworming['Benefit on one year\'s income (discounted back because of delay between deworming and working for income)']* \
        (1.0 - 1.0/np.power((1.0 + inputs['Shared']['Discount rate']), inputs['Deworming']['Duration of long term benefits of deworming (in years)']))/ \
        (1.0 - 1.0/(1.0 + inputs['Shared']['Discount rate']))
    deworming['Adjusted long term benefits per year of treatment (in terms of ln $), assuming income supports household consumption (before adjusting for alternate funders)'] = \
        deworming['Present value of the sum of the lifetime benefits per worker (in terms of Ln(income))']* \
        inputs['Deworming']['Number of household members that benefit - Deworming']* \
        inputs['Deworming']['Adjustment for El Nino']* \
        inputs['Deworming']['Proportion of child-years that are as helpful (in terms of developmental effects) as the years in Baird et al.']* \
        inputs['Deworming']['Proportion of dewormed children that benefited from long term gains in Baird et al.']* \
        inputs['Deworming']['Replicability adjustment for deworming']/ \
        inputs['Deworming']['Additional years of treatment assigned to Baird\'s treatment group']
    deworming['Adjusted long term benefits per year of treatment (in terms of ln $), assuming income supports household consumption'] = \
        deworming['Adjusted long term benefits per year of treatment (in terms of ln $), assuming income supports household consumption (before adjusting for alternate funders)']* \
        inputs['Deworming']['Deworming alternate funders adjustment']
    
    # short term effects
    deworming['Short term health benefits of deworing in terms of ln(income)'] = \
        inputs['Shared']['1 DALY averted is equivalent to increasing ln(consumption) by one unit for one individual for how many years?']* \
        inputs['Deworming']['Short term health benefits of deworming (DALYs averted per person treated)']* \
        inputs['Deworming']['Deworming alternate funders adjustment']
    
    # deworming specific charities
    dtw = calc_deworming('DtW', deworming, inputs)
    dtw['DALYs per $' + str(m)] = m*inputs['AMF']['DALYs averted per death of an under-5 averted - AMF']/ \
        dtw['Cost per equivalent life saved']
    sci = calc_deworming('SCI', deworming, inputs)
    sci['DALYs per $' + str(m)] = m*inputs['AMF']['DALYs averted per death of an under-5 averted - AMF']/ \
        sci['Cost per equivalent life saved']
    ss = calc_deworming('SS', deworming, inputs)
    ss['DALYs per $' + str(m)] = m*inputs['AMF']['DALYs averted per death of an under-5 averted - AMF']/ \
        ss['Cost per equivalent life saved']
    
    # bednets
    bednets = {}
    bednets['Deaths averted per protected child under 5 according to Lengeler 2004\'s Summary Effect'] = 5.53/1000.0
    bednets['Under 5 all mortality rate 1995 in the countries where RCT studies were done - Burkina Faso, Gambia, Ghana, and Kenya (per 1000)'] = 123.565
    bednets['Pre-distribution wastage'] = 0.05
    bednets['Under 5 all mortality rate 2015 (per 1000)'] = 63.2938
    bednets['Ratio of mortality rate in 2015 compared to 1995'] = bednets['Under 5 all mortality rate 2015 (per 1000)'] / \
        bednets['Under 5 all mortality rate 1995 in the countries where RCT studies were done - Burkina Faso, Gambia, Ghana, and Kenya (per 1000)']
    bednets['Under 5 all mortality rate 2004 (per 1000)'] = 113
    bednets['Ratio of mortality rate in 2004 compared to 1995'] = bednets['Under 5 all mortality rate 2004 (per 1000)']/ \
        bednets['Under 5 all mortality rate 1995 in the countries where RCT studies were done - Burkina Faso, Gambia, Ghana, and Kenya (per 1000)']
    bednets['Percent of mortality decline between 2004 and 2015 attributable to ITNs'] = 0.25
    bednets['Adjustment for ratio of current child mortality to historical child mortality when RCTs were conducted'] = bednets['Ratio of mortality rate in 2015 compared to 1995'] + \
        (bednets['Ratio of mortality rate in 2004 compared to 1995'] - bednets['Ratio of mortality rate in 2015 compared to 1995'])* \
        bednets['Percent of mortality decline between 2004 and 2015 attributable to ITNs']
    bednets['Efficacy reduction due to insecticide resistance'] = 0.26
    bednets['Percent of country population with IRS coverage (Current inputs based on 2015 Malaria Atlas Project estimates)'] = 0.0826
    bednets['Reduction in ITN efficacy when ITNs are used in conjunction with IRS'] = 0.5
    bednets['Efficacy reduction attributable to IRS'] = bednets['Percent of country population with IRS coverage (Current inputs based on 2015 Malaria Atlas Project estimates)']* \
        bednets['Reduction in ITN efficacy when ITNs are used in conjunction with IRS']
    bednets['Adjustment for differences in malaria burdens between geographic areas'] = 0.86
    bednets['Deaths averted per protected child under 5 - adjusted for today\'s lower rates of child mortality, insecticide resistance, and IRS'] = \
        bednets['Deaths averted per protected child under 5 according to Lengeler 2004\'s Summary Effect']* \
        bednets['Adjustment for ratio of current child mortality to historical child mortality when RCTs were conducted']* \
        bednets['Adjustment for differences in malaria burdens between geographic areas']* \
        (1.0 - bednets['Efficacy reduction due to insecticide resistance'])* \
        (1.0 - bednets['Efficacy reduction attributable to IRS'])
    bednets['Adjustment for net use in AMF distributions relative to net use in Lengeler'] = 0.8
    bednets['Effective deaths averted per under 5 person-year in community-wide distributions'] = \
        bednets['Deaths averted per protected child under 5 - adjusted for today\'s lower rates of child mortality, insecticide resistance, and IRS']* \
        inputs['AMF']['Replicability adjustment - ITNs']* \
        bednets['Adjustment for net use in AMF distributions relative to net use in Lengeler']* \
        inputs['AMF']['External validity adjustment for declines in malaria mortality (to make ITN model consistent with SMC model) - Autocalculated']
    
    bednets['Percent of population under 5 (used for mortality effects and development effects)'] = 0.1740241
    bednets['Percent of population ages 5-14'] = 0.30426622
    
    bednets['Cost per LLIN'] = 4.85
    bednets['Number of LLINs distributed per person in the community'] = 1.0/1.8
    bednets['Cost per person covered in a universal distribution'] = bednets['Cost per LLIN']* \
        bednets['Number of LLINs distributed per person in the community']
    
    bednets['Percent of all individuals owning nets (in absence of a distribution)'] = 0.3
    bednets['Proportion of "extra" nets distributed that are eventually used'] = 0.5
    bednets['Adjustment for unused nets'] = (1.0 - bednets['Proportion of "extra" nets distributed that are eventually used']* \
        bednets['Percent of all individuals owning nets (in absence of a distribution)'])
    bednets['Adjustment for unused nets and alternate funders'] = inputs['AMF']['ITN alternative funders adjustment']* \
        bednets['Adjustment for unused nets']
    
    bednets['Arbitrary donation size'] = 1000000
    bednets['Donation size after costs from pre-distribution wastage'] = bednets['Arbitrary donation size']* \
        (1.0 - bednets['Pre-distribution wastage'])
    bednets['Number of people covered'] = bednets['Donation size after costs from pre-distribution wastage']/ \
        bednets['Cost per person covered in a universal distribution']
    bednets['Under 5\'s covered'] = bednets['Number of people covered']*bednets['Percent of population under 5 (used for mortality effects and development effects)']
    bednets['Children 5-14 covered'] = bednets['Number of people covered']*bednets['Percent of population ages 5-14']
    bednets['Lifespan of an LLIN'] = 2.22
    bednets['Person-years of coverage for under 5\'s'] = bednets['Under 5\'s covered']*bednets['Lifespan of an LLIN']
    bednets['Person-years of coverage for ages 5-14'] = bednets['Children 5-14 covered']*bednets['Lifespan of an LLIN']
    bednets['Person years of protection for under 14\'s'] = bednets['Person-years of coverage for under 5\'s'] + bednets['Person-years of coverage for ages 5-14']
    bednets['Cost per person year of protection for under 14\'s'] = bednets['Arbitrary donation size']/ \
        bednets['Person years of protection for under 14\'s']
    bednets['Cost per person-year of protection, adjusted for insecticide resistance: under-14\'s'] = bednets['Cost per person year of protection for under 14\'s']/ \
        (1.0 - bednets['Efficacy reduction due to insecticide resistance'])
    
    bednets['Total under 5 lives saved by AMF nets and pre-existing nets'] = bednets['Person-years of coverage for under 5\'s']* \
        bednets['Effective deaths averted per under 5 person-year in community-wide distributions']
    bednets['Cost per death averted (before adjusting for alternate funders and pre-existing nets)'] = bednets['Arbitrary donation size']/ \
        bednets['Total under 5 lives saved by AMF nets and pre-existing nets']
    bednets['Under 5 lives saved on the margin'] = bednets['Total under 5 lives saved by AMF nets and pre-existing nets']* \
        bednets['Adjustment for unused nets and alternate funders']
    bednets['Marginal cost per under 5 death averted'] = bednets['Arbitrary donation size']/ \
        bednets['Under 5 lives saved on the margin']
    
    bednets['Proportional increase in consumption per dollar from under 5 deaths averted'] = \
        inputs['AMF']['DALYs averted per death of an under-5 averted - AMF']* \
        inputs['Shared']['1 DALY averted is equivalent to increasing ln(consumption) by one unit for one individual for how many years?']/ \
        bednets['Marginal cost per under 5 death averted']
    
    bednets['Ratio of 5 and over malaria deaths to under 5 malaria deaths'] = 0.49
    bednets['Value of over 5 mortality reduction relative to under 5 mortality reduction'] = \
        inputs['AMF']['Value of an adult malaria death prevented relative to that of a young child']* \
        inputs['AMF']['Relative efficacy of ITNs for reducing adult mortality']* \
        bednets['Ratio of 5 and over malaria deaths to under 5 malaria deaths']
    bednets['Proportional increase in consumption per dollar from 5 and over deaths averted'] = \
        bednets['Proportional increase in consumption per dollar from under 5 deaths averted']* \
        bednets['Value of over 5 mortality reduction relative to under 5 mortality reduction']
    
    bednets['Proportional increase in consumption per dollar from developmental benefits'] = \
        bednets['Adjustment for unused nets and alternate funders']* \
        deworming['Adjusted long term benefits per year of treatment (in terms of ln $), assuming income supports household consumption (before adjusting for alternate funders)']/ \
        inputs['AMF']['Relative value of a year of deworming in Baird to development benefits from a year of ITN coverage']/ \
        bednets['Cost per person-year of protection, adjusted for insecticide resistance: under-14\'s']
    bednets['Proportional increase in consumption per dollar equivalent overall'] = \
        bednets['Proportional increase in consumption per dollar from developmental benefits'] + \
        bednets['Proportional increase in consumption per dollar from 5 and over deaths averted'] + \
        bednets['Proportional increase in consumption per dollar from under 5 deaths averted']
    
    bednets['Cost per equivalent life saved'] = \
        inputs['Shared']['1 DALY averted is equivalent to increasing ln(consumption) by one unit for one individual for how many years?']* \
        inputs['AMF']['DALYs averted per death of an under-5 averted - AMF']/ \
        bednets['Proportional increase in consumption per dollar equivalent overall']
    bednets['DALYs per $' + str(m)] = m*inputs['AMF']['DALYs averted per death of an under-5 averted - AMF']/ \
        bednets['Cost per equivalent life saved']
   
    bednets['Percent of total benefit coming from development effects'] = \
        bednets['Proportional increase in consumption per dollar from developmental benefits']/ \
        bednets['Proportional increase in consumption per dollar equivalent overall']
    bednets['Percent of total benefit coming from adult mortality reduction'] = \
        bednets['Proportional increase in consumption per dollar from 5 and over deaths averted']/ \
        bednets['Proportional increase in consumption per dollar equivalent overall']
    bednets['Percent of total benefit coming from child mortality reduction'] = \
        bednets['Proportional increase in consumption per dollar from under 5 deaths averted']/ \
        bednets['Proportional increase in consumption per dollar equivalent overall']
        
    # smc
    smc = {}
    smc['Total cost for all of ACCESS-SMC in 2015'] = 19441346.4311218
    smc['Total ACCESS-SMC target population in 2015'] = 3423337.0
    smc['Coverage rate: % of targeted children who received at least 1 cycle of treatment (in 2015)'] = 0.8695
    smc['Coverage rate: % of targeted children who received at least 3 cycles of treatment (in 2015)'] = 0.6588
    smc['Coverage rate: % of targeted children who received at least 2 cycles of treatment (in 2015)'] = \
        (smc['Coverage rate: % of targeted children who received at least 1 cycle of treatment (in 2015)'] + \
        smc['Coverage rate: % of targeted children who received at least 3 cycles of treatment (in 2015)'])/2.0
    smc['Coverage rate: % of targeted children who received all 4 cycles of treatment (in 2015)'] = 0.4628
    smc['% of kids who got exactly 1 round'] = smc['Coverage rate: % of targeted children who received at least 1 cycle of treatment (in 2015)'] - \
        smc['Coverage rate: % of targeted children who received at least 2 cycles of treatment (in 2015)']
    smc['% of kids who got exactly 2 rounds'] = smc['Coverage rate: % of targeted children who received at least 2 cycles of treatment (in 2015)'] - \
        smc['Coverage rate: % of targeted children who received at least 3 cycles of treatment (in 2015)']
    smc['% of kids who got exactly 3 rounds'] = smc['Coverage rate: % of targeted children who received at least 3 cycles of treatment (in 2015)'] - \
        smc['Coverage rate: % of targeted children who received all 4 cycles of treatment (in 2015)']
    smc['% of kids who got all 4 rounds'] = smc['Coverage rate: % of targeted children who received all 4 cycles of treatment (in 2015)']
    smc['Adjustment to get from coverage survey figures to actual coverage'] = 1.0
    smc['Overall adjustment for lack of adherence to treatment regimen'] = 0.88
    
    smc['Total person-months of coverage'] = smc['Total ACCESS-SMC target population in 2015']* \
        (1.0*smc['% of kids who got exactly 1 round'] + 2.0*smc['% of kids who got exactly 2 rounds'] + \
        3.0*smc['% of kids who got exactly 3 rounds'] + 4.0*smc['% of kids who got all 4 rounds'])* \
        smc['Adjustment to get from coverage survey figures to actual coverage']* \
        smc['Overall adjustment for lack of adherence to treatment regimen']
    smc['Equivalent 4-cycles of person-months of coverage'] = \
        smc['Total person-months of coverage']/4.0
    smc['Sanity check: Effective coverage rate for 4-cycles of person-months of coverage'] = \
        smc['Equivalent 4-cycles of person-months of coverage']/smc['Total ACCESS-SMC target population in 2015']
    
    smc['Cost per equivalent child treated with 4 cycles'] = smc['Total cost for all of ACCESS-SMC in 2015']/ \
        smc['Equivalent 4-cycles of person-months of coverage']
    smc['Sanity check: Cost per child targeted (i.e., cost for 4 treatments per child if coverage and adherence were 100%)'] = \
        smc['Total cost for all of ACCESS-SMC in 2015']/smc['Total ACCESS-SMC target population in 2015']
    smc['Sanity check: overall adjustment on cost per child targeted'] = smc['Cost per equivalent child treated with 4 cycles']/ \
        smc['Sanity check: Cost per child targeted (i.e., cost for 4 treatments per child if coverage and adherence were 100%)']
    
    smc['Hypothetical cohort'] = 1000.0
    smc['Cost to cover hypothetical cohort with 4 cycles each'] = smc['Cost per equivalent child treated with 4 cycles']*smc['Hypothetical cohort']
    
    smc['2015 3- to 59-month old all-cause deaths expected in cohort, in absence of SMC'] = 15.36
    smc['2015 3- to 59-month old malaria mortality rate (i.e., expected deaths in the specified cohort, in absence of SMC)'] = \
        smc['2015 3- to 59-month old all-cause deaths expected in cohort, in absence of SMC']* \
        inputs['SMC']['If malaria were eliminated, the fraction of all-cause mortality that would be averted in 3- to 59-month olds in ACCESS-SMC countries']
    smc['Fraction of annual malaria burden occurring in SMC period'] = 0.7
    smc['2015 3- to 59-month old malaria deaths during malaria season (in the cohort)'] = \
        smc['2015 3- to 59-month old malaria mortality rate (i.e., expected deaths in the specified cohort, in absence of SMC)']* \
        smc['Fraction of annual malaria burden occurring in SMC period']
    
    smc['Deaths averted in hypothetical cohort (including replicability, external validity, and alternate funders adjustments)'] = \
        smc['2015 3- to 59-month old malaria deaths during malaria season (in the cohort)']* \
        (1.0 - inputs['SMC']['Relative risk for malaria outcome, intention to treat effect'])* \
        inputs['SMC']['Ratio of the reduction in malaria mortality to the reduction in malaria incidence']* \
        inputs['SMC']['Replicability adustment - SMC']* \
        inputs['SMC']['External validity adjustment - SMC']* \
        inputs['SMC']['Alternate funders adjustment - SMC']
    
    smc['Cost per 3- to 59-month old death averted'] = smc['Cost to cover hypothetical cohort with 4 cycles each']/ \
        smc['Deaths averted in hypothetical cohort (including replicability, external validity, and alternate funders adjustments)']
    
    smc['Sanity check: Value of SMC death averted relative to AMF death averted'] = \
        inputs['SMC']['DALYs averted per death of a 3- to 59-month old child averted - SMC']/ \
        inputs['AMF']['DALYs averted per death of an under-5 averted - AMF']
    smc['Proportional increase in consumption per dollar from under 5 deaths averted'] = \
        inputs['SMC']['DALYs averted per death of a 3- to 59-month old child averted - SMC']* \
        inputs['Shared']['1 DALY averted is equivalent to increasing ln(consumption) by one unit for one individual for how many years?']/ \
        smc['Cost per 3- to 59-month old death averted']
    
    smc['Proportional increase in consumption per dollar equivalent from developmental benefits'] = \
        inputs['SMC']['Alternate funders adjustment - SMC']* \
        deworming['Adjusted long term benefits per year of treatment (in terms of ln $), assuming income supports household consumption (before adjusting for alternate funders)']/ \
        inputs['SMC']['Relative value of a year of deworming in Baird to development benefits from 4-months of SMC coverage']/ \
        smc['Cost per equivalent child treated with 4 cycles']
    
    smc['Proportional increase in consumption per dollar equivalent overall'] = smc['Proportional increase in consumption per dollar equivalent from developmental benefits'] + \
        smc['Proportional increase in consumption per dollar from under 5 deaths averted']
    
    smc['Cost per equivalent life saved'] = inputs['AMF']['DALYs averted per death of an under-5 averted - AMF']* \
        inputs['Shared']['1 DALY averted is equivalent to increasing ln(consumption) by one unit for one individual for how many years?']/ \
        smc['Proportional increase in consumption per dollar equivalent overall']
    smc['DALYs per $' + str(m)] = m*inputs['AMF']['DALYs averted per death of an under-5 averted - AMF']/ \
        smc['Cost per equivalent life saved']
    
    smc['Percent of SMC\'s cost-effectiveness coming from development effects'] = smc['Proportional increase in consumption per dollar equivalent from developmental benefits']/ \
        smc['Proportional increase in consumption per dollar equivalent overall']
    
    

    # generate pdfs
    x = np.linspace(0.0, 50.0, 100)
    cash_y, cash_x = np.histogram(cash[key], bins=x, density=True)    
    bednets_y, bednets_x = np.histogram(bednets[key], bins=x, density=True)
    dtw_y, dtw_x = np.histogram(dtw[key], bins=x, density=True)
    sci_y, sci_x = np.histogram(sci[key], bins=x, density=True)
    ss_y, ss_x = np.histogram(ss[key], bins=x, density=True)
    #iodine_y, iodine_x = np.histogram(iodine[key], bins=x, density=True)
    smc_y, smc_x = np.histogram(smc[key], bins=x, density=True)
    
    # generate plots
    plt.figure(0,  figsize=(8, 6))
    plt.plot((cash_x[:-1] + cash_x[1:])/2.0, cash_y, label='cash', color='k')
    plt.plot((bednets_x[:-1] + bednets_x[1:])/2.0, bednets_y, label='bednets', color='b')
    plt.plot((dtw_x[:-1] + dtw_x[1:])/2.0, dtw_y, label='dtw', color='g')
    plt.plot((sci_x[:-1] + sci_x[1:])/2.0, sci_y, label='sci', color='r')
    plt.plot((ss_x[:-1] + ss_x[1:])/2.0, ss_y, label='ss', color='c')
    #plt.plot((iodine_x[:-1] + iodine_x[1:])/2.0, iodine_y, label='iodine', color='m')
    plt.plot((smc_x[:-1] + smc_x[1:])/2.0, smc_y, label='smc', color='m')
    plt.xlim([np.min(x), np.max(x)])
    plt.xlabel(key)
    plt.ylabel('Probability')
    plt.title('PDF of cost effectiveness')
    plt.legend(loc='upper right')
    plt.show()
    
    # export data
    data = np.array([dtw[key], sci[key], ss[key], cash[key], bednets[key], smc[key]]).transpose()
    df = pd.DataFrame(data, columns=['dtw', 'sci', 'ss', 'cash', 'bednets', 'smc'])    
    df.to_pickle('data.pickle')
    
    '''    
    bednets = {}
    bednets['Ratio of mortality rate in 2015 compared to 1995'] = \
        inputs['Bednets']['Under 5 all mortality rate 2015 (per 1000)']/ \
        inputs['Bednets']['Under 5 all mortality rate 1995 in the countries where RCT studies were done -  Burkina Faso, Gambia, Ghana, and Kenya (per 1000)']
    bednets['Ratio of mortality rate in 2004 compared to 1995'] = \
        inputs['Bednets']['Under 5 all mortality rate 2004 (per 1000)']/ \
        inputs['Bednets']['Under 5 all mortality rate 1995 in the countries where RCT studies were done -  Burkina Faso, Gambia, Ghana, and Kenya (per 1000)']
    bednets['Adjustment for ratio of current child mortality to historical child mortality when RCTs were conducted'] = \
        bednets['Ratio of mortality rate in 2015 compared to 1995'] + \
        (bednets['Ratio of mortality rate in 2004 compared to 1995'] - \
        bednets['Ratio of mortality rate in 2015 compared to 1995'])* \
        inputs['Bednets']['Decrease 2004-2015 attributed to ITNs']
    bednets['Deaths averted per protected child under 5 - adjusted for today\'s lower rates of child mortality and insecticide resistance'] = \
        inputs['Bednets']['Deaths averted per protected child under 5']* \
        bednets['Adjustment for ratio of current child mortality to historical child mortality when RCTs were conducted']* \
        (1.0 - inputs['Bednets']['Impact of insecticide resistance'])
    bednets['Pre-existing ITN ownership: children under 5 (GiveWell estimate)'] = \
        inputs['Bednets']['Pre-existing ITN ownership: all (from AMF)']* \
        inputs['Bednets']['Pre-existing ITN ownership: children under 5 (from DHS)']/ \
        inputs['Bednets']['Pre-existing ITN ownership: all']
    bednets['Pre-existing ITN ownership: children aged 5-14 (GiveWell estimate)'] = \
        inputs['Bednets']['Pre-existing ITN ownership: all (from AMF)']* \
        inputs['Bednets']['Pre-existing ITN ownership: children aged 5-14 (from DHS)']/ \
        inputs['Bednets']['Pre-existing ITN ownership: all']
    bednets['Effective pre-existing coverage of children under 5'] = \
        inputs['Bednets']['% of impact of ITNs coming from community-wide effects']* \
        inputs['Bednets']['Pre-existing ITN ownership: all (from AMF)'] + \
        (1.0 - inputs['Bednets']['% of impact of ITNs coming from community-wide effects'])* \
        bednets['Pre-existing ITN ownership: children under 5 (GiveWell estimate)']
    bednets['Effective pre-existing coverage: children aged 5-14'] = \
        inputs['Bednets']['% of impact of ITNs coming from community-wide effects']* \
        inputs['Bednets']['Pre-existing ITN ownership: all (from AMF)'] + \
        (1.0 - inputs['Bednets']['% of impact of ITNs coming from community-wide effects'])* \
        bednets['Pre-existing ITN ownership: children aged 5-14 (GiveWell estimate)']
    bednets['# of person-years of protection for children under 5, per person-year of protection for the community as a whole'] = \
        (1.0 - bednets['Effective pre-existing coverage of children under 5'])* \
        inputs['Bednets']['Percent of population under 5']/ \
        (1.0 - inputs['Bednets']['Pre-existing ITN ownership: all (from AMF)'])
    bednets['# of person-years of protection for children aged 5-14, per person-year of protection for the community as a whole'] = \
        (1.0 - bednets['Effective pre-existing coverage: children aged 5-14'])* \
        inputs['Bednets']['Percent of population aged 5-14']/ \
        (1.0 - inputs['Bednets']['Pre-existing ITN ownership: all (from AMF)'])        
    bednets['Total LLINs distributed'] = \
        (inputs['Bednets']['Total amount spent']/ \
        inputs['Bednets']['Cost per ITN distributed (including delivery)'])* \
        (1.0 - inputs['Bednets']['Wastage'])
    bednets['Total person-years of protection'] = \
        bednets['Total LLINs distributed']* \
        inputs['Bednets']['People covered per LLIN']* \
        inputs['Bednets']['Years of protection per person per LLIN']
    bednets['Total person-years of protection for children under 5'] = \
        bednets['Total person-years of protection']* \
        bednets['# of person-years of protection for children under 5, per person-year of protection for the community as a whole']
    bednets['Total person-years of protection for children aged 5-14'] = \
        bednets['Total person-years of protection']* \
        bednets['# of person-years of protection for children aged 5-14, per person-year of protection for the community as a whole']
    bednets['Total deaths averted for children under 5'] = \
        bednets['Total person-years of protection for children under 5']* \
        bednets['Deaths averted per protected child under 5 - adjusted for today\'s lower rates of child mortality and insecticide resistance']
    bednets['Cost per person-year of protection: under-14\'s only'] = \
        inputs['Bednets']['Total amount spent']/ \
        (bednets['Total person-years of protection for children under 5'] + \
        bednets['Total person-years of protection for children aged 5-14'] )
    bednets['Cost per person-year of protection, adjusted for insecticide resistance: under-14\'s only'] = \
        bednets['Cost per person-year of protection: under-14\'s only']/ \
        (1.0 - inputs['Bednets']['Impact of insecticide resistance'])
    bednets['Cost per death averted'] = \
        inputs['Bednets']['Total amount spent']/ \
        bednets['Total deaths averted for children under 5']
    bednets['Aggregate adjustment to Baird development effect'] = \
        inputs['Deworming']['Adjustment for El Nino']* \
        inputs['Deworming']['Replicability adjustment for  deworming']* \
        inputs['Deworming']['% of years of childhood in which deworming is helpful for development']* \
        inputs['Deworming']['Proportion of dewormed children that benefit from long term gains']/ \
        inputs['Bednets']['Relative value of year of deworming treatment to development benefits from year of bednet coverage']
    bednets['Adjustment to calculations'] = \
        (np.maximum(bednets['Aggregate adjustment to Baird development effect'], inputs['Shared']['Intuitive maximum adjustment']) \
        if inputs['Shared']['Cap adjustment at intuitive maximum'] else bednets['Aggregate adjustment to Baird development effect'])/ \
        bednets['Aggregate adjustment to Baird development effect']
   
    cash = {}
    cash['PPP multiplier'] = 1525.0/inputs['Cash']['Large transfer size, USD']
    cash['Control group household monthly consumption, USD'] = \
        inputs['Cash']['Control group household monthly consumption, USD PPP']/ \
        cash['PPP multiplier']
    cash['Control group per capita monthly consumption, USD'] = \
         cash['Control group household monthly consumption, USD']/ \
         inputs['Cash']['Average family size']
    cash['Control group per capita annual consumption, USD'] = \
        12.0*cash['Control group per capita monthly consumption, USD']
    cash['Size of transfer per person'] = \
        inputs['Cash']['Size of transfer']/ \
        inputs['Cash']['Average family size']
    cash['Control group household monthly consumption, USD'] = \
        inputs['Cash']['Control group household monthly consumption, USD PPP']/ \
        cash['PPP multiplier']
    cash['Control group per capita monthly consumption, USD'] = \
        cash['Control group household monthly consumption, USD']/ \
        inputs['Cash']['Average family size']
    cash['Control group per capita annual consumption, USD'] = \
        12.0*cash['Control group per capita monthly consumption, USD']
    cash['Cash flow from initial spending'] = \
        (1.0 - inputs['Cash']['% of transfers invested'])* \
        cash['Size of transfer per person']
    cash['Initial balance'] = \
        cash['Size of transfer per person'] - cash['Cash flow from initial spending']
    cash['Cash flow from investment return'] = \
        cash['Initial balance']*inputs['Cash']['ROI of cash transfers']
    cash['Sum of benefits from year 1 onward'] = \
        ((1.0 - np.power((1.0 + inputs['Shared']['Discount rate']), -(inputs['Cash']['Duration of benefits of cash transfers (years)'] - 1.0)))/ \
        inputs['Shared']['Discount rate'])*(np.log(cash['Cash flow from investment return'] + cash['Control group per capita annual consumption, USD']) - \
        np.log(cash['Control group per capita annual consumption, USD'])) + \
        (np.log((cash['Initial balance'] + cash['Cash flow from investment return']) + \
        cash['Control group per capita annual consumption, USD']) - np.log(cash['Control group per capita annual consumption, USD']))* \
        (np.power((1.0 + inputs['Shared']['Discount rate']), -inputs['Cash']['Duration of benefits of cash transfers (years)']))
    cash['Present value of the sum of future benefits from cash transfers (ln income)'] = \
        cash['Sum of benefits from year 1 onward']
    cash['Increase in current consumption from spending the transfer (Ln(income))'] = \
        (np.log(cash['Cash flow from initial spending'] + cash['Control group per capita annual consumption, USD']) - 
        np.log(cash['Control group per capita annual consumption, USD']))   
    cash['Present value of net increase in current and future consumption'] = \
        cash['Present value of the sum of future benefits from cash transfers (ln income)'] + \
        cash['Increase in current consumption from spending the transfer (Ln(income))']
    cash['Proportional increase in consumption per dollar'] = \
        cash['Present value of net increase in current and future consumption']/ \
        (cash['Size of transfer per person']/inputs['Cash']['Transfers as a percentage of total cost'])
    cash['Cost per equivalent life saved'] = \
        inputs['Shared']['1 DALY is equivalent to increasing ln(income) by one unit for how many years']* \
        inputs['Shared']['DALYs per death of a young child averted']/ \
        cash['Proportional increase in consumption per dollar']
    cash['Lives saved per $' + str(m)] = m/cash['Cost per equivalent life saved']
    cash['$/DALY'] = cash['Cost per equivalent life saved']/inputs['Shared']['DALYs per death of a young child averted']
    cash['DALYs per $' + str(m)] = m/cash['$/DALY']
    
    deworming = {}
    deworming['Benefit on one year\'s income (discounted back 10 years because of delay between deworming and working for income)'] = \
        inputs['Deworming']['Treatment effect of deworming on Ln(total labor earnings)']/ \
        np.power((1.0 + inputs['Shared']['Discount rate']), inputs['Deworming']['Average number of years between deworming and the beginning of long term benefits - also used for iodine'])
    deworming['Present value of the sum of the lifetime benefits per worker (in terms of Ln(income))'] = \
        deworming['Benefit on one year\'s income (discounted back 10 years because of delay between deworming and working for income)']* \
        (1.0 - 1.0/np.power((1.0 + inputs['Shared']['Discount rate']), inputs['Deworming']['Duration of long term benefits of deworming (years) - also used for iodine']))/ \
        (1.0 - 1.0/(1.0 + inputs['Shared']['Discount rate']))
    deworming['Adjusted long term benefits per year of treatment (in terms of ln $), assuming income supports household consumption'] = \
        deworming['Present value of the sum of the lifetime benefits per worker (in terms of Ln(income))']* \
        inputs['Deworming']['Number of household members that benefit']* \
        inputs['Deworming']['Adjustment for El Nino']* \
        inputs['Deworming']['% of years of childhood in which deworming is helpful for development']* \
        inputs['Deworming']['Proportion of dewormed children that benefit from long term gains']* \
        inputs['Deworming']['Replicability adjustment for  deworming']/ \
        inputs['Deworming']['Years of deworming treatment in Miguel and Kremer 2004']
    deworming['Short term health benefits (deworming only) in terms of Ln(income)'] = \
        inputs['Deworming']['Short term health benefits of deworming (DALYs per person treated)']* \
        inputs['Shared']['1 DALY is equivalent to increasing ln(income) by one unit for how many years']
    
    dtw = {}
    dtw['Aggregate adjustment to Baird development effect'] = \
        inputs['Deworming']['Adjustment for El Nino']* \
        inputs['Deworming']['Replicability adjustment for  deworming']* \
        inputs['Deworming']['% of years of childhood in which deworming is helpful for development']* \
        inputs['Deworming']['Proportion of dewormed children that benefit from long term gains']* \
        inputs['DtW']['Prevalence/ intensity adjustment']
    dtw['Adjustment to calculations'] = \
        (np.maximum(dtw['Aggregate adjustment to Baird development effect'], inputs['Shared']['Intuitive maximum adjustment']) \
        if inputs['Shared']['Cap adjustment at intuitive maximum'] else dtw['Aggregate adjustment to Baird development effect'])/ \
        dtw['Aggregate adjustment to Baird development effect']
    dtw['Adjusted total benefits, per person dewormed (Ln(income))'] = \
        inputs['DtW']['Adjustment for benefit varying by treatment frequency'] * \
        (deworming['Adjusted long term benefits per year of treatment (in terms of ln $), assuming income supports household consumption']* \
        dtw['Adjustment to calculations']* \
        inputs['DtW']['Proportion of deworming going to children']* \
        inputs['DtW']['Prevalence/ intensity adjustment'] + \
        deworming['Short term health benefits (deworming only) in terms of Ln(income)']* \
        inputs['DtW']['Prevalence/ intensity adjustment'])
    dtw['Proportional increase in consumption per dollar'] = \
        dtw['Adjusted total benefits, per person dewormed (Ln(income))']/ \
        (inputs['DtW']['Cost per person dewormed']/ \
        inputs['DtW']['Leverage (dollar of impact per dollar spent)'])
    dtw['Cost per equivalent life saved'] = \
        inputs['Shared']['1 DALY is equivalent to increasing ln(income) by one unit for how many years']* \
        inputs['Shared']['DALYs per death of a young child averted']/ \
        dtw['Proportional increase in consumption per dollar']
    dtw['X as cost effective as Cash'] = \
        dtw['Proportional increase in consumption per dollar']/cash['Proportional increase in consumption per dollar']
    #dtw_p = stats.lognorm.fit(dtw['X as cost effective as Cash'])
    #dtw_d = stats.lognorm(*dtw_p[:-2], loc=dtw_p[-2], scale=dtw_p[-1])
    dtw['Lives saved per $' + str(m)] = m/dtw['Cost per equivalent life saved']
    dtw['$/DALY'] = dtw['Cost per equivalent life saved']/inputs['Shared']['DALYs per death of a young child averted']
    dtw['DALYs per $' + str(m)] = m/dtw['$/DALY']    
    
    sci = {}
    sci['Aggregate adjustment to Baird development effect'] = \
        inputs['Deworming']['Adjustment for El Nino']* \
        inputs['Deworming']['Replicability adjustment for  deworming']* \
        inputs['Deworming']['% of years of childhood in which deworming is helpful for development']* \
        inputs['Deworming']['Proportion of dewormed children that benefit from long term gains']* \
        inputs['SCI']['Prevalence/ intensity adjustment']
    sci['Adjustment to calculations'] = \
        (np.maximum(sci['Aggregate adjustment to Baird development effect'], inputs['Shared']['Intuitive maximum adjustment']) \
        if inputs['Shared']['Cap adjustment at intuitive maximum'] else sci['Aggregate adjustment to Baird development effect'])/ \
        sci['Aggregate adjustment to Baird development effect']
    sci['Adjusted total benefits, per person dewormed (Ln(income))'] = \
        inputs['SCI']['Adjustment for benefit varying by treatment frequency'] * \
        (deworming['Adjusted long term benefits per year of treatment (in terms of ln $), assuming income supports household consumption']* \
        sci['Adjustment to calculations']* \
        inputs['SCI']['Proportion of deworming going to children']* \
        inputs['SCI']['Prevalence/ intensity adjustment'] + \
        deworming['Short term health benefits (deworming only) in terms of Ln(income)']* \
        inputs['SCI']['Prevalence/ intensity adjustment'])
    sci['Proportional increase in consumption per dollar'] = \
        sci['Adjusted total benefits, per person dewormed (Ln(income))']/ \
        (inputs['SCI']['Cost per person dewormed']/ \
        inputs['SCI']['Leverage (dollar of impact per dollar spent)'])
    sci['Cost per equivalent life saved'] = \
        inputs['Shared']['1 DALY is equivalent to increasing ln(income) by one unit for how many years']* \
        inputs['Shared']['DALYs per death of a young child averted']/ \
        sci['Proportional increase in consumption per dollar']
    sci['X as cost effective as Cash'] = \
        sci['Proportional increase in consumption per dollar']/cash['Proportional increase in consumption per dollar']
    #sci_p = stats.lognorm.fit(sci['X as cost effective as Cash'])
    #sci_d = stats.lognorm(*sci_p[:-2], loc=sci_p[-2], scale=sci_p[-1])
    sci['Lives saved per $' + str(m)] = m/sci['Cost per equivalent life saved']   
    sci['$/DALY'] = sci['Cost per equivalent life saved']/inputs['Shared']['DALYs per death of a young child averted']
    sci['DALYs per $' + str(m)] = m/sci['$/DALY']       
     
    bednets['Proportional increase in consumption per dollar'] = \
        inputs['Bednets']['Alternative funders adjustment']* \
        ((1.0/bednets['Cost per person-year of protection, adjusted for insecticide resistance: under-14\'s only'])* \
        (1.0/inputs['Bednets']['Relative value of year of deworming treatment to development benefits from year of bednet coverage'])* \
        deworming['Adjusted long term benefits per year of treatment (in terms of ln $), assuming income supports household consumption'] + \
        (1.0/bednets['Cost per death averted'])* \
        inputs['Shared']['DALYs per death of a young child averted']* \
        inputs['Shared']['1 DALY is equivalent to increasing ln(income) by one unit for how many years'])
    bednets['Cost per equivalent life saved'] = \
        inputs['Shared']['1 DALY is equivalent to increasing ln(income) by one unit for how many years']* \
        inputs['Shared']['DALYs per death of a young child averted']/ \
        bednets['Proportional increase in consumption per dollar']
    bednets['X as cost effective as Cash'] = \
        bednets['Proportional increase in consumption per dollar']/cash['Proportional increase in consumption per dollar']
    #bednets_p = stats.lognorm.fit(bednets['X as cost effective as Cash'])
    #bednets_d = stats.lognorm(*bednets_p[:-2], loc=bednets_p[-2], scale=bednets_p[-1])
    bednets['Lives saved per $' + str(m)] = m/bednets['Cost per equivalent life saved']
    bednets['$/DALY'] = bednets['Cost per equivalent life saved']/inputs['Shared']['DALYs per death of a young child averted']
    bednets['DALYs per $' + str(m)] = m/bednets['$/DALY']        
    
    iodine = {}
    iodine['Benefit on one year\'s income (discounted back 10 years because of delay between deworming and working for income)'] = \
        (inputs['Iodine']['% of benefit of iodine that lasts for the long term']* \
        inputs['Iodine']['Equivalent increase in wages from having iodine throughout childhood'])/ \
        np.power((1.0 + inputs['Shared']['Discount rate']),  inputs['Deworming']['Average number of years between deworming and the beginning of long term benefits - also used for iodine'])
    iodine['Present value of the sum of the lifetime benefits per worker (in terms of Ln(income))'] = \
        iodine['Benefit on one year\'s income (discounted back 10 years because of delay between deworming and working for income)']* \
        (1.0 - 1.0/np.power((1.0 + inputs['Shared']['Discount rate']), inputs['Deworming']['Duration of long term benefits of deworming (years) - also used for iodine']))/ \
        (1.0 - 1.0/(1.0 + inputs['Shared']['Discount rate']))
    iodine['Adjusted long term benefits per year of treatment (in terms of ln $), assuming income supports household consumption'] = \
        iodine['Present value of the sum of the lifetime benefits per worker (in terms of Ln(income))']* \
        inputs['Iodine']['Replicability']*inputs['Iodine']['External validity']* \
        inputs['Iodine']['% of children that benefit']* \
        (inputs['Iodine']['Percent of population under 15']/inputs['Iodine']['Years of Childhood (for iodine)'])* \
        inputs['Deworming']['Number of household members that benefit']
    iodine['Short term health benefits (deworming only) in terms of Ln(income)'] = 0.0
    iodine['Adjusted total benefits, per person dewormed (Ln(income))'] = \
        iodine['Adjusted long term benefits per year of treatment (in terms of ln $), assuming income supports household consumption']
    iodine['Proportional increase in consumption per dollar'] = \
        inputs['Iodine']['Probability that GAIN/ICCIDD has an impact']* \
        iodine['Adjusted total benefits, per person dewormed (Ln(income))']/ \
        (inputs['Iodine']['Cost per person per year']/inputs['Iodine']['Leverage (dollars of impact per dollars spent)'])
    iodine['X as cost effective as Cash'] = \
        iodine['Proportional increase in consumption per dollar']/cash['Proportional increase in consumption per dollar']
    iodine['Cost per equivalent life saved'] = \
        inputs['Shared']['1 DALY is equivalent to increasing ln(income) by one unit for how many years']* \
        inputs['Shared']['DALYs per death of a young child averted']/ \
        iodine['Proportional increase in consumption per dollar']
    iodine['Lives saved per $' + str(m)] = m/iodine['Cost per equivalent life saved']
    iodine['$/DALY'] = iodine['Cost per equivalent life saved']/inputs['Shared']['DALYs per death of a young child averted']
    iodine['DALYs per $' + str(m)] = m/iodine['$/DALY']        
    '''
    
    '''
    x = np.linspace(0.0, 50.0, 100)
    #x = np.logspace(0.0, np.log10(50.0), 50) - 1.0
    #cash_y, cash_x = np.histogram(cash['Proportional increase in consumption per dollar']/np.median(cash['Proportional increase in consumption per dollar']), bins=x, density=True)
    cash_y, cash_x = np.histogram(cash[key], bins=x, density=True)    
    bednets_y, bednets_x = np.histogram(bednets[key], bins=x, density=True)
    dtw_y, dtw_x = np.histogram(dtw[key], bins=x, density=True)
    sci_y, sci_x = np.histogram(sci[key], bins=x, density=True)
    iodine_y, iodine_x = np.histogram(iodine[key], bins=x, density=True)
    
    plt.figure(0,  figsize=(8, 6))
    plt.plot((cash_x[:-1] + cash_x[1:])/2.0, cash_y, label='cash', color='k')
    plt.plot((bednets_x[:-1] + bednets_x[1:])/2.0, bednets_y, label='bednets', color='b')
    plt.plot((dtw_x[:-1] + dtw_x[1:])/2.0, dtw_y, label='dtw', color='g')
    plt.plot((sci_x[:-1] + sci_x[1:])/2.0, sci_y, label='sci', color='r')
    plt.plot((iodine_x[:-1] + iodine_x[1:])/2.0, iodine_y, label='iodine', color='m')
    plt.xlim([np.min(x), np.max(x)])
    plt.xlabel(key)
    plt.ylabel('Probability')
    plt.title('PDF of cost effectiveness')
    plt.legend(loc='upper right')
    plt.show()
    
    #data = np.array([bednets[key], dtw[key], sci[key], iodine[key]]).transpose()
    data = np.array([bednets[key], dtw[key], sci[key], iodine[key], cash[key]]).transpose()
    #data = np.array([bednets[key], dtw[key], sci[key]]).transpose()
    #data = np.log(np.array([bednets[key], dtw[key], sci[key]])).transpose()
    df = pd.DataFrame(data, columns=['bednets', 'dtw', 'sci', 'iodine', 'cash'])
    #df = pd.DataFrame(data, columns=['bednets', 'dtw', 'sci', 'iodine'])
    #df = pd.DataFrame(data, columns=['bednets', 'dtw', 'sci'])
    df.to_pickle('data.pickle')
    
    #x_max = np.max([bednets_d.ppf(0.9), dtw_d.ppf(0.9), sci_d.ppf(0.9)])
    #x = np.linspace(0, x_max, 100)
    #plt.plot(x, bednets_d.pdf(x), label='bednets', color='b')
    #plt.plot(x, dtw_d.pdf(x), label='dtw', color='g')
    #plt.plot(x, sci_d.pdf(x), label='sci', color='r')
    #plt.hist(sci_d.rvs(n), label='fit', bins=x, color='r')
    #plt.hist(sci['X as cost effective as Cash'], label='data', bins=x, color='w')
    #plt.xlim([0, x_max])
    #plt.legend(loc='upper right')
    #plt.show()
    '''  