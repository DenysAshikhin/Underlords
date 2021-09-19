from gym import spaces
import numpy as np

heroId = 72
localHeroId = 100
itemId = 70
localItemId = 10

space = spaces.Tuple(
    (spaces.Discrete(9),  # final position * (if not 0 means game is over!)
     spaces.Discrete(101),  # health *
     spaces.Discrete(100),  # gold
     spaces.Discrete(11),  # level *
     spaces.Discrete(99),  # remaining EXP to level up
     spaces.Discrete(50),  # round
     spaces.Discrete(2),  # locked in
     spaces.Discrete(2),  # punish for locking in this round
     spaces.Discrete(6),  # gamePhase *
     spaces.MultiDiscrete([localHeroId, 3]),  # heroToMove: heroLocalID, isUnderlord
     spaces.Discrete(localItemId),  # itemToMove: localID*,
     spaces.Discrete(3),  # reRoll cost
     spaces.Discrete(2),  # rerolled (item)
     spaces.Discrete(35),  # current round timer
     # below are the store heros
     spaces.MultiDiscrete([heroId, heroId, heroId, heroId, heroId]),
     # below are the bench heroes
     spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]), spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]),
     spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]), spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]),
     spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]), spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]),
     spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]), spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]),
     # below are the board heros
     spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]), spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]),
     spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]), spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]),
     spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]), spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]),
     spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]), spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]),
     spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]), spaces.MultiDiscrete([heroId, localHeroId, 4, 6, localItemId, 9, 9, 3]),
     # below are underlords to pick (whenever valid) -> underlord ID - specialty
     spaces.MultiDiscrete([5, 3, 5, 3, 5, 3, 5, 3]),
     # below are the items
     spaces.MultiDiscrete([itemId, localItemId, localHeroId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, localHeroId, 4, 5]),
     spaces.MultiDiscrete([itemId, localItemId, localHeroId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, localHeroId, 4, 5]),
     spaces.MultiDiscrete([itemId, localItemId, localHeroId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, localHeroId, 4, 5]),
     spaces.MultiDiscrete([itemId, localItemId, localHeroId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, localHeroId, 4, 5]),
     spaces.MultiDiscrete([itemId, localItemId, localHeroId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, localHeroId, 4, 5]),
     # spaces.MultiDiscrete([itemId, localItemId, localHeroId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, localHeroId, 4, 5]),
     # below are the items to pick from
     spaces.MultiDiscrete([itemId, itemId, itemId]),
     # below are dicts of other players: slot, health, gold, level, boardUnits (ID, Tier)
     spaces.MultiDiscrete(
         [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4,
          heroId, 4, heroId, 4]),
     spaces.MultiDiscrete(
         [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4,
          heroId, 4, heroId, 4]),
     spaces.MultiDiscrete(
         [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4,
          heroId, 4, heroId, 4]),
     spaces.MultiDiscrete(
         [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4,
          heroId, 4, heroId, 4]),
     spaces.MultiDiscrete(
         [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4,
          heroId, 4, heroId, 4]),
     spaces.MultiDiscrete(
         [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4,
          heroId, 4, heroId, 4]),
     spaces.MultiDiscrete(
         [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4,
          heroId, 4, heroId, 4])
     ))

dimension = 9 + 101 + 100 + 11 + 99 + 50 + 2 + 2 + 6 + localHeroId + 3 + localItemId + 3 + 2 + 35 + (heroId * 5) + 18 * (heroId + localHeroId + 4 + 6 + localItemId + 9 + 9 + 3) + (4 * 5 + 4 * 3) + 10 * (itemId + localItemId + localHeroId + 4 + 5) + 3 * (itemId)  + 7 * (9 + 101 + 100 + 11 + (10 * heroId) + (10 * 4))
print(dimension)

output = 7 + 9 + 9
print(f"Output: {output}")

from math import ceil
# obs_size = 100 #replace with real value`
obs_size = dimension
outputSize = 5
num_layers = 128
shrink_factor = 0.96

newNet = [obs_size]

for i in range(num_layers):
 val = ceil(obs_size * shrink_factor**(i+1))
 if val < outputSize:
  newNet.append(outputSize)
 else:
  newNet.append(ceil(obs_size * shrink_factor**(i+1)))

# net = [ceil(obs_size * shrink_factor**(i+1)) for i in range(num_layers)]
print(newNet)
print(sum(newNet))
print(f"Original {obs_size * 42}")
