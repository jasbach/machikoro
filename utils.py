# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 13:42:58 2022

@author: johna
"""

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