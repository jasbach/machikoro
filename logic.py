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
import logging
logging.basicConfig()
logger = logging.getLogger("logic")
logger.setLevel("INFO")

import dice
import utils

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

LANDMARKS = ['train_station','shopping_mall','amusement_park','radio_tower']
MAJ_ESTAB = ['stadium','tv_station','business_center']

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

def calc_EV(game,ap,full_cycle=True):
    """
    Calcuates expected value of either a full turn cycle or a single AP dice
    roll.
    
    Parameters
    ----------
    game : Game
        Current game state
    ap : int
        Index for the active player in game.players
    full_cycle : bool
        True if you want the full turn cycle EV (used for build calcs) and
        false if you want a single active player dice roll EV
        
    Returns
    -------
    total_EV : float
        Expected value in gold
    """
    # TODO - need a smarter way to evaluate whether a player will roll doubles
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
        if full_cycle is True:
            cum_other_odds[result] = (
                other_singles * ONEDICE_ODDS[result] +
                other_doubles * TWODICE_ODDS[result]
                )
        else:
            cum_other_odds[result] = 0
    
    enemycafes = sum([player.cafe for player in game.players])
    enemycafes -= game.players[ap].cafe
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
    
    total_EV = (wf_EV + ranch_EV + bakery_EV + cafe_pos_EV + 
                     conv_s_EV + forest_EV + stadium_EV + tv_EV + 
                     cheese_fac_EV + furn_fac_EV + mine_EV + apples_EV +
                     family_rest_pos_EV + farmers_m_EV + cafe_neg_EV +
                     family_rest_neg_EV)
    return total_EV



class SimpleLogic():
    """
    Least complex decision framework for each decision-point
    """
        
    
    def tv_station(self,game,ap):
        """
        Selects the opponent with the most gold.
        """
        take_from = who_has_most(game,ap,"gold")        
        if isinstance(take_from,list):
            take_from = random.choice(take_from)
        logger.info(
            " TV Station - taking 5 gold from player {}".format(take_from)
            )
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
            pref_level += 1
            
        for give_building in reversed(building_list):
            if getattr(game.players[ap],give_building) > 0:
                break
        logger.info(
            " Building swap! Taking {} from {} in exchange for {}".format(
                take_building,take_from,give_building,
                )
            )
        return take_from, take_building, give_building
    
    def reroll(self,game,ap,result):
        current_gold = game.players[ap].gold
        # first evaluate gold change
        futuregame = game.copy()
        dice.process_roll(futuregame,result,ap)
        future_gold = futuregame.players[ap].gold
        gold_diff = current_gold - future_gold
        expected_value = calc_EV(game,ap,full_cycle=False)
        if gold_diff > expected_value:
            decision = False
        else:
            decision = True
        return decision
    
    def build(self,game,ap):
        """
        
        """
        
        # first check landmarks in ascending cost order, if possible, build
        for landmark in LANDMARKS:
            if utils.COSTS[landmark] < game.players[ap].gold:
                if getattr(game.players[ap],landmark) == 0:
                    return landmark
        # second check major establishments and pick them up if possible
        for building in MAJ_ESTAB:
            if utils.COSTS[building] < game.players[ap].gold:
                if getattr(game.players[ap],building) == 0:
                    return building
        
        # possibly want to move the evaluation of legal options into game file
        legal_options = []
        for building in utils.COSTS.keys():
            if all((utils.COSTS[building] < game.players[ap].gold,
                    getattr(game.supply,building) > 0)):
                   if any((building not in MAJ_ESTAB,
                           getattr(game.players[ap],building) == 0)):
                       legal_options.append(building)
        
        # finally, cycle through legal options and choose the one that
        # provides the best immediate turn cycle EV boost
        current_EV = calc_EV(game,ap,full_cycle=True)
        best_gains = 0
        to_build = None
        for building in legal_options:
            hypothetical = game.copy()
            setattr(hypothetical.players[ap],
                    building,
                    getattr(hypothetical.players[ap],building) + 1)
            hypo_EV = calc_EV(hypothetical,ap,full_cycle=True)
            gains = hypo_EV - current_EV
            if gains > best_gains:
                best_gains = gains
                to_build = building
        logger.info(" Build choice is: {}".format(to_build))
        return to_build

if __name__ == '__main__':
    import game
    testgame = game.Game()
    testlogic = SimpleLogic()
    testlogic.build(testgame,0)