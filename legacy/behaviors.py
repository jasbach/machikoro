# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 01:00:25 2020

@author: johna
"""

import numpy as np
import random
    
def active_onedice_EV(gamestate,active):
    num_players = len(gamestate) - 1
    
    EV = 0
    EV += gamestate[active][0] * 1/6 #wheat field
    EV += gamestate[active][1] * 1/6 #ranch
    EV += gamestate[active][2] * 1/6 #forest
    #no value for mines
    #no value for apple orchards
    EV += gamestate[active][5] * (1+gamestate[active][16]) * 2/6 #bakery, accounts for shopping mall
    EV += gamestate[active][6] * (3+gamestate[active][16]) * 1/6 #convenience store, accounts for shopping mall
    #no value for cheese factory
    #no value for furniture factory
    #no value for fruit & veggie market
    #no value for cafe
    #no value for fam restaurant
    EV += gamestate[active][12] * 0.333 * num_players - 0.333 #stadium
    EV += gamestate[active][13] * 5 * 1/6 #tvstation
    #tough to quantify business center
    return EV

def inactive_onedice_EV(gamestate,inactive):
    EV = 0
    EV += gamestate[inactive][0] * 1/6 #wheat field
    EV += gamestate[inactive][1] * 1/6 #ranch
    EV += gamestate[inactive][2] * 1/6 #forest
    #no value for mines
    #no value for apple orchards
    #no value for green cards
    EV += gamestate[inactive][10] * (1+gamestate[inactive][16]) * 1/6 #cafe, accounts for shopping mall
    #no value for family restaurant
    #no value for establishments/landmarks
    return EV

def active_twodice_EV(gamestate,active):
    num_players = len(gamestate) - 1
    
    EV = 0
    EV += gamestate[active][0] * (2*3/36*gamestate[active][9]) #wheat field
    EV += gamestate[active][1] * (1/36+gamestate[active][7]*3*6/36) #ranch, accounts for cheese fac
    EV += gamestate[active][2] * (4/36 + 3*5/36*gamestate[active][8]) #forest, accounts for furniture fac
    EV += gamestate[active][3] * (5*4/36 + 3*5/36*gamestate[active][8]) #mine, accounts for furniture fac
    EV += gamestate[active][4] * (3*3/36 + 2*3/36*gamestate[active][9]) #apple orchard
    EV += gamestate[active][5] * (1+gamestate[active][16]) * 3/36 #bakery, accounts for shopping mall
    EV += gamestate[active][6] * (3+gamestate[active][16]) * 3/36 #convenience store, accounts for shopping mall
    EV += gamestate[active][7] * (3*6/36*gamestate[active][1]) #cheese factory
    EV += gamestate[active][8] * (3*5/36*np.sum(gamestate[active][2:4])) #furniture factory
    EV += gamestate[active][9] * (2*3/36*(gamestate[active][0]+gamestate[active][4])) #fruit and veggie
    #no value for cafe
    #no value for fam restaurant
    EV += gamestate[active][12] * (2*5/36*(num_players - 1))
    EV += gamestate[active][13] * (5*5/36)
    
    #how to calculate amusement park - take another turn if doubles?
    #likely need a tool that returns total payout of each dice roll
    return EV

def inactive_twodice_EV(gamestate,inactive):
    EV = 0
    #no value for wheat field
    EV += gamestate[inactive][1] * 1/36 #ranch
    EV += gamestate[inactive][2] * 4/36 #forest
    EV += gamestate[inactive][3] * 5 * 4/36 #mine
    EV += gamestate[inactive][4] * 3 * 3/36 #apple orchard
    #no value for green cards
    EV += gamestate[inactive][10] * (1+gamestate[inactive][16]) * 2/36 #cafe, accounts for shopping mall
    EV += gamestate[inactive][11] * (2+gamestate[inactive][16]) * 7/36 #family restaurant, accounts for shopping mall
    #no value for establishments/landmarks
    return EV

def decide_dice(gamestate,active):
    EV1 = active_onedice_EV(gamestate,active)
    EV2 = active_twodice_EV(gamestate,active)
    
    if EV1 > EV2:
        roll = 1
    else:
        roll = 2
    return roll

def turn_cycle_EV(gamestate,active):
    totalEV = 0
    for i in range(1,len(gamestate)):
        expected_roll = decide_dice(gamestate,i) #determine what player i will roll on their turn
        if i == active: #evaluate for own roll
            if expected_roll == 1:
                totalEV += active_onedice_EV(gamestate,active)
            elif expected_roll == 2:
                totalEV += active_twodice_EV(gamestate,active)
        else: #evaluate for other players' rolls
            if expected_roll == 1:
                totalEV += inactive_onedice_EV(gamestate,active)
            elif expected_roll == 2:
                totalEV += inactive_twodice_EV(gamestate,active)
    #totalEV now represents the expected return for a full turn cycle
    #does not consider any additional buildings built during turn cycle
    return totalEV

def roll_payout(gamestate,active,roll):
    if roll == 1:
        return gamestate[active][0] #wheat field
    elif roll == 2:
        return (gamestate[active][1] + gamestate[active][5]) #ranch and bakery
    elif roll == 3:
        return (gamestate[active][5]) #bakery (ignore cafe)
    elif roll == 4:
        return (gamestate[active][6]*3) #convenience store
    elif roll == 5:
        return gamestate[active][2] #forest
    elif roll == 6:
        #still haven't quantified business center
        payout = gamestate[active][12] * 2 * (len(gamestate)-1) + gamestate[active][13] * 5
        return payout
    elif roll == 7:
        return (gamestate[active][7]*3*gamestate[active][1]) #cheese factory
    elif roll == 8:
        return (gamestate[active][8]*3*np.sum(gamestate[active][2:4])) #furniture factory
    elif roll == 9:
        return (gamestate[active][3]*5) #mine
    elif roll == 10:
        return (gamestate[active][4]*3) #apple orchard
    elif roll == 11 or roll == 12:
        payout = gamestate[active][9] * (2*(gamestate[active][0]+gamestate[active][4]))
        return payout

def purchase_options(gamestate,active):
    costs = np.array([1,1,3,6,3,1,2,5,3,2,2,3,6,7,8,4,10,16,22]) #coin cost of each building
    coin = gamestate[active][-1]
    supply = gamestate[0]
    options = np.where(costs<=coin,1,0) * np.where(supply>0,1,0) #checks affordability and availability
    options[12:19] = options[12:19] * np.where(gamestate[active][12:19]==0,1,0) #ensures no double-purchase of landmarks
    #result is array with either 0 or 1 for each building - 0 if not viable option, 1 if viable
    return options    

def resolve_purchase(gamestate,active,selection):
    costs = np.array([1,1,3,6,3,1,2,5,3,2,2,3,6,7,8,4,10,16,22])
    gamestate[active][selection] += 1
    gamestate[0][selection] -= 1
    gamestate[active][-1] -= costs[selection]
    return gamestate

def roll_again(gamestate,active,dice):
    num_dice = decide_dice(gamestate,active)
    orig_payout = roll_payout(gamestate,active,dice)
    if num_dice == 1:
        EV = active_onedice_EV(gamestate,active)
    elif num_dice == 2:
        EV = active_twodice_EV(gamestate,active)
    if orig_payout >= EV:
        reroll = False
    else:
        reroll = True
    return reroll
    