import random
import logging
logging.basicConfig()
logger = logging.getLogger('game')
logger.setLevel("INFO")

import pandas as pd

import dice
import utils
from logic import SimpleLogic


class Game():

    def __init__(self,players=4,logic=[SimpleLogic()]*4):
        """
        Initialize a fresh game state
        """
        assert 1 < players < 5
        self.supply = Supply()
        self.players = [Player() for n in range(players)]
        for player, l in zip(self.players, logic):
            player.logic = l
        self.supply.gold -= 3*players
        self.active_player = random.randint(0,players-1)
        self.turn_number = 1
        self.game_over = False
        self.winner = None
        self.history = pd.DataFrame(
            columns=['active_player','roll','build']
            )
        
    def copy(self):
        # utility function used for hypotheticals in simple logic structures
        newgame = Game(players=len(self.players))
        for i in range(len(self.players)):
            for attr in vars(self.players[i]).keys():
                if attr.startswith("_"):
                    continue
                setattr(newgame.players[i],attr,getattr(self.players[i],attr))
                
        for attr in vars(self.supply).keys():
                if attr.startswith("_"):
                    continue
                setattr(newgame.supply,attr,getattr(self.supply,attr))
                
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
        logger.info(" Starting turn {}...".format(self.turn_number))
        for player in self.players:
            player.log_state()
        while True:
            dice_result, doubles = self.roll()
            logger.info(
                " Player {} rolled a {}.".format(self.active_player, 
                                                 dice_result)
                )
            if self.players[self.active_player].radio_tower:
                if self.players[self.active_player].logic.reroll(
                        self,self.active_player,dice_result
                        ):
                    logger.info(" Opting to re-roll...")
                    dice_result, doubles = self.roll()
                    logger.info(" New result is: {}".format(dice_result))
            dice.process_roll(self,dice_result,self.active_player)
            to_build = self.players[self.active_player].logic.build(
                self,self.active_player
                )
            if to_build is not None:
                self.players[self.active_player].gold -= utils.COSTS[to_build]
                utils.increment(self.players[self.active_player],to_build)
                utils.increment(self.supply,to_build,subtract=True)
            if doubles and self.players[self.active_player].amusement_park:
                logger.info(" Doubles! Taking an extra turn...")
                continue
            else:
                break
        
        # possible we want to make this a separate function
        self.history = pd.concat((
            self.history,
            pd.DataFrame(index=[self.turn_number],
                         data = {'active_player':self.active_player,
                                 'roll':dice_result,
                                 'build':to_build})
            ))
            
        # check for win
        if all((self.players[self.active_player].amusement_park == 1,
                self.players[self.active_player].radio_tower == 1,
                self.players[self.active_player].train_station == 1,
                self.players[self.active_player].shopping_mall == 1)):
            self.game_over = True
            self.winner = self.active_player
        # advance active player indicator
        self.active_player += 1
        self.active_player %= len(self.players)
        self.turn_number += 1
        
        
class Player():
    def __init__(self):
        for building in utils.BUILDINGS:
            if building == 'wheat_field' or building == 'ranch':
                setattr(self,building,1)
            else:
                setattr(self,building,0)
        self.gold = 3
        self.logic = None
        self.history = pd.DataFrame(columns=utils.BUILDINGS + ['gold'])
        
    def log_state(self):
        state = {
            building:getattr(self,building) for building in utils.BUILDINGS
            }
        state['gold'] = self.gold
        self.history = pd.concat((
            self.history,pd.DataFrame(data=state,index=[0])
            ),
            ignore_index=True)
            
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
                         'farmers_market',
                         'family_restaurant']:
            setattr(self,building,6)
        for maj_building in ['tv_station',
                             'business_center',
                             'stadium']:
            setattr(self,maj_building,4)
        for landmark in ['amusement_park',
                         'train_station',
                         'shopping_mall',
                         'radio_tower']:
            setattr(self,landmark,4)
        self.gold = 42 + 24*5 + 12*10
        