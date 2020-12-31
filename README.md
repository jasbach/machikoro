# Machi Koro Simulator

This tool can simulate games of Machi Koro.
The rules for Machi Koro can be found here: https://www.idwgames.com/wp-content/uploads/2015/02/Machi-RULES-reduced.pdf
Refernences for what each card does can be found here: https://machi-koro.fandom.com/wiki/List_of_cards
Note that this only simulates the base game, no expansions.

Three files are included in this simulator:
machikoro.py is the main script with the basic game management functions (roll dice, take turn, start new game)
The other two files are meant to be imported by machikoro.py and are supplementary:
card_effects.py contains functions for each card type. The main script function of resolve_dice contains callouts to these functions to alter the gamestate as necessary.
behaviors.py contains some statistical tools such as EV calculators to guide some simple optimization as well as the skeleton of game decision tools.

The important data in this simulator is a variable called "gamestate". gamestate is a list object containing numpy arrays. The first array, index 0, is the game supply. The number of cards for each type of building is limited, so tracking the supply is essential to constrain legal purchasing decisions. Coins are not supply-limited.
Each subsequent list item is an array representing a player's boardstate. The array is a one-dimensional array of length=19 where each array element represents the number of that building the player owns. The final position in each array represents the player's current number of coins.
The player boards are indexed in this order:
0: wheat field, 1: ranch, 2: forest, 3: mine, 4: apple orchard, 5: bakery, 6: convenience store, 7: cheese factory, 8: furniture factory, 9: fruit and vegetable market, 10: cafe, 11: family restaurant, 12: stadium, 13: TV station, 14: business center, 15: train station, 16: shopping mall, 17: amusement park, 18: radio tower, 19: coins 

There are only a few points in the game where a player makes a decision.
The first and most common is each turn's purchasing decision, where the active player may purchase a new building for their board.
This is handled by first assessing what options are legal purchase options and generating an array of length=18 (corresponding to buildings) and setting legal options to 1 and invalid purchase options to 0. Purchase decisions are made by generating a random float number between 0 and 1 for each building and performing element-wise multiplication with the "options" array - illegal choices will be zeroed out. The building that scores the highest will be selected for purchase.
This introduces the option to apply weighting as we choose - a matching weights array of length=18 can apply weighting by element-wise multiplication. An array of all 1.0 for weights will not alter the probability at all, making the selection pure random from legal options. Any other values can adjust the likelihood of that building scoring max value from the random array - less than 1 decreases odds, greater than 1 increases odds, weighting of 0 makes it impossible for to choose that building.

Currently the simulator is equipped only for full random decision-making. The results of 20,000 simulated 4-player games with full random purchase decisions are stored in the winningplayerboards.csv file included. It records the winning game position for the 20,000 games. Keep in mind that the requirement for winning is building the train station, shopping mall, amusement park, and radio tower - so those don't provide any statistical value.

Other, smaller decision points and how I handled them in the simulator:
With train station built, whether to roll 1 or 2 dice - calculate the EV of rolling one dice vs rolling two dice and choosing the one with greater expected return
When TV Station is activated, who to steal 5 coins from - set to steal from whichever player has the most coins
When Business Center is activated, which buildings to trade - first the function calculates which building is adding the least EV to the board and identifies it as outgoing. Then it checks all possible buildings for which would add the most EV, sorts them by added EV, and checks other players' boards for if they have any of those buildings in descending EV+ order. Once it finds one, it makes that trade. Maximizes active player EV, does not consider sabotage of opponents, does not consider possible synergies involving potential incoming buildings.
Whether to re-roll dice once Radio Tower is built - calculates the actual payout of the original roll, and if it is less than the expected value of the average roll, rerolls the dice
Note that all of these smaller decision points could in the future be tinkered with, but for now I'm focused on purchasing decisions.
