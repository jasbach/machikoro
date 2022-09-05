# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 13:42:58 2022

@author: johna
"""

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
BUILDINGS = ['wheat_field',
             'ranch',
             'bakery',
             'cafe',
             'convenience_store',
             'forest',
             'cheese_factory',
             'furniture_factory',
             'mine',
             'family_restaurant',
             'apple_orchard',
             'farmers_market',
             'tv_station',
             'business_center',
             'stadium',
             'amusement_park',
             'radio_tower',
             'shopping_mall',
             'train_station']

def transact(src,dest,amount):
        """
        Function to govern game transactions as a result of dice rolls.

        Parameters
        ----------
        src : Player or Supply
            from - Source of the gold changing hands.
        dest : Player
            to - Destination of the gold changing hands.
        amount : int
            Amount of gold changing hands

        """
        if amount > src.gold:
            amount = src.gold
            
        src.gold -= amount
        dest.gold += amount
        
def increment(obj,attr,subtract=False):
    # util function used to modify by one an attribute via string naming
    if subtract == False:
        setattr(obj,attr,getattr(obj,attr)+1)
    elif subtract == True:
        setattr(obj,attr,getattr(obj,attr)-1)