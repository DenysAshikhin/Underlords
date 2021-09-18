import os
import ray
from ray.rllib.agents import with_common_config
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.env import PolicyServerInput
from ray.tune.logger import pretty_print

from ray.rllib.examples.env.random_env import RandomEnv
from gym import spaces
import numpy as np


import argparse

heroId = 72
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
             spaces.MultiDiscrete([250, 3]),  # heroToMove: heroLocalID, isUnderlord
             spaces.Discrete(250),  # itemToMove: localID*,
             spaces.Discrete(3),  # reRoll cost
             spaces.Discrete(2),  # rerolled (item)
             spaces.Discrete(35),  # current round timer
             # below are the store heros
             spaces.MultiDiscrete([heroId, heroId, heroId, heroId, heroId]),
             # below are the bench heroes
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             # below are the board heros
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             # below are underlords to pick (whenever valid) -> underlord ID - specialty
             spaces.MultiDiscrete([5, 3, 5, 3, 5, 3, 5, 3]),
             # below are the items
             spaces.MultiDiscrete([70, 14, 250, 4, 5]), spaces.MultiDiscrete([70, 14, 250, 4, 5]),
             spaces.MultiDiscrete([70, 14, 250, 4, 5]), spaces.MultiDiscrete([70, 14, 250, 4, 5]),
             spaces.MultiDiscrete([70, 14, 250, 4, 5]), spaces.MultiDiscrete([70, 14, 250, 4, 5]),
             spaces.MultiDiscrete([70, 14, 250, 4, 5]), spaces.MultiDiscrete([70, 14, 250, 4, 5]),
             spaces.MultiDiscrete([70, 14, 250, 4, 5]), spaces.MultiDiscrete([70, 14, 250, 4, 5]),
             spaces.MultiDiscrete([70, 14, 250, 4, 5]), spaces.MultiDiscrete([70, 14, 250, 4, 5]),
             # below are the items to pick from
             spaces.MultiDiscrete([70, 70, 70]),
             # below are dicts of other players: slot, health, gold, level, boardUnits (ID, Tier)
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4]),
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4]),
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4]),
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4]),
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4]),
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4]),
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4])
             ))
print(space)
print('-----')

# result = (int(np.product(space.shape)), )
result = spaces.flatten_space(space)
print(result)