# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 22:37:15 2022

@author: johna

Places that involve decision-making:
    1. Build phase
    2. One dice or two (with train station)
    3. TV Station activation
    4. Business Center activation
    5. Re-roll (with radio tower)
    
Different decisionmaking paradigms will be defined as classes.

Each class has a function for each decision point, named:
    tv_station()
    roll_two()
    build()
    business_center()
    reroll()
    
All decision functions will take (game, ap) as arguments for compatibility.
"""

import random

COSTS = {'wheat_field':1,
         'ranch':1,
         'bakery':1,
         'cafe':2,
         'convenience_store':2,
         'forest':3,
         'cheese_factory':5,
         'furniture_factory':3,
         'mine':6,
         'apple_orchard':3,
         'family_restaurant':3,
         'farmers_market':2,
         'stadium':6,
         'tv_station':7,
         'business_center':8,
         'amusement_park':16,
         'radio_tower':22,
         'shopping_mall':10,
         'train_station':4}

ONEDICE_ODDS = {1: 1/6,
                2: 1/6,
                3: 1/6,
                4: 1/6,
                5: 1/6,
                6: 1/6,
                7: 0,
                8: 0,
                9: 0,
                10: 0,
                11: 0,
                12: 0}

TWODICE_ODDS = {1: 0,
                2: 1/36,
                3: 2/36,
                4: 3/36,
                5: 4/36,
                6: 5/36,
                7: 6/36,
                8: 5/36,
                9: 4/36,
                10: 3/36,
                11: 2/36,
                12: 1/36}

def who_has_most(game,ap,thing):
    most = 0
    take_from = 0
    no_one = True
    for i, player in enumerate(game.players):
        if i == ap:
            continue
        if getattr(player,thing) == 0:
            continue
        no_one = False
        if getattr(player,thing) > most:
            take_from = i
            most = getattr(player,thing)
        elif getattr(player,thing) == most:
            if isinstance(take_from,list):
                take_from.append(i)
            else:
                take_from = [take_from, i]
    if no_one is True:
        return None
    return take_from

def turn_cycle_EV(game,ap):
    self_doubles = (game.players[ap].train_station == 1)
    if self_doubles:
        self_odds = ONEDICE_ODDS
    else:
        self_odds = TWODICE_ODDS
        
    other_doubles = sum(
        [player.train_station for player in game.players]
        )
    other_singles = len(game.players) - other_doubles
    if self_doubles:
        other_doubles -= 1
    
    cum_other_odds = {}
    for result in self_odds.keys():
        cum_other_odds[result] = (
            other_singles * ONEDICE_ODDS[result] +
            other_doubles * TWODICE_ODDS[result]
            )
    
    # 
    enemycafes = sum([player.cafe for player in game.players])
    enemycafes -= game.players[ap].cafes
    enemyrestrnt = sum(
        [player.family_restaurant for player in game.players]
        )
    enemyrestrnt -= game.players[ap].family_restaurant
    
    wf_EV = (game.players[ap].wheat_field * 
                  (self_odds[1] + cum_other_odds[1]))
    ranch_EV = (game.players[ap].ranch * 
                  (self_odds[2] + cum_other_odds[2]))
    bakery_EV = (game.players[ap].bakery * (self_odds[2]+self_odds[3]))
    cafe_pos_EV = (game.players[ap].cafe * cum_other_odds[3])
    conv_s_EV = (game.players[ap].convenience_store * self_odds[4] * 3)
    forest_EV = (game.players[ap].forest * 
                  (self_odds[5] + cum_other_odds[5]))
    stadium_EV = (
        game.players[ap].stadium * 2 * len(game.players) * self_odds[6]
        )
    tv_EV = (game.players[ap].tv_station * 5 * self_odds[6])
    cheese_fac_EV = (game.players[ap].cheese_factory * 3 *
                     game.players[ap].ranch * self_odds[7])
    furn_fac_EV = (game.players[ap].furniture_factory * 3 *
                   (game.players[ap].forest + game.players[ap].mine) *
                   self_odds[8])
    mine_EV = (game.players[ap].mine * 5 * 
               (self_odds[9] + cum_other_odds[9]))
    apples_EV = (game.players[ap].apple_orchard * 3 *
                 (self_odds[10] + cum_other_odds[10]))
    family_rest_pos_EV = (game.players[ap].family_restaurant * 2 *
                      (cum_other_odds[9] + cum_other_odds[10]))
    farmers_m_EV = (
        game.players[ap].farmers_market * 2 *
        (game.players[ap].wheat_field + game.players[ap].apple_orchard) * 
        (self_odds[11] + self_odds[12])
        )
    cafe_neg_EV = -(enemycafes * self_odds[3])
    family_rest_neg_EV = -(enemyrestrnt * 2 * 
                           (self_odds[9] + self_odds[10]))
    
    turn_cycle_EV = (wf_EV + ranch_EV + bakery_EV + cafe_pos_EV + 
                     conv_s_EV + forest_EV + stadium_EV + tv_EV + 
                     cheese_fac_EV + furn_fac_EV + mine_EV + apples_EV +
                     family_rest_pos_EV + farmers_m_EV + cafe_neg_EV +
                     family_rest_neg_EV)
    return turn_cycle_EV



class SimpleLogic():
    """
    Least complex decision framework for each decision-point
    """
    
    def turn_cycle_EV(self,game,ap):
        self_doubles = (game.players[ap].train_station == 1)
        if self_doubles:
            self_odds = ONEDICE_ODDS
        else:
            self_odds = TWODICE_ODDS
            
        other_doubles = sum(
            [player.train_station for player in game.players]
            )
        other_singles = len(game.players) - other_doubles
        if self_doubles:
            other_doubles -= 1
        
        cum_other_odds = {}
        for result in self_odds.keys():
            cum_other_odds[result] = (
                other_singles * ONEDICE_ODDS[result] +
                other_doubles * TWODICE_ODDS[result]
                )
        
        # 
        enemycafes = sum([player.cafe for player in game.players])
        enemycafes -= game.players[ap].cafes
        enemyrestrnt = sum(
            [player.family_restaurant for player in game.players]
            )
        enemyrestrnt -= game.players[ap].family_restaurant
        
        wf_EV = (game.players[ap].wheat_field * 
                      (self_odds[1] + cum_other_odds[1]))
        ranch_EV = (game.players[ap].ranch * 
                      (self_odds[2] + cum_other_odds[2]))
        bakery_EV = (game.players[ap].bakery * (self_odds[2]+self_odds[3]))
        cafe_pos_EV = (game.players[ap].cafe * cum_other_odds[3])
        conv_s_EV = (game.players[ap].convenience_store * self_odds[4] * 3)
        forest_EV = (game.players[ap].forest * 
                      (self_odds[5] + cum_other_odds[5]))
        stadium_EV = (
            game.players[ap].stadium * 2 * len(game.players) * self_odds[6]
            )
        tv_EV = (game.players[ap].tv_station * 5 * self_odds[6])
        cheese_fac_EV = (game.players[ap].cheese_factory * 3 *
                         game.players[ap].ranch * self_odds[7])
        furn_fac_EV = (game.players[ap].furniture_factory * 3 *
                       (game.players[ap].forest + game.players[ap].mine) *
                       self_odds[8])
        mine_EV = (game.players[ap].mine * 5 * 
                   (self_odds[9] + cum_other_odds[9]))
        apples_EV = (game.players[ap].apple_orchard * 3 *
                     (self_odds[10] + cum_other_odds[10]))
        family_rest_pos_EV = (game.players[ap].family_restaurant * 2 *
                          (cum_other_odds[9] + cum_other_odds[10]))
        farmers_m_EV = (
            game.players[ap].farmers_market * 2 *
            (game.players[ap].wheat_field + game.players[ap].apple_orchard) * 
            (self_odds[11] + self_odds[12])
            )
        cafe_neg_EV = -(enemycafes * self_odds[3])
        family_rest_neg_EV = -(enemyrestrnt * 2 * 
                               (self_odds[9] + self_odds[10]))
        
        turn_cycle_EV = (wf_EV + ranch_EV + bakery_EV + cafe_pos_EV + 
                         conv_s_EV + forest_EV + stadium_EV + tv_EV + 
                         cheese_fac_EV + furn_fac_EV + mine_EV + apples_EV +
                         family_rest_pos_EV + farmers_m_EV + cafe_neg_EV +
                         family_rest_neg_EV)
        return turn_cycle_EV
        
    
    def tv_station(self,game,ap):
        """
        Selects the opponent with the most gold.
        """
        take_from = who_has_most(game,ap,"gold")        
        if isinstance(take_from,list):
            take_from = random.choice(take_from)
        return take_from
    
    def roll_two(self,game,ap):
        """
        Always chooses to roll 2 dice if possible. Arguments are for
        compatibility.
        """
        return True

    def business_center(self,game,ap):
        building_list = ['mine','forest','apple_orchard','cafe',
                         'convenience_store','bakery','ranch','wheat_field']
        take_from = None
        pref_level = 0
        while take_from is None:
            take_building = building_list[pref_level]
            take_from = who_has_most(game, ap, take_building)
            
        for give_building in building_list.reverse():
            if getattr(game.player[ap],give_building) > 0:
                break
        return take_from, take_building, give_building
    
