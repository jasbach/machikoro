# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 00:25:01 2020

@author: johna
"""

import numpy as np
import random

import behaviors

def wheat_field(gamestate,active):
    #wheat field activation - each player gains 1 gold per wheat field
    for i in range(1,len(gamestate)):
        gamestate[i][-1] += gamestate[i][0]
    return gamestate

def ranch(gamestate,active):
    #ranch activation - each player gains 1 gold per ranch
    for i in range(1,len(gamestate)):
        gamestate[i][-1] += gamestate[i][1]
    return gamestate

def bakery(gamestate,active):
    #bakery activation - only active player gets 1 gold per bakery
    payout = 1 + gamestate[active][16] #adjusts for shopping mall
    gamestate[active][-1] += gamestate[active][5] * payout
    return gamestate

def cafe(gamestate,active):
    #cafe activation - nonactive take 1 coin from active player per cafe
    for i in [active-1,active-2,active-3]:
        if gamestate[active][-1] == 0: #active player has no money to pay
            break
        if i < 1:
            i += 4
        if i > (len(gamestate)-1): #clause for less than 4 player game
            continue
        payout = 1
        if gamestate[i][16] == 1:
            payout = 2 #if shopping mall exists
        owed = gamestate[i][10] * payout 
        if owed > gamestate[active][-1]:
            owed = gamestate[active][-1]
        gamestate[i][-1] += owed
        gamestate[active][-1] -= owed
    return gamestate

def convenience_store(gamestate,active):
    #convenience store - active player gets 3 coins per
    payout = 3 + gamestate[active][16] #adjusts for shopping mall
    gamestate[active][-1] += gamestate[active][6] * payout
    return gamestate

def forest(gamestate,active):
    #forest - all players get 1 coin per
    for i in range(1,len(gamestate)):
        gamestate[i][-1] += gamestate[i][2]
    return gamestate

def cheese_factory(gamestate,active):
    #cheese factory - 3 coins per ranch
    gamestate[active][-1] += gamestate[active][1] * 3
    return gamestate

def furniture_factory(gamestate,active):
    #furniture factory - 3 coins per forest and mine
    gamestate[active][-1] += (gamestate[active][2] + gamestate[active][3])*3
    return gamestate

def family_restaurant(gamestate,active):
    #family restaurant - nonactive owner gets 2 coins from active roller
    for i in [active-1,active-2,active-3]:
        if gamestate[active][-1] == 0:
            break
        if i < 1:
            i += 4
        if i > (len(gamestate)-1):
            continue
        payout = 2
        if gamestate[i][11] > 0:
            if gamestate[i][16] == 1: #shopping mall clause
                payout = 3
            totalowed = gamestate[i][11] * payout
            if totalowed > gamestate[active][-1]:
                totalowed = gamestate[active][-1]
            gamestate[active][-1] -= totalowed
            gamestate[i][-1] += totalowed
    return gamestate

def fv_market(gamestate,active):
    #fruit and veggie market - 2 coins per wheat field and apple orchard
    gamestate[active][-1] += (gamestate[active][0] + gamestate[active][4]) * 2
    return gamestate

def mine(gamestate,active):
    #mine - 5 coins from bank on any turn per
    for i in range(1,len(gamestate)):
        gamestate[i][-1] += gamestate[i][3] * 5
    return gamestate

def apple_orchard(gamestate,active):
    #apple orchard - 3 coins per, any turn
    for i in range(1,len(gamestate)):
        gamestate[i][-1] += gamestate[i][4] * 3
    return gamestate

def stadium(gamestate,active):
    #stadium - active player takes 2 from all
    if gamestate[active][12] == 1:
        for i in range(1,len(gamestate)):
            if i == active:
                continue
            playercoin = gamestate[i][-1]
            owed = 2
            if playercoin < owed:
                owed = playercoin #take whatever they have left
            gamestate[i][-1] -= owed
            gamestate[active][-1] += owed
    return gamestate

def tv_station(gamestate,active):
    #tv station - take 5 coins from one player
    #(will take from player with most coins)
    if gamestate[active][13] == 1:
        maxoppcoin = 0
        stealfrom = 0
        for i in [active-1,active-2,active-3]:
            if i < 1:
                i += 4
            if i > (len(gamestate)-1): #will pass over if less than 4 players
                continue
            if gamestate[i][-1] > maxoppcoin:
                maxoppcoin = gamestate[i][-1]
                stealfrom = i
        if stealfrom > 0:
            steal = 5
            if gamestate[stealfrom][-1] < steal:
                steal = gamestate[stealfrom][-1]
            gamestate[active][-1] += steal
            gamestate[stealfrom][-1] -= steal
    return gamestate

def business_center(gamestate,active):
    if gamestate[active][14] == 1:
        baselineEV = behaviors.turn_cycle_EV(gamestate,active)
        minEVloss = 999
        giveaway = 0
        EVgains = np.zeros(12)
        trade_complete = False
        for i in range(0,12): #can not trade major establishments or landmarks, so limited to 0-11 index
            if gamestate[active][i] > 0:
                gamestate[active][i] -= 1
                checkEV = behaviors.turn_cycle_EV(gamestate,active) #temporarily subtract one building to assess EV impact
                gamestate[active][i] += 1
                if (baselineEV - checkEV) < minEVloss:
                    minEVloss = checkEV
                    giveaway = i #identifies the outgoing trade piece that costs least EV
            gamestate[active][i] += 1
            checkEV = behaviors.turn_cycle_EV(gamestate,active)
            gamestate[active][i] -= 1
            EVgains[i] = (checkEV - baselineEV) #collects hypothetical EV gains of adding each possible incoming trade piece
        steal_priority = np.flip(np.argsort(EVgains)) #ordered list of building indices in decending order of gains
        for building in steal_priority:
            players = list(range(1,len(gamestate)))
            del players[active-1] #due to 0-indexing
            random.shuffle(players) #randomize - later can add targeting
            for player in players:
                if gamestate[player][building] > 0:
                    gamestate[player][building] -= 1
                    gamestate[active][building] += 1
                    gamestate[player][giveaway] += 1
                    gamestate[active][giveaway] -= 1
                    trade_complete = True
                    break
            if trade_complete == True:
                break
    return gamestate
            
                
        