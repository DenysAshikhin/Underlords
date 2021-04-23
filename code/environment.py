from gym import spaces
import gym

import os
import time
import tkinter
from threading import Event, Thread
from tkinter import Frame, Tk, Label

import numpy
import win32gui
from PIL import ImageTk, Image

from Game_State import state
from HUD import HUD
from Shop import Shop

from hero import Hero
from Items import Items
from Underlords import Underlords
from pynput.mouse import Button, Controller as MouseController

from item import Item

from ray.rllib.utils.typing import EnvActionType, EnvObsType, EnvInfoDict
import threading
import uuid
from typing import Optional

from botVision import UnderlordInteract


class UnderlordEnv(threading.Thread):

    def __init__(self):
        """Initializes an external env.
        Args:
            action_space (gym.Space): Action space of the env.
            observation_space (gym.Space): Observation space of the env.
            max_concurrent (int): Max number of active episodes to allow at
                once. Exceeding this limit raises an error.
        """

        threading.Thread.__init__(self)

        self.daemon = True
        # self.action_space = action_space
        # note to make sure 0's are reserved for n/a -> adding +1 to some values ( marked with a *)
        self.observation_space = spaces.Tuple(
            (spaces.Discrete(101),  # health *
             spaces.Discrete(999),  # gold
             spaces.Discrete(11),  # level *
             spaces.Discrete(99),  # remaining EXP to level up
             spaces.Discrete(50),  # round
             spaces.Discrete(2),  # locked in
             spaces.Discrete(6),  # gamePhase *
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             # heroToMove: id *, tier *, gold * , item(id) *, x *, y * Note: add stats like melee/ranged?
             spaces.MultiDiscrete([61, 200, 4, 5]),  # itemToMove: id *,heroID, x *, y *
             # below are the store heros
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             # below are the bench heroes
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             # below are the board heros
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             # below are underlords to pick (whenever valid)
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]), spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
             # below are the items
             spaces.MultiDiscrete([61, 4, 5, 200]), spaces.MultiDiscrete([61, 4, 5, 200]),
             spaces.MultiDiscrete([61, 4, 5, 200]), spaces.MultiDiscrete([61, 4, 5, 200]),
             spaces.MultiDiscrete([61, 4, 5, 200]), spaces.MultiDiscrete([61, 4, 5, 200]),
             spaces.MultiDiscrete([61, 4, 5, 200]), spaces.MultiDiscrete([61, 4, 5, 200]),
             spaces.MultiDiscrete([61, 4, 5, 200]), spaces.MultiDiscrete([61, 4, 5, 200]),
             spaces.MultiDiscrete([61, 4, 5, 200]), spaces.MultiDiscrete([61, 4, 5, 200]),
             # below are the items to pick from
             spaces.MultiDiscrete([61, 4, 5, 200]), spaces.MultiDiscrete([61, 4, 5, 200]),
             spaces.MultiDiscrete([61, 4, 5, 200])
             ))

        self.action_space = spaces.MultiDiscrete(
            [  # 0=reroll, 1 = lock in, 2 = level up, 3 = buy unit from store, 4 = sell unit, 5 = choose item,
                # 6 = choose underlord, 7 = move Unit, 8 = move Item
                9,
                9,  # x-cordinate *
                9,  # y-cordinate *
                4,  # selection -> used only when having to choose an item or underlord
            ]
        )
        self._episodes = {}
        self._finished = set()
        self._results_avail_condition = threading.Condition()
        self._max_concurrent_episodes = 1  # maybe maybe not, no clue lmao

        root = Tk()
        root.resizable(0, 0)
        underlord = UnderlordInteract(root)

        root.mainloop()
