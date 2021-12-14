from tkinter import Tk
import gym
from gym import spaces
import numpy as np




heroId = 72
allianceId = 27
localHeroId = 100
itemId = 70
localItemId = 10
x = 8
y = 5
underlordsId = 9
tier = 6

observation_space = spaces.Tuple(
            (spaces.Discrete(9),  # final position * (if not 0 means game is over!)

             # spaces.Discrete(101),  # health *
             # spaces.Discrete(100),  # gold
             # spaces.Discrete(11),  # level *

             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),

             # spaces.Discrete(99),  # remaining EXP to level up
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),

             # spaces.Discrete(50),  # round
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),

             spaces.Discrete(2),  # locked in
             spaces.Discrete(2),  # punish for locking in this round
             spaces.Discrete(6),  # gamePhase *
             spaces.MultiDiscrete([x, y]),  # heroToMove: x, y coord
             spaces.Discrete(localItemId),  # itemToMove: localID*,
             spaces.Discrete(3),  # reRoll cost
             spaces.Discrete(2),  # rerolled (item)

             # spaces.Discrete(35),  # current round timer
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),

             # below are the store heros
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, tier, allianceId, allianceId, allianceId, tier,
                                   allianceId, allianceId, allianceId, tier, allianceId, allianceId, allianceId, tier,
                                   allianceId, allianceId, allianceId, tier]),
             # below are the bench heroes
             # first the levels of all the heroes
             spaces.Box(low=np.array([0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0, 
                                      0, 0, 0, 0, 0, 
                                      0, 0, 0, 0]),
                        high=np.array([3, 3, 3, 3, 3, 
                                       3, 3, 3, 3, 3, 
                                       3, 3, 3, 3, 3, 
                                       3, 3, 3, 3]),
                        dtype=np.float32),
             # now the cost of all the heroes
             spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
                        high=np.array([5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]),
                        dtype=np.float32),

             # Alliance composition of units
             spaces.Box(low=np.array([0, 0, 0, 0, 0, 
                                      0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0, 
                                      0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0, 
                                      0, 0]),
                        high=np.array([1, 1, 1, 1, 1, 
                                       1, 1, 1, 1, 1,
                                       1, 1, 1, 1, 1, 
                                       1, 1, 1, 1, 1,
                                       1, 1, 1, 1, 1, 
                                       1, 1]),
                        dtype=np.float32),


             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             # below are the board heros (11 because 1 is underlord)
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             # below are underlords to pick (whenever valid) -> underlord ID - specialty
             spaces.MultiDiscrete([5, 3, 5, 3, 5, 3, 5, 3]),
             # below are the items
             spaces.MultiDiscrete([itemId, localItemId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, 4, 5]),
             spaces.MultiDiscrete([itemId, localItemId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, 4, 5]),
             spaces.MultiDiscrete([itemId, localItemId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, 4, 5]),
             spaces.MultiDiscrete([itemId, localItemId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, 4, 5]),
             spaces.MultiDiscrete([itemId, localItemId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, 4, 5]),
             # spaces.MultiDiscrete([itemId, localItemId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, 4, 5]),
             # below are the items to pick from
             spaces.MultiDiscrete([itemId, itemId, itemId]),
             # below are dicts of other players: slot, health, gold, level, boardUnits (ID, Tier)

             spaces.Discrete(9),
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             spaces.MultiDiscrete([
             allianceId, allianceId, allianceId, 
             allianceId, allianceId, allianceId, 
             allianceId, allianceId, allianceId, 
             allianceId, allianceId, allianceId, 
             allianceId, allianceId, allianceId, 
             allianceId, allianceId, allianceId, 
             allianceId, allianceId, allianceId, 
             allianceId, allianceId, allianceId, 
             allianceId, allianceId, allianceId, 
             allianceId, allianceId, allianceId]),

             # spaces.Discrete(9),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             # spaces.MultiDiscrete([allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId]),
             #
             # spaces.Discrete(9),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             # spaces.MultiDiscrete([allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId]),
             #
             # spaces.Discrete(9),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             # spaces.MultiDiscrete([allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId]),
             #
             # spaces.Discrete(9),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             # spaces.MultiDiscrete([allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId]),
             #
             # spaces.Discrete(9),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             # spaces.MultiDiscrete([allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId]),
             #
             # spaces.Discrete(9),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             # spaces.MultiDiscrete([allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId])
             ))


obs = (0, [0.66], [0.09], [0.6], [0.16], [0.18], 0, 0, 0, [5, 0], 0, 0, 0, 
[0.8218074980236235], 
[
5, 7, 11, 3, 
13, 14, 0, 4, 
21, 23, 0, 3, 
17, 19, 0, 1, 
13, 20, 0, 2
], 

[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 1, 1, 1, 1, 1, 2, 2, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
[
0, 0.0, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.0, 
0.0, 0.0, 0.0, 0.0, 0.0, 
0.0, 0.0, 0.0, 0.0, 0, 
0.0, 0.0, 0.0, 0.0, 0.0, 
0.0, 0.0], 

[7, 12, 0, 0, 0, 0, 0, 0], [8, 15, 23, 0, 1, 0, 0, 0], 
[10, 13, 0, 0, 2, 0, 0, 0], [11, 16, 0, 0, 3, 0, 0, 0], 
[2, 6, 0, 0, 4, 0,0, 0], [12, 23, 0, 0, 5, 0, 0, 0], 
[11, 24, 0, 0, 6, 0, 0, 0], [19, 21, 0, 0, 7, 0, 0, 0], 
[0, 0, 0, 0, 3, 1, 2, 1], [19, 21, 0, 0, 7, 1, 0, 0], 
[17, 19, 0, 0, 3, 2, 0, 0],  [0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0,0, 0], 


[22, 1, 1, 1], [53, 2, 1, 2], [2, 3, 1, 3], [0, 0, 0, 0], [0, 0, 0, 0], [
0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0],


5, [0.83], [0.27], [0.6], 
[1, 1, 1, 1, 1, 1, 0, 0, 0, 0], 
[
4, 10, 0, 
4, 10, 0, 
17, 26, 0, 
8, 10, 12, 
3, 17, 0, 
1, 20, 22, 
0, 0, 0, 
0, 0, 0, 
0, 0, 0, 
0, 0, 0
])

print(observation_space.contains(obs))