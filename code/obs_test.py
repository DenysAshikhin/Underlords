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


obs = (0, [0.24], [0.97], [1.0], [0.0], [0.68], 0, 0, 0, 
[0, 0], 0, 0, 0, 
[0.5780193692161923], 
[10, 13, 0, 4, 
5, 25, 0, 3, 
3, 5, 0, 4, 
1, 5, 15, 2, 
1, 24, 25, 4], 
[1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 2, 2, 1, 2, 1, 1, 1], 
[3, 4, 4, 5, 1, 4, 1, 4, 1, 1, 0, 1, 2, 1, 3, 1, 1, 3, 4], 
[
1, 0.0, 0.0, 0.0, 0.0, 
1.0, 0.0, 0.0, 0.0, 0.3333333333333333, 
0.0, 0.0, 0.0, 0.0, 0.0, 
0.0, 0.0, 0.3333333333333333, 0.5, 0.0, 
0.0, 0.0, 0.0, 0.0, 0.0, 
0.0, 0.0
], 
[10, 17, 21, 0, 0, 0, 0, 0], [1, 24, 25, 0, 1, 0, 0, 0], 
[12, 16, 22, 0, 2, 0, 0, 0], [10, 13, 0, 0, 3, 0, 0, 0], 
[1, 22, 0, 0, 4, 0, 0, 0], [3, 5, 0, 0, 5, 0, 0, 0], 
[1, 22, 0, 3, 6, 0, 0, 0], [12, 16, 22, 0, 7, 0, 0, 0], 
[17, 19, 0, 0, 0, 1, 0, 0], [1, 16, 0, 0, 1, 1, 0, 0], 
[0, 0, 0, 0, 3, 1, 2, 0], [5, 9, 0, 0, 2, 2, 0, 0], 
[2, 17, 0, 0, 4, 2, 0, 0], [15, 18, 21, 0, 7, 2, 0, 0], 
[1, 18, 0, 0, 3, 3, 0, 0], [7, 9, 0, 0, 6, 3, 0, 0], 
[17, 26, 0, 0, 1, 4, 0, 0], [7, 12, 0, 0, 4, 4, 0, 0], 
[18, 26, 0, 0, 6, 4, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], 

[37, 1, 1, 1], [8, 2, 1, 2], [51, 4, 1, 3], [59, 8, 1, 4], [47, 6, 1, 4], 
[44, 9, 2, 2], [11, 7, 2, 1], [24, 9, 2, 4], [28, 5, 1, 4], [40, 3, 1, 3], 
[0, 0, 0], 

8, [0.0], [0.11], [0.9], 
[1, 1, 1, 1, 1, 1, 1, 1, 1, 0], 
[
2, 22, 0, 
18, 26, 0, 
10, 13, 0, 
1, 18, 0, 
6, 13, 0, 
10, 17, 21, 
21, 23, 0,
18, 26, 0, 
2, 11, 19, 
0, 0, 0
]
)

print(observation_space.contains(obs))