# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 13:40:59 2022

@author: johna
"""

from utils import transact

def activation_order(game,ap,reverse=False):
    num_p = len(game.players)
    eval_order = [(ap + i) % num_p for i in range(num_p)]
    if reverse is True:
        eval_order.reverse()
    return eval_order

def process_roll(game,diceroll,ap):
    """
    Function to handle non-decisionmaking gold transactions for any given
    dice roll.

    Parameters
    ----------
    game : Game object
    diceroll : int
        Value of the dice roll to be evaluated.
    ap : int
        Index of active player in game.
    """
    order = activation_order(game,ap)
    reverse_order = activation_order(game,ap,reverse=True)
    
    if diceroll == 1:
        for i in order:
            num_fields = game.players[i].wheat_field
            transact(src=game.supply,dest=game.players[i],amount=1*num_fields)

    elif diceroll == 2:
        for i in order:
            num_ranch = game.players[i].ranch
            transact(src=game.supply,dest=game.players[i],amount=1*num_ranch)
        active_bakeries = game.players[ap].bakery
        transact(
            src=game.supply,dest=game.players[ap],amount=1*active_bakeries
            )

    elif diceroll == 3:
        for i in reverse_order:
            num_cafe = game.players[i].cafe
            transact(
                src=game.players[ap],dest=game.players[i],amount=1*num_cafe
                )
        
        active_bakeries = game.players[ap].bakery
        transact(
            src=game.supply,dest=game.players[ap],amount=1*active_bakeries
            )
    
    elif diceroll == 4:
        num_conv = game.players[ap].convenience_store
        transact(src=game.supply,dest=game.players[ap],amount=3*num_conv)
    
    elif diceroll == 5:
        for i in order:
            num_forest = game.players[i].forest
            transact(src=game.supply,dest=game.players[i],amount=1*num_forest)
            
    elif diceroll == 6:
        if game.players[ap].tv_station:
            take_from = game.players[ap].logic.tv_station(game,ap)
            transact(src=game.players[take_from],
                     dest=game.players[ap],
                     amount=5)
            
        if game.players[ap].business_center:
            take_from, take_building, give_building = \
                game.players[ap].logic.business_center(game,ap)
            setattr(
                game.players[ap],
                take_building,
                getattr(game.players[ap],take_building) + 1
                )
            setattr(
                game.players[ap],
                give_building,
                getattr(game.players[ap],give_building) - 1
                )
            setattr(
                game.players[take_from],
                take_building,
                getattr(game.players[take_from]) - 1
                )
            setattr(
                game.players[take_from],
                give_building,
                getattr(game.players[take_from]) + 1
                )
        if game.players[ap].stadium:
            for i in reverse_order:
                transact(
                    src=game.players[i],
                    dest=game.players[ap],
                    amount=2
                    )
        
        
    elif diceroll == 7:
        num_cheese = game.players[ap].cheese_factory
        num_ranch = game.players[ap].ranch
        transact(src=game.supply,
                 dest=game.players[ap],
                 amount=3*num_cheese*num_ranch)
        
    elif diceroll == 8:
        num_furnfac = game.players[ap].furniture_factory
        num_mine = game.players[ap].mine
        num_forest = game.players[ap].forest
        transact(src=game.supply,
                 dest=game.players[ap],
                 amount= 3 * (num_mine + num_forest) * num_furnfac)
    
    elif diceroll == 9:
        for i in reverse_order:
            num_restrnt = game.players[i].family_restaurant
            transact(
                src=game.players[ap],dest=game.players[i],amount=2*num_restrnt
                )
        for i in order:
            num_mine = game.players[i].mine
            transact(src=game.supply,dest=game.players[i],amount=5*num_mine)
            
    elif diceroll == 10:
        for i in reverse_order:
            num_restrnt = game.players[i].family_restaurant
            transact(
                src=game.players[ap],dest=game.players[i],amount=2*num_restrnt
                )
        for i in order:
            num_orch = game.players[i].apple_orchard
            transact(src=game.supply,dest=game.players[i],amount=3*num_orch)
            
    elif diceroll == 11 or diceroll == 12:
        num_market = game.players[ap].farmers_market
        num_wheatfield = game.players[ap].wheat_field
        num_orch = game.players[ap].apple_orchard
        transact(
            src=game.supply,
            dest=game.players[ap],
            amount= 2 * (num_wheatfield + num_orch) * num_market
            )
        

    