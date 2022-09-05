# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 19:10:08 2022

@author: johna
"""

from game import Game
from logic import SimpleLogic

g = Game(players=4,logic=[SimpleLogic()]*4)
while g.game_over is False:
    g.take_turn()
    
print("Winner! Player {}".format(g.winner))