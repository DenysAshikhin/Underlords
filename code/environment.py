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
        thread = UnderlordInteract(root)

        root.mainloop()

        self.observation_space = spaces.tuple()