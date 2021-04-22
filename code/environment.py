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

from botVision import UnderlordInteract


class UnderlordEnv(gym.Env):

    def __init__(self):
        super(UnderlordEnv, self).__init__()

        root = Tk()
        root.resizable(0, 0)
        underlord = UnderlordInteract(root)

        root.mainloop()

        # note to make sure 0's are reserved for n/a -> adding +1 to some values ( marked with a *)
        self.observation_space = spaces.Tuple(
            spaces.Discrete(100),  # health
            spaces.Discrete(999),  # gold
            spaces.Discrete(10),  # level
            spaces.Discrete(50),  # round
            spaces.Discrete(2),  # locked in
            spaces.Discrete(6),  # gamePhase *
            spaces.MultiDiscrete([64, 4, 6, 14, 9, 9]),
            # heroToMove: id *, tier *, gold * , item(id) *, x *, y * Note: add stats like melee/ranged?
            spaces.MultiDiscrete([61, 4, 5, 200])  # itemToMove: id *, x *, y *, heroID
        )

    def getObservation(self):

        vals = self.underlord.getObservation()