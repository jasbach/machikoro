# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 16:20:22 2020

@author: johna
"""

import pandas as pd
import random
import numpy as np

import card_effects as cards
import behaviors

#name list for index referencing, gamestate stores array positions in this order
names = ["wheatfield","ranch","forest","mine","appleorchard","bakery","conveniencestore","cheesefactory",
         "furniturefactory","fruitandveggiemarket","cafe","familyrestaurant","stadium","tvstation","businesscenter",
         "trainstation","shoppingmall","amusementpark","radiotower","gold"]
def start_new_game(num_players):
    supply = np.array([6,6,6,6,6,6,6,6,6,6,6,6,4,4,4,4,4,4,4])
    player = np.array([1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,3])
    new_game = [supply]
    for i in range(num_players):
        new_game.append(np.copy(player))
    return new_game

def validate(gamestate,dice):
    for data in gamestate[1:]:
        if np.any(data < 0):
            raise Exception("Negative numbers found in gamestate, most recent dice roll was",dice)
        if np.any(data[12:19] > 1):
            raise Exception("Too many establishments/landmarks!")
        if np.any(data[:12] > 7):
            raise Exception("Too many regular buildings!")
        

def resolve_dice(gamestate,active,dice):
    if dice == 1:
        #wheat field activation - each player gains 1 gold per wheat field
        gamestate = cards.wheat_field(gamestate,active)
    elif dice == 2:
        #ranch activation - each player gains 1 gold per ranch
        gamestate = cards.ranch(gamestate,active)
        #bakery activation - only active player gets 1 gold per bakery
        gamestate = cards.bakery(gamestate,active)
    elif dice == 3:
        #cafe activation - nonactive take 1 coin from active player per cafe
        gamestate = cards.cafe(gamestate,active)
        #bakery activation - only active player gets 1 gold per bakery
        gamestate = cards.bakery(gamestate,active)
    elif dice == 4:
        #convenience store - active player gets 3 coins per
        gamestate = cards.convenience_store(gamestate,active)
    elif dice == 5:
        #forest - all players get 1 coin per
        gamestate = cards.forest(gamestate,active)
    elif dice == 6:
        #stadium - active player takes 2 from all
        gamestate = cards.stadium(gamestate,active)
        #tv station - take 5 coins from one player
        #(will take from player with most coins)
        gamestate = cards.tv_station(gamestate,active)
        #BUSINESS CENTER ACTIVATION - currently optimizes self-EV
        #does not consider any sabotage, randomly selects opponent to force trade with
        gamestate = cards.business_center(gamestate,active)
    elif dice == 7:
        #cheese factory - 3 coins per ranch
        gamestate = cards.cheese_factory(gamestate,active)
    elif dice == 8:
        #furniture factory - 3 coins per forest and mine
        gamestate = cards.furniture_factory(gamestate,active)
    elif dice == 9:
        #family restaurant - nonactive owner gets 2 coins from active roller
        gamestate = cards.family_restaurant(gamestate,active)
        #mine - 5 coins from bank on any turn per
        gamestate = cards.mine(gamestate,active)
    elif dice == 10:
        #family restaurant - nonactive owner gets 2 coins from active roller
        gamestate = cards.family_restaurant(gamestate,active)
        #apple orchard - 3 coins per, any turn
        gamestate = cards.apple_orchard(gamestate,active)
    elif dice == 11 or dice == 12:
        #fruit and veggie market - 2 coins per wheat field and apple orchard
        gamestate = cards.fv_market(gamestate,active)
                
    return gamestate

def roll_dice(gamestate,active):
    num_dice = behaviors.decide_dice(gamestate,active) #determines highest EV, 1 or 2 dice
    dice = random.randint(1,6)
    doubles = False
    if gamestate[active][15] == 1 and num_dice == 2:  #if train station is built, roll two dice
        seconddice = random.randint(1,6)
        if dice == seconddice:
            doubles = True
        dice = dice + seconddice
    return dice, doubles
        
def take_turn(gamestate,active,purchase_weights):
    #print("Active player: Player", active)
    dice, doubles = roll_dice(gamestate,active)
    #print("First dice roll:", dice)
    if gamestate[active][18] == 1: #if radio tower is built, decide whether to reroll
        roll_again = behaviors.roll_again(gamestate,active,dice)
        if roll_again == True:
            dice, doubles = roll_dice(gamestate,active)
            #print("Additional dice roll:",dice)
    gamestate = resolve_dice(gamestate,active,dice)
    validate(gamestate,dice)
    options = behaviors.purchase_options(gamestate,active)
    weighted_options = options * purchase_weights
    if np.sum(weighted_options) > 0: 
        selection = np.argmax(weighted_options * np.random.random_sample(19))
        #print("Selection:",selection,names[selection])
        gamestate = behaviors.resolve_purchase(gamestate,active,selection)
    validate(gamestate,dice)
    return gamestate,doubles
      
if __name__ == "__main__":
    records = pd.DataFrame(columns=names)
    OUTPUTPATH = ""
    NUM_PLAYERS = 4 #number of players
    
    games_played = 0
    even_weights = np.ones(19) #full random purchasing
    player_weights = ["null",even_weights,even_weights,even_weights,even_weights] #account for zero-indexing
    while games_played < 20000:
        gamestate = start_new_game(NUM_PLAYERS)
        winner = False
        active = 1
        turns = 0
        while winner == False:
            turns += 1
            gamestate, doubles = take_turn(gamestate,active,player_weights[active])
            if gamestate[active][17] == 1: #if amusement park is built, take another turn on doubles
                while doubles == True:
                    gamestate, doubles = take_turn(gamestate,active,player_weights[active])
            if np.all(gamestate[active][15:19]) == True:
                winner = True
                break
            active += 1
            if active > NUM_PLAYERS:
                active = 1
        #print("The game has ended after",turns,"turns, player",active,"is the winner.")
        #print(gamestate[active])
        games_played += 1
        winnersboard = pd.Series(gamestate[active],index=records.columns)
        records = records.append(winnersboard,ignore_index=True)
        
    records.to_csv(OUTPUTPATH)
