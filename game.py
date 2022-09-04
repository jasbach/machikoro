import random

import pandas as pd
import numpy as np


import dice


class Game():

    def __init__(self,players=4):
        """
        Initialize a fresh game state
        """
        assert 1 < players < 5
        self.supply = Supply()
        self.players = [Player() for n in range(players)]
        self.supply.gold -= 3*players
        self.active_player = random.randint(1,players)
        
    def copy(self):
        # utility function used for hypotheticals in simple logic structures
        newgame = Game()
        for attr in vars(self).keys():
            if attr.startswith("_"):
                continue
            setattr(newgame,attr,getattr(self,attr))
        return newgame
    
    def roll(self):
        two_dice = False
        doubles = False
        if self.players[self.active_player].train_station:
            # does not call decisionmaking unless train station is built
            two_dice = self.players[self.active_player].logic.roll_two(
                self,self.active_player
                )
        result = random.randint(1,6)
        if two_dice is True:
            second_die = random.randint(1,6)
            if second_die == result:
                doubles = True
            result += second_die
            
        # ===== DECISION POINT =====
        # decide whether to reroll if radio tower is built
        return result, doubles
    
    def take_turn(self):
        """
        Three phases to every turn:
            1. Roll Dice
            2. Earn Income
            3. Build
            
        Dice rolling occurs via the roll() method of the game, which includes
        decision-making hooks for landmarks 
        """
        while True:
            dice_result, doubles = self.roll()
            dice.process_roll(self,dice_result,self.active_player)
            # ===== DECISION POINT =====
            # TODO - build
            if doubles and self.players[self.active_player].amusement_park:
                continue
            else:
                break
        # advance active player indicator
        self.active_player += 1
        self.active_player %= len(self.players)
        
        
class Player():
    def __init__(self):
        self.wheat_field = 1
        self.ranch = 1
        for building in ['bakery',
                         'cafe',
                         'convenience_store',
                         'forest',
                         'cheese_factory',
                         'furniture_factory',
                         'mine',
                         'apple_orchard',
                         'farmers_market',
                         'tv_station',
                         'business_center',
                         'stadium',
                         'amusement_park',
                         'radio_tower',
                         'shopping_mall',
                         'train_station']:
            setattr(self,building,0)
        self.gold = 3

        
            
class Supply():
    def __init__(self):
        for building in ['wheat_field',
                         'ranch',
                         'bakery',
                         'cafe',
                         'convenience_store',
                         'forest',
                         'cheese_factory',
                         'furniture_factory',
                         'mine',
                         'apple_orchard',
                         'farmers_market']:
            setattr(self,building,6)
        for maj_building in ['tv_station',
                             'business_center',
                             'stadium']:
            setattr(self,maj_building,4)
        self.gold = 42 + 24*5 + 12*10