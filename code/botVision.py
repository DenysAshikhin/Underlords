import os
import time
import tkinter
from threading import Event, Thread
from tkinter import Frame, Tk, Label

import time
import numpy
import win32gui
from PIL import ImageTk, Image

import Offset
from GSI_Server import GSI_Server
from Game_State import state
from HUD import HUD
from Shop import Shop
import main

from hero import Hero
from Items import Items
from Underlords import Underlords
from pynput.mouse import Button, Controller as MouseController

from item import Item

mouse1 = MouseController()


def loadProfiles():
    root = os.path.join(os.path.dirname(os.getcwd()), "final profile pics")
    profileMap = {}
    itemIDMap = {}
    i = 0
    for file in os.listdir(root):
        img = Image.open(os.path.join(root, file))
        img = ImageTk.PhotoImage(img)
        profileMap[file[: -4]] = img
        itemIDMap[file[: -4]] = i
        i += 1
    return profileMap


def loadUnderlodProfiles():
    root = os.path.join(os.path.dirname(os.getcwd()), "underlord profile pics")
    profileMap = {}
    for file in os.listdir(root):
        img = Image.open(os.path.join(root, file))
        img = ImageTk.PhotoImage(img)
        profileMap[file[: -4]] = img
    return profileMap


def itemNameList():
    root = os.path.join(os.path.dirname(os.getcwd()), "items")
    itemList = []
    for file in os.listdir(root):
        itemList.append(file[: -4])
    return itemList


"""
Loads in the offset between different monitor resolutions, offset is calculated by calling Offset.py writeConfig() 
"""


def loadScreenOffset():
    x, y = Offset.detectOffset()
    return x, y


class UnderlordInteract():
    def __init__(self, rootWindow, training=False):
        # Thread.__init__(self)
        # self.stopped = event
        self.rootWindow = rootWindow
        self.lockedIn = False
        self.items = Items()

        self.hwnd = win32gui.FindWindow(None, 'Dota Underlords')
        #        win32gui.SetForegroundWindow(self.hwnd)

        rect = None

        try:
            rect = win32gui.GetWindowRect(self.hwnd)
        except:
            rect = None

        self.alliances = {
            'none': 0,
            'assassin': 1,
            'brawny': 2,
            'brute': 3,
            'champion': 4,
            'demon': 5,
            'dragon': 6,
            'fallen': 7,
            'healer': 8,
            'heartless': 9,
            'human': 10,
            'hunter': 11,
            'knight': 12,
            'mage': 13,
            'magus': 14,
            'poisoner': 15,
            'rogue': 16,
            'savage': 17,
            'scaled': 18,
            'shaman': 19,
            'spirit': 20,
            'summoner': 21,
            'swordsman': 22,
            'troll': 23,
            'vigilant': 24,
            'void': 25,
            'warrior': 26
        }

        self.heroAlliances = {
            'anti_mage': [self.alliances['hunter'], self.alliances['rogue'], self.alliances['none']],
            'batrider': [self.alliances['knight'], self.alliances['troll'], self.alliances['none']],
            'bounty_hunter': [self.alliances['assassin'], self.alliances['rogue'], self.alliances['none']],
            'crystal_maiden': [self.alliances['human'], self.alliances['mage'], self.alliances['none']],
            'dazzle': [self.alliances['healer'], self.alliances['poisoner'], self.alliances['troll']],
            'drow_ranger': [self.alliances['heartless'], self.alliances['hunter'], self.alliances['vigilant']],
            'enchantress': [self.alliances['shaman'], self.alliances['healer'], self.alliances['none']],
            'lich': [self.alliances['fallen'], self.alliances['mage'], self.alliances['none']],
            'magnus': [self.alliances['savage'], self.alliances['shaman'], self.alliances['none']],
            'phantom_assassin': [self.alliances['assassin'], self.alliances['swordsman'], self.alliances['none']],
            'shadow_demon': [self.alliances['demon'], self.alliances['heartless'], self.alliances['none']],
            'slardar': [self.alliances['scaled'], self.alliances['warrior'], self.alliances['none']],
            'snapfire': [self.alliances['brawny'], self.alliances['dragon'], self.alliances['none']],
            'tusk': [self.alliances['savage'], self.alliances['warrior'], self.alliances['none']],
            'vengeful_spirit': [self.alliances['fallen'], self.alliances['spirit'], self.alliances['none']],
            'venomancer': [self.alliances['poisoner'], self.alliances['scaled'], self.alliances['summoner']],
            'bristleback': [self.alliances['brawny'], self.alliances['savage'], self.alliances['none']],
            'chaos_knight': [self.alliances['demon'], self.alliances['knight'], self.alliances['none']],
            'earth_spirit': [self.alliances['spirit'], self.alliances['warrior'], self.alliances['none']],
            'juggernaut': [self.alliances['brawny'], self.alliances['swordsman'], self.alliances['none']],
            'kunkka': [self.alliances['human'], self.alliances['swordsman'], self.alliances['warrior']],
            'legion_commander': [self.alliances['champion'], self.alliances['human'], self.alliances['none']],
            'luna': [self.alliances['knight'], self.alliances['vigilant'], self.alliances['none']],
            'meepo': [self.alliances['rogue'], self.alliances['summoner'], self.alliances['none']],
            'natures_prophet': [self.alliances['shaman'], self.alliances['summoner'], self.alliances['none']],
            'pudge': [self.alliances['heartless'], self.alliances['warrior'], self.alliances['none']],
            'queen_of_pain': [self.alliances['assassin'], self.alliances['demon'], self.alliances['poisoner']],
            'spirit_breaker': [self.alliances['brute'], self.alliances['savage'], self.alliances['none']],
            'storm_spirit': [self.alliances['mage'], self.alliances['spirit'], self.alliances['none']],
            'windranger': [self.alliances['hunter'], self.alliances['vigilant'], self.alliances['none']],
            'abaddon': [self.alliances['fallen'], self.alliances['knight'], self.alliances['none']],
            'alchemist': [self.alliances['brute'], self.alliances['poisoner'], self.alliances['rogue']],
            'beastmaster': [self.alliances['brawny'], self.alliances['hunter'], self.alliances['shaman']],
            'ember_spirit': [self.alliances['assassin'], self.alliances['spirit'], self.alliances['swordsman']],
            'lifestealer': [self.alliances['brute'], self.alliances['healer'], self.alliances['none']],
            'lycan': [self.alliances['human'], self.alliances['savage'], self.alliances['summoner']],
            'omniknight': [self.alliances['healer'], self.alliances['human'], self.alliances['knight']],
            'puck': [self.alliances['dragon'], self.alliances['mage'], self.alliances['none']],
            'shadow_shaman': [self.alliances['summoner'], self.alliances['troll'], self.alliances['none']],
            'slark': [self.alliances['assassin'], self.alliances['scaled'], self.alliances['none']],
            'spectre': [self.alliances['demon'], self.alliances['void'], self.alliances['none']],
            'terrorblade': [self.alliances['demon'], self.alliances['fallen'], self.alliances['hunter']],
            'treant_protector': [self.alliances['hunter'], self.alliances['rogue'], self.alliances['none']],
            'death_prophet': [self.alliances['fallen'], self.alliances['heartless'], self.alliances['none']],
            'doom': [self.alliances['brute'], self.alliances['demon'], self.alliances['none']],
            'lina': [self.alliances['human'], self.alliances['mage'], self.alliances['none']],
            'lone_druid': [self.alliances['savage'], self.alliances['shaman'], self.alliances['summoner']],
            'mirana': [self.alliances['hunter'], self.alliances['vigilant'], self.alliances['none']],
            'pangolier': [self.alliances['savage'], self.alliances['swordsman'], self.alliances['none']],
            'rubick': [self.alliances['mage'], self.alliances['magus'], self.alliances['none']],
            'sven': [self.alliances['knight'], self.alliances['rogue'], self.alliances['swordsman']],
            'templar_assassin': [self.alliances['assassin'], self.alliances['vigilante'], self.alliances['void']],
            'tidehunter': [self.alliances['scaled'], self.alliances['warrior'], self.alliances['none']],
            'viper': [self.alliances['dragon'], self.alliances['poisoner'], self.alliances['none']],
            'void_spirit': [self.alliances['spirit'], self.alliances['void'], self.alliances['none']],
            'axe': [self.alliances['brawny'], self.alliances['brute'], self.alliances['none']],
            'dragon_knight': [self.alliances['dragon'], self.alliances['human'], self.alliances['knight']],
            'keeper_of_the_light': [self.alliances['human'], self.alliances['mage'], self.alliances['none']],
            'medusa': [self.alliances['hunter'], self.alliances['scaled'], self.alliances['none']],
            'troll_warlord': [self.alliances['troll'], self.alliances['warrior'], self.alliances['none']],
            'skeleton_king': [self.alliances['fallen'], self.alliances['swordsman'], self.alliances['none']]
        }

        self.finalPlacement = 0
        self.rerollCost = 2
        self.underlordPicks = None
        self.itemPicks = None
        self.shopUnits = None
        self.gsiItems = None
        self.combatType = 0
        # self.allowMove = False
        self.combatResult = -1
        self.wins = 0
        self.losses = 0
        self.round = 0
        self.prevHP = 100
        self.newRoundStarted = False

        self.rewardSummary = {'purchases': 0, 'roundsSurvived': 0, 'finalPosition': 0, 'unitLevelUp': 0,
                              'mainLevelUp': 0, 'extra': 0, 'lockIn': 0, 'itemPick': 0}
        self.server = True

        if rect is not None:
            self.server = GSI_Server(('localhost', 3000), env=self)
            self.server.start_server()
            print('server started!')
            self.profilePics = loadProfiles()
            self.underlordPics = loadUnderlodProfiles()
            self.server = False
        else:
            return None

        if rect is None:
            self.x = 0
            self.y = 0
            self.h = 0
            self.w = 0
        else:
            self.x = rect[0]
            self.y = rect[1]
            self.w = rect[2] - self.x
            self.h = rect[3] - self.y
        self.shopX = self.x + 910
        self.shopY = self.y + 70
        self.rerollX = self.shopX
        self.rerollY = self.shopY + 82
        self.clickUpX = self.rerollX
        self.clickUpY = self.rerollY + 70
        self.benchX = self.x + 250
        self.benchXOffset = 90
        self.benchY = self.y + 800
        self.boardX = self.x + 300
        self.boardXOffset = 80
        self.boardY = self.y + 400
        self.boardYOffset = 70
        self.lockInX = self.shopX - 500
        self.lockInY = self.shopY + 75
        self.itemX = self.shopX + 60
        self.itemXOffset = 20
        self.itemY = self.shopY + 60
        self.itemYOffset = 20
        self.itemSelectY = self.y + 394
        self.itemSelectX = self.x + 290
        self.itemSelectXOffset = 220
        self.itemRerollX = self.itemSelectX + self.itemSelectXOffset
        self.itemRerollY = self.itemSelectY + 200
        self.itemMoveX = self.x + 965
        self.itemMoveXOffset = 40
        self.itemMoveY = self.y + 185
        self.itemMoveYOffset = 35
        self.gamePhase = None

        # Punishments to be received at reward calculation if previously did illegal actions.
        self.tinyPunish = False
        self.smallPunish = False
        self.mediumPunish = False
        self.strongPunish = False
        self.lockInPunish = False
        self.lost = False
        self.extraReward = 0

        self.localHeroID = 1
        self.localItemID = 1

        # make sure to close store before getting state!
        # possible states:
        # select: selecting an item
        # choose: choose an underlord
        # preparing: full control in between combat rounds
        # combat: fight is happening
        # countdown: same as preparing - assuming its not SELECT or CHOOSE so check for those first

        self.UnitItemMove = ['preparing', 'countdown']  # Note, might need to remove COUNTDOWN if it delays too much
        self.StoreInteract = ['preparing', 'combat', 'countdown']
        self.SelectUnderlord = ['choose']
        self.SelectItem = ['select']

        self.choseItem = False
        self.rerolledItem = False
        self.selected = False

        self.heroToMove = None
        self.itemToMove = None

        self.speedUpFactor = 1

        self.shopSleepTime = 0.3 / self.speedUpFactor
        self.mouseSleepTime = 0.2 / self.speedUpFactor

        self.shop = Shop()
        self.screenOffsetX, self.screenOffsetY = loadScreenOffset()
        self.HUD = HUD(self.screenOffsetX, self.screenOffsetY)
        self.gameStateLoader = state(self.screenOffsetX, self.screenOffsetY)
        self.itemIDmap = self.items.itemIDMap
        self.underlords = Underlords()
        self.bench = numpy.zeros([1, 8])
        self.board = numpy.zeros([4, 8])
        # try:

        # except:
        # print('Issue loading profiles')

        self.shopChoices = None
        self.storeMap = [350, 450, 575, 700, 800]  # super dumb and outdated to get X offset for purchase unit. change
        # later if I ever feel like it
        self.purchaseHistory = []
        self.gold = 0
        self.health = 0
        self.remainingEXP = 1
        self.level = 0
        self.round = 0
        self.prevHP = 100
        self.freeRerollAvailable = False
        self.lockedIn = False
        self.leveledUp = False
        self.lastLockedInRound = -1

        self.currentTime = 0
        self.elapsedTime = 0
        # self.pickTime = False

        self.otherPlayersDict = {2: {'slot': 2, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 3: {'slot': 3, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 4: {'slot': 4, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 5: {'slot': 5, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 6: {'slot': 6, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 7: {'slot': 7, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 8: {'slot': 8, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 }

        # shopImages, classes, value, inspect, statesList = self.shop.labelShop()

        # self.shopImages

        self.gameCrop = None

        self.shopLabels = []
        self.shopImages = []
        self.oldShopImages = []
        self.benchLabels = []
        self.benchHeroes = [None, None, None, None, None, None, None, None]
        self.boardLabels = numpy.full((4, 8), None)
        self.boardHeroes = numpy.full((4, 8), None)
        self.itemObjects = numpy.full((3, 4), None)
        self.itemlabels = numpy.full((3, 4), None)
        self.underlord = None

        self.checkState = True  # note make sure to False this for production

        # self.boardHeroes = numpy.empty((4, 8))
        # self.boardHeroes[:] = None
        self.boardHeroes = self.boardHeroes.tolist()

        self.levelThresh = 3  # level threshold for tiering up a unit

        self.hudLabel = None
        self.toBuy = None
        self.shopFrame = Frame(
            master=rootWindow,
            relief=tkinter.RAISED,
            borderwidth=1
        )
        # tempImage = ImageTk.PhotoImage(shopImages[0])

        # Initialize 5 pictures for shop, 5 purchase buttons
        for i in range(5):
            # print(f"Confidence {statesList[i] * 100}")
            label = Label(master=self.shopFrame, foreground='white', background='black',
                          text=f"Ignore", compound='top')
            label.grid(row=0, column=i, padx=5, pady=5)
            self.shopLabels.append(label)

            if not training:
                button = tkinter.Button(
                    master=self.shopFrame,
                    text="Purchase",
                    width=10,
                    height=1,
                    bg="blue",
                    fg="yellow",
                    command=lambda idx=i: self.buy(idx=idx)
                )
                button.grid(row=1, column=i)

        self.itemFrame = Frame(master=self.shopFrame, relief=tkinter.RAISED, borderwidth=1)
        self.itemFrame.grid(row=0, column=5)

        if not training:
            for i in range(3):
                for j in range(4):

                    label = Label(master=self.itemFrame, foreground='white', background='black',
                                  text=f"", compound='top')
                    label.grid(row=2 * i, column=j, padx=5, pady=5)

                    self.itemlabels[i][j] = label

                    if not training:
                        button = tkinter.Button(
                            master=self.itemFrame,
                            text="Move",
                            width=10,
                            height=1,
                            bg="blue",
                            fg="yellow",
                            command=lambda X=i, y=j: self.selectItem(x=X, y=y)
                        )
                        button.grid(row=2 * i + 1, column=j)
        else:
            for i in range(3):
                for j in range(4):
                    label = Label(master=self.itemFrame, foreground='white', background='black',
                                  text=f"", compound='top')
                    label.grid(row=i, column=j, padx=5, pady=5)

                    self.itemlabels[i][j] = label

        hudRow = 14

        # 8 bench portrait slots
        for x in range(8):
            newLabel = Label(master=self.shopFrame, foreground='white', background='black',
                             text=f"", compound='top')
            newLabel.grid(row=hudRow + 2, column=x, padx=5, pady=5)
            self.benchLabels.append(newLabel)
            if not training:
                tempButton = tkinter.Button(master=self.shopFrame, text="Move", width=4, height=1,
                                            command=lambda pos=x, idx=-1: self.moveUnit(x=pos, y=idx))
                tempButton.grid(row=hudRow + 3, column=x)

        # self.shopFrame.grid(row=1, column=0, pady=0, columnspan=5)
        self.hudLabel = Label(master=self.shopFrame, foreground='white', background='black',
                              text="Hi", compound='top')

        self.hudLabel.grid(row=hudRow, column=4, padx=5, pady=5)

        self.rerollButton = tkinter.Button(
            master=self.shopFrame,
            text="Reroll",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=self.rerollStore
        )
        self.rerollButton.grid(row=hudRow, column=3)

        self.buyItem1 = tkinter.Button(
            master=self.shopFrame,
            text="buyItem1",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=lambda pos=0: self.selectItem(selection=pos)
        )
        self.buyItem1.grid(row=hudRow + 1, column=0)
        self.buyItem2 = tkinter.Button(
            master=self.shopFrame,
            text="buyItem2",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=lambda pos=1: self.selectItem(selection=pos)
        )
        self.buyItem2.grid(row=hudRow + 1, column=1)
        self.buyItem3 = tkinter.Button(
            master=self.shopFrame,
            text="buyItem3",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=lambda pos=2: self.selectItem(selection=pos)
        )
        self.buyItem3.grid(row=hudRow + 1, column=2)
        self.buyItem4 = tkinter.Button(
            master=self.shopFrame,
            text="buyItem4",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=lambda pos=3: self.selectItem(selection=pos)
        )
        self.buyItem4.grid(row=hudRow + 1, column=3)

        self.testButton = tkinter.Button(
            master=self.shopFrame,
            text='Test Button',
            width=10,
            height=1,
            bg='blue',
            fg='yellow',
            # command=lambda underlor='healing_tank', selecty=3: self.buyUnderlord(underlord=underlor, selection=selecty)
            command=lambda x=0, y=0: self.testFunction(x, y)
        )
        self.testButton.grid(row=hudRow + 1, column=4)

        self.refreshStore = tkinter.Button(
            master=self.shopFrame,
            text='Refresh Store',
            width=10,
            height=1,
            bg='blue',
            fg='yellow',
            command=self.updateShop
        )
        self.refreshStore.grid(row=hudRow + 1, column=5)

        self.sellButton = tkinter.Button(
            master=self.shopFrame,
            text="Sell",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=self.sellHero
        )
        self.sellButton.grid(row=hudRow, column=2)

        self.lockInButton = tkinter.Button(
            master=self.shopFrame,
            text="Lock in",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=self.lockIn
        )
        self.lockInButton.grid(row=hudRow, column=1)

        self.clickUpButton = tkinter.Button(
            master=self.shopFrame,
            text="Click Up",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=self.clickUp
        )
        self.clickUpButton.grid(row=hudRow, column=0)

        for i in range(4):
            for j in range(8):
                newLabel = Label(master=self.shopFrame, foreground='white', background='black',
                                 text=f"", compound='top')
                newLabel.grid(row=3 + (2 * i), column=j, padx=3, pady=2)
                self.boardLabels[i][j] = newLabel

                if not training:
                    tempButton = tkinter.Button(master=self.shopFrame, text="Move", width=4, height=1,
                                                command=lambda pos=j, idx=i: self.moveUnit(x=pos, y=idx))
                    tempButton.grid(row=4 + (2 * i), column=j)

        self.shopFrame.pack()

    def resetEnv(self, training=False):

        if self.server:
            return 1

        # print('rest ENV CALLED!')
        self.gamePhase = None
        # self.gameStateLoader = state()

        # Punishments to be received at reward calculation if previously did illegal actions.
        self.smallPunish = False
        self.mediumPunish = False
        self.strongPunish = False
        self.lost = False

        self.localHeroID = 1
        self.localItemID = 1

        # make sure to close store before getting state!
        # possible states:
        # select: selecting an item
        # choose: choose an underlord
        # preparing: full control in between combat rounds
        # combat: fight is happening
        # countdown: same as preparing - assuming its not SELECT or CHOOSE so check for those first

        self.UnitItemMove = ['preparing', 'countdown']  # Note, might need to remove COUNTDOWN if it delays too much
        self.StoreInteract = ['preparing', 'combat', 'countdown']
        self.SelectUnderlord = ['choose']
        self.SelectItem = ['select']

        self.choseItem = False
        self.rerolledItem = False
        self.selected = False

        self.heroToMove = None
        self.itemToMove = None

        self.speedUpFactor = 1

        self.shopSleepTime = 0.4 / self.speedUpFactor
        self.mouseSleepTime = 0.25 / self.speedUpFactor

        self.bench = numpy.zeros([1, 8])
        self.board = numpy.zeros([4, 8])
        self.shopChoices = None
        self.storeMap = [350, 450, 575, 700, 800]  # super dumb and outdated to get X offset for purchase unit. change
        # later if I ever feel like it
        self.purchaseHistory = []
        self.gold = 0
        self.health = 0
        self.remainingEXP = 1
        self.level = 0
        self.round = 0
        self.prevHP = 100
        self.freeRerollAvailable = False
        self.lockedIn = False
        self.leveledUp = False

        self.finalPlacement = 0
        self.rerollCost = 2
        self.underlordPicks = None
        self.itemPicks = None
        self.shopUnits = None
        self.gsiItems = None
        self.combatType = 0
        self.combatResult = -1
        self.wins = 0
        self.losses = 0
        self.round = 0
        self.prevHP = 100
        self.newRoundStarted = False
        self.currentTime = 0
        self.elapsedTime = 0
        self.lastLockedInRound = -1
        self.tinyPunish = False
        self.smallPunish = False
        self.mediumPunish = False
        self.strongPunish = False
        self.lockInPunish = False
        self.bigPunish = False
        self.extraReward = 0

        # self.allowMove = False
        # self.pickTime = False
        # self.pickTime = False

        self.rewardSummary = {'purchases': 0, 'roundsSurvived': 0, 'finalPosition': 0, 'unitLevelUp': 0,
                              'mainLevelUp': 0, 'extra': 0, 'lockIn': 0, 'itemPick': 0}
        self.otherPlayersDict = {2: {'slot': 2, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 3: {'slot': 3, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 4: {'slot': 4, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 5: {'slot': 5, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 6: {'slot': 6, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 7: {'slot': 7, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 8: {'slot': 8, 'health': 100, 'gold': 0, 'level': 2, 'units': []},
                                 }

        # shopImages, classes, value, inspect, statesList = self.shop.labelShop()

        # self.shopImages

        self.oldShopImages = self.shopImages
        self.shopImages = []
        self.benchHeroes = [None, None, None, None, None, None, None, None]
        self.boardHeroes = numpy.full((4, 8), None)
        self.itemObjects = numpy.full((3, 4), None)

        self.underlord = None

        self.gameCrop = None

        self.checkState = False  # note make sure to False this for production

        # self.boardHeroes = numpy.empty((4, 8))
        # self.boardHeroes[:] = None
        self.boardHeroes = self.boardHeroes.tolist()

        self.levelThresh = 3  # level threshold for tiering up a unit

        self.toBuy = None
        # tempImage = ImageTk.PhotoImage(shopImages[0])

        # Initialize 5 pictures for shop, 5 purchase buttons
        for i in range(5):
            # print(f"Confidence {statesList[i] * 100}")
            self.shopLabels[i].config(foreground='white', background='black',
                                      text=f"Ignore", compound='top', image='')

        for i in range(3):
            for j in range(4):
                self.itemlabels[i][j].config(foreground='white', background='black',
                                             text=f"", compound='top', image='')

        hudRow = 14

        # 8 bench portrait slots
        for x in range(8):
            self.benchLabels[x].config(foreground='white', background='black',
                                       text=f"", compound='top', image='')

        # self.shopFrame.grid(row=1, column=0, pady=0, columnspan=5)
        self.hudLabel.config(foreground='white', background='black',
                             text="Hi", compound='top', image='')

        for i in range(4):
            for j in range(8):
                self.boardLabels[i][j].config(foreground='white', background='black',
                                              text=f"", compound='top', image='')

        self.shopFrame.pack()

    def testFunction(self, param1, param2):
        # print(self.HUD.getClockTimeLeft())

        if self.localItemID < 4:
            for i in range(3):
                for j in range(4):
                    melee = False
                    ranged = False
                    preventMana = False
                    boughtItemId = 7
                    name = 'tester item' + str(i) + str(j)
                    self.itemObjects[i][j] = Item(name, (i, j),
                                                  ID=2,
                                                  melee=melee,
                                                  ranged=ranged,
                                                  preventMana=preventMana,
                                                  localID=self.localItemID,
                                                  legacyID=boughtItemId)
                    self.localItemID += 1
                    self.itemlabels[i][j].config(text=name)
        print(self.getObservation())
        # print(self.getGamePhase())
        # print(f"Punishment: {self.getPunishment()}")
        self.boardUnitCount(True)

        # self.itemObjects[0][1] = Item('claymore', (0,1), melee=True)
        # self.itemlabels[0][1].config(text='claymore')
        #
        # mouse1.position = (self.itemMoveX + (self.itemMoveXOffset * self.itemObjects[0][1].coords[1]),
        #                    self.itemMoveY + (self.itemMoveYOffset * self.itemObjects[0][1].coords[0]))
        # self.updateWindowCoords()
        # start_time = time.time()
        # print(self.getObservation())
        # print("--- %s seconds to get observation ---" % (time.time() - start_time))

        # if self.underlordPicks is not None or self.itemPicks is not None:
        #     print(f"result of running out: {self.timeRunningOut()}")

        # self.startNewGame()

        #
        # self.buyItem(0,[(-1, 10101)])
        # self.buyItem(0, [(-1, 10101)])
        # self.buyItem(0, [(-1, 10106)])
        # self.resetEnv()
        # print(self.finished())

    def returnToMainScreen(self):
        self.updateWindowCoords()
        mouse1.position = (self.shopX, self.shopY + 100)
        time.sleep(1)
        mouse1.click(Button.left, 1)
        time.sleep(1)
        mouse1.click(Button.left, 1)
        time.sleep(2)
        self.gameStateLoader.currentPhase = None
        time.sleep(8)

    def startNewGame(self):

        if self.server:
            return 1

        # print('got to startnewGame')
        self.updateWindowCoords()

        mouse1.position = (self.shopX, self.shopY + 720)
        time.sleep(self.shopSleepTime * 3)
        mouse1.click(Button.left, 1)

        time.sleep(self.shopSleepTime * 3)

        mouse1.position = (self.x + 700, self.shopY + 200)
        time.sleep(self.shopSleepTime)
        mouse1.click(Button.left, 1)
        time.sleep(self.shopSleepTime)
        mouse1.click(Button.left, 1)
        time.sleep(self.shopSleepTime)
        mouse1.click(Button.left, 1)

        mouse1.position = (self.shopX, self.shopY + 720)
        time.sleep(self.shopSleepTime)
        mouse1.click(Button.left, 1)
        time.sleep(self.shopSleepTime)
        mouse1.click(Button.left, 1)
        time.sleep(self.shopSleepTime)
        mouse1.click(Button.left, 1)
        try:
            self.resetEnv()
        except:
            print('reset Env died')

        flag = True

        while flag:
            # time.sleep(0.2) #There is sleep inside the closing store inside getGamePhase
            phase = self.getGamePhase()
            print('gamephase: ')
            print(phase)
            if phase is not None:
                flag = False

        # self.closeStore()
        # print('sleeping for 5s')
        time.sleep(1)
        # print('done sleeping')
        self.finalPlacement = 0
        self.round = 0
        self.openStore()
        time.sleep(1)
        # self.openStore()
        # time.sleep(1)
        # self.openStore()
        # time.sleep(1)
        # print('done opening the store')

    def pickTime(self):
        return (self.itemPicks is not None) or (self.underlordPicks is not None)

    def allowMove(self):
        # return True
        thresh = 20
        if self.round < 3:  # arbitrary large number cause you have a ton more time in the beginning
            thresh = 35
        return self.combatType == 0 and not self.pickTime() and (self.currentTime > 2) and (self.currentTime < thresh)

    def proper_round(self, num, dec=0):
        if (str(num).find('.') == -1):
            return float(num)
        num = str(num)[:str(num).index('.') + dec + 2]
        if num[-1] >= '5':
            a = num[:-2 - (not dec)]  # integer part
            b = int(num[-2 - (not dec)]) + 1  # decimal part
            return float(a) + b ** (-dec + 1) if a and b == 10 else float(a + str(b))
        return float(num[:-1])

    def getObservation(self):

        self.boardUnitCount(True)

        overallTime = time.time()
        # print("--- %s seconds to get observation ---" % (time.time() - overallTime))

        # start_time = time.time()
        # position = self.finished()
        # print("--- %s seconds to get position ---" % (time.time() - start_time))

        # if self.finalPlacement != 0:
        #     obs = (
        #         self.finalPlacement, 0, 0, 0, 0, self.round, 0, 0, 0,
        #         [0, 0], 0, 0, 0, 0,
        #         # store heros
        #         [0, 0, 0, 0, 0],
        #         # bench heroes
        #         [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
        #         [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
        #         # board heroes
        #         [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
        #         [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
        #         [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
        #         # underlords to pick
        #         [0, 0, 0, 0, 0],
        #         # local Items,
        #         [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
        #         [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
        #         # items to pick
        #         [0, 0, 0],
        #         # other players
        #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        #     )
        #     return obs

        # self.updateWindowCoords() #adds like 0.2seconds of delay minimum longer the slower the VM is...
        # phase = self.getGamePhase(skipCheck=True)

        # print("--- %s seconds to get past gamephase ---" % (time.time() - overallTime))

        # if phase not in ['select', 'choose']:

        # making sure it is not time to pick an underlord or
        if self.itemPicks is None and self.underlordPicks is None:
            self.updateShop(skipCheck=True)

        # gamePhase = -1
        #
        # if phase == 'select':
        #     gamePhase = 1
        # elif phase == 'choose':
        #     gamePhase = 2
        # elif phase == 'preparing':
        #     gamePhase = 3
        # elif gamePhase == 'combat':
        #     gamePhase = 4
        # elif gamePhase == 'countdown':
        #     gamePhase = 5

        heroToMove = None

        if self.heroToMove is not None:

            isUnderlord = 0

            if self.heroToMove.underlord:
                isUnderlord = 2
            else:
                isUnderlord = 1

            heroToMove = [self.heroToMove.coords[0] + 1, self.heroToMove.coords[1] + 1]
        else:
            heroToMove = [0, 0]

        itemToMove = None

        if self.itemToMove == None:
            itemToMove = 0
        else:
            itemToMove = self.itemToMove.localID

        shopHeros = []

        try:

            for idx in range(5):
                heroData = self.underlords.underlordDataID[self.shopUnits[idx]]
                name = heroData['texturename']
                uniqueID = self.shop.classIDMap[name]

                shopHeros.append(int(uniqueID) + 1)
                if (int(uniqueID) + 1) > 70:
                    raise RuntimeError('error 1')
        except:  # meaning we haven't yet received data about the store units
            shopHeros = [0, 0, 0, 0, 0]

        benchHeros = []
        playerHeroTier = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        playerHeroCost = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(8):
            tempHero = None

            if self.benchHeroes[i] is not None:

                isUnderlord = 0

                if self.benchHeroes[i].underlord:
                    isUnderlord = 2
                else:
                    isUnderlord = 1

                itemID = 0

                if self.benchHeroes[i].item is not None:
                    itemID = self.benchHeroes[i].item.localID

                playerHeroTier[i] = self.benchHeroes[i].tier
                playerHeroCost[i] = self.benchHeroes[i].gold
                tempHero = [self.benchHeroes[i].id + 1,
                            # self.benchHeroes[i].localID, 
                            # self.benchHeroes[i].tier,
                            # self.benchHeroes[i].gold,
                            itemID,
                            self.benchHeroes[i].coords[0],
                            self.benchHeroes[i].coords[1] + 1,
                            isUnderlord]

                if (self.benchHeroes[i].id + 1) > 71:
                    raise RuntimeError('error 2')
                if self.benchHeroes[i].localID > 249:
                    raise RuntimeError('error 3')
                if self.benchHeroes[i].tier > 3:
                    raise RuntimeError('error 4')
                if self.benchHeroes[i].gold > 5:
                    raise RuntimeError('error 5')
                if itemID > 13:
                    raise RuntimeError('error 6')
                if (self.benchHeroes[i].coords[0] + 1) > 8:
                    raise RuntimeError('error 7')
                if (self.benchHeroes[i].coords[1] + 1) > 8:
                    raise RuntimeError('error 7')
                if isUnderlord > 2:
                    raise RuntimeError('error 8')

            else:
                tempHero = [0, 0, 0, 0, 0]
            benchHeros.append(tempHero)

        # 11 because I have to take into account the Underlord!!!
        boardHeroes = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        idx = 0

        for i in range(4):
            for j in range(8):
                tempHero = None

                if self.boardHeroes[i][j] is not None:

                    isUnderlord = 0

                    if self.boardHeroes[i][j].underlord:
                        isUnderlord = 2
                    else:
                        isUnderlord = 1

                    itemID = 0

                    if self.boardHeroes[i][j].item is not None:
                        itemID = self.boardHeroes[i][j].item.localID

                    tempHero = [self.boardHeroes[i][j].id + 1,
                                # self.boardHeroes[i][j].localID,
                                # self.boardHeroes[i][j].tier,
                                # self.boardHeroes[i][j].gold,
                                itemID,
                                self.boardHeroes[i][j].coords[0],
                                self.boardHeroes[i][j].coords[1] + 1,
                                isUnderlord]

                    if (self.boardHeroes[i][j].id + 1) > 71:
                        raise RuntimeError('error 11')
                    if self.boardHeroes[i][j].localID > 249:
                        raise RuntimeError('error 12')
                    if self.boardHeroes[i][j].tier > 3:
                        raise RuntimeError('error 13')
                    if self.boardHeroes[i][j].gold > 5:
                        raise RuntimeError('error 14')
                    if itemID > 13:
                        raise RuntimeError('error 15')
                    if (self.boardHeroes[i][j].coords[0] + 1) > 8:
                        raise RuntimeError('error 16')
                    if (self.boardHeroes[i][j].coords[1] + 1) > 8:
                        raise RuntimeError('error 17')
                    if isUnderlord > 2:
                        raise RuntimeError('error 18')

                    playerHeroTier[8 + idx] = self.boardHeroes[i][j].tier
                    playerHeroCost[8 + idx] = self.boardHeroes[i][j].gold
                    boardHeroes[idx] = tempHero
                    idx += 1

        underlordsPick = []

        itemPick = []

        if self.itemPicks is not None:

            # items = self.items.checkItems()

            for i in range(3):
                try:
                    item = self.items.itemDataID[self.itemPicks[i]]
                    name = item['icon']
                    properID = self.items.itemIDMap[name]
                    itemPick.append(properID)

                    if properID > 69:
                        raise RuntimeError('error 19')
                except:
                    print(self.itemIDmap)
                    print(item)
                    raise RuntimeError('Error trying to observe items')

        else:
            itemPick = [0, 0, 0]

        if self.underlordPicks is not None:

            # underlords = self.underlords.checkUnderlords()

            for i in range(4):
                underlord = self.underlordPicks[i]

                underlordsPick.append(underlord[0])
                underlordsPick.append(underlord[1])

                if underlord[0] > 4:
                    raise RuntimeError('error 20')
                if underlord[1] > 2:
                    raise RuntimeError('error 21')

                # underlordID = None
                #
                # if underlord == 'aggressive_tank':
                #     underlordID = 63
                # elif underlord == 'healing_tank':
                #     underlordID = 64
                # elif underlord == 'damage_support':
                #     underlordID = 65
                # elif underlord == 'healing_support':
                #     underlordID = 66
                # elif underlord == 'healing_stealing':
                #     underlordID = 67
                # elif underlord == 'rapid_furball':
                #     underlordID = 68
                # elif underlord == 'high_damage_dealer':
                #     underlordID = 69
                # elif underlord == 'support_damage_dealer':
                #     underlordID = 70
                # else:
                #     raise RuntimeError("Found a no match for underlord in obs!")
                # underlordsPick.append(underlordID)

        else:
            underlordsPick = [0, 0, 0, 0, 0, 0, 0, 0]

        localItems = []

        for i in range(3):
            limit = 4
            if i == 2:  # Only getting the first 10 items, might be an issue once the bot has more than 10 items but eh
                limit -= 2
            for j in range(limit):
                if self.itemObjects[i][j] is not None:
                    item = self.itemObjects[i][j]
                    heroID = 0

                    if item.hero is not None:
                        heroID = item.hero.localID

                    # localItems.append([item.ID + 1, item.localID, heroID, item.coords[0] + 1, item.coords[1] + 1])
                    localItems.append([item.ID + 1, item.localID, item.coords[0] + 1, item.coords[1] + 1])

                    if item.ID > 69:
                        raise RuntimeError('error 22')
                    if item.localID > 13:
                        raise RuntimeError('error 23')
                    if heroID > 249:
                        raise RuntimeError('24')
                    if (item.coords[0] + 1) > 3:
                        raise RuntimeError('25')
                    if (item.coords[1] + 1) > 4:
                        raise RuntimeError('26')

                else:
                    localItems.append([0, 0, 0, 0])
                    # localItems.append([0, 0, 0, 0, 0])

        rerolledItem = 0

        if self.rerolledItem:
            rerolledItem = 1

        if (self.currentTime < 3) or self.pickTime():
            self.gameCrop = main.imageGrab(w=1152, h=864)
            self.currentTime = self.HUD.getClockTimeLeft(self.gameCrop)
            self.elapsedTime = time.time()
        else:
            self.currentTime -= (time.time() - self.elapsedTime)
            self.elapsedTime = time.time()
            self.gameCrop = None

        lockedIn = 1

        if not self.lockedIn:
            lockedIn = 0

        otherPlayers = []

        for otherPlayer in self.otherPlayersDict:

            otherPlayerTiers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            otherPlayerHeros = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            other = self.otherPlayersDict[otherPlayer]
            temp = [other['slot'], other['health'], other['gold'], other['level']]

            units = other['units']
            idx = 0

            for unit in units:
                tier = unit['rank']
                tempID = unit['unit_id']
                fullData = self.underlords.underlordDataID[tempID]

                if ('texturename' not in fullData) or ('can_be_sold' not in unit):
                    continue
                if not unit['can_be_sold']:
                    continue

                name = fullData['texturename']

                if name == 'anessix' or name == 'hobgen' or name == 'jull' or name == 'enno':
                    continue

                goodID = self.shop.classIDMap[name] + 1
                # print(f"Adding {name}-{tier}-{goodID}")
                # temp.append(goodID)
                # temp.append(tier)
                otherPlayerTiers[idx] = tier
                otherPlayerHeros[idx] = goodID
                idx += 1

                if other['slot'] > 8:
                    raise RuntimeError('error 27')
                if other['health'] > 100:
                    raise RuntimeError('error 28')
                if other['gold'] > 99:
                    raise RuntimeError('error 29')
                if other['level'] > 10:
                    raise RuntimeError('error 30')
                if goodID > 70:
                    raise RuntimeError('error 31')
                if tier > 3:
                    raise RuntimeError('error 32')

            # blankUnits = 10 - idx  # adding blank 0's for units on board if there are less than 10 of them
            # 
            # for i in range(blankUnits):
            #     temp.append(0)
            #     temp.append(0)
            temp.append(otherPlayerTiers)
            temp.append(otherPlayerHeros)
            otherPlayers.append(temp)

        finalTime = int(self.proper_round(self.currentTime)) + 1
        if finalTime < 0:
            finalTime = 0

        punishLockIn = 0
        if self.round == self.lastLockedInRound:
            punishLockIn = 1

        # print('other player1:')
        # print(otherPlayers[1])
        obs = (
            self.finalPlacement, [self.health / 100], [self.gold / 100], [self.level / 10], [self.remainingEXP / 50],
            [self.round / 50], lockedIn,
            punishLockIn, self.combatType,
            heroToMove, itemToMove, self.rerollCost, rerolledItem, [finalTime / 30],
            # store heros
            shopHeros,
            playerHeroTier,
            playerHeroCost,
            # bench heroes
            benchHeros[0], benchHeros[1], benchHeros[2], benchHeros[3], benchHeros[4], benchHeros[5], benchHeros[6],
            benchHeros[7],
            # board heroes
            boardHeroes[0], boardHeroes[1], boardHeroes[2], boardHeroes[3], boardHeroes[4], boardHeroes[5],
            boardHeroes[6], boardHeroes[7], boardHeroes[8], boardHeroes[9], boardHeroes[10],
            # underlords to pick
            underlordsPick,
            # local Items,
            localItems[0], localItems[1], localItems[2], localItems[3], localItems[4], localItems[5],
            localItems[6], localItems[7], localItems[8], localItems[9],
            # localItems[10], localItems[11],
            # items to pick
            itemPick,
            # other players
            otherPlayers[0][0], [otherPlayers[0][1] / 100], [otherPlayers[0][2] / 100], [otherPlayers[0][3] / 10],
            otherPlayers[0][4], otherPlayers[0][5],
            otherPlayers[1][0], [otherPlayers[1][1] / 100], [otherPlayers[1][2] / 100], [otherPlayers[1][3] / 10],
            otherPlayers[1][4], otherPlayers[1][5],
            otherPlayers[2][0], [otherPlayers[2][1] / 100], [otherPlayers[2][2] / 100], [otherPlayers[2][3] / 10],
            otherPlayers[2][4], otherPlayers[2][5],
            otherPlayers[3][0], [otherPlayers[3][1] / 100], [otherPlayers[3][2] / 100], [otherPlayers[3][3] / 10],
            otherPlayers[3][4], otherPlayers[3][5],
            otherPlayers[4][0], [otherPlayers[4][1] / 100], [otherPlayers[4][2] / 100], [otherPlayers[4][3] / 10],
            otherPlayers[4][4], otherPlayers[4][5],
            otherPlayers[5][0], [otherPlayers[5][1] / 100], [otherPlayers[5][2] / 100], [otherPlayers[5][3] / 10],
            otherPlayers[5][4], otherPlayers[5][5],
            otherPlayers[6][0], [otherPlayers[6][1] / 100], [otherPlayers[6][2] / 100], [otherPlayers[6][3] / 10],
            otherPlayers[6][4], otherPlayers[6][5]

            # otherPlayers[1], otherPlayers[2], otherPlayers[3], otherPlayers[4], otherPlayers[5],
            # otherPlayers[6],
        )

        # print("--- %s seconds to get clock observation ---" % (time.time() - clockTime))

        # print("--- %s seconds to get observation ---" % (time.time() - overallTime))

        return obs

    def act(self, action, x, y, selection=None):

        tieredUp = None
        firstPlace = 10
        earnedMoney = -1

        acted = -1

        hadToPick = self.pickTime()

        if action == 0:
            # self.rerollStore()
            # print('rerolling')
            print("wanted to reroll")
        elif action == 1:
            self.lockIn()
            print('lock in')
        elif action == 2:
            self.clickUp()
            print('click up')
        elif action == 3:
            tieredUp = self.buy(x)
            print('buy')
        elif action == 4:
            earnedMoney = self.sellHero()
            print('sell hero')
        elif action == 5:
            acted = self.selectItem(x, y)
            print('select item')
        elif action == 6:
            self.moveUnit(x, y)
            print('move unit7')

        reward = 0

        if hadToPick:

            if acted < 1:
                print(f"it dun goofed: {acted}")
                res = self.timeRunningOut()
                reward += res
                self.rewardSummary['itemPick'] += res
                print(f"extra punish from item: {res}")
            else:
                print("It chose something...at least")

        if self.extraReward > 0:
            reward += self.extraReward
            self.rewardSummary['extra'] += self.extraReward
            self.extraReward = 0

        if self.lockInPunish:
            self.lockInPunish = False
            reward -= firstPlace * 0.0005
            self.rewardSummary['lockIn'] -= firstPlace * 0.0005

        # if self.tinyPunish:
        #     self.tinyPunish = False
        #     reward -= firstPlace * 0.0001
        # if self.smallPunish:
        #     self.smallPunish = False
        #     reward -= firstPlace * 0.001
        # if self.mediumPunish:
        #     self.mediumPunish = False
        #     reward -= firstPlace * 0.01
        # if self.strongPunish:
        #     self.strongPunish = False
        #     reward -= firstPlace * 0.1

        # for i in range(8):
        #     if self.benchHeroes[i] is not None:
        #         numBenchHeroes += 1
        #
        # if (tieredUp != 10) and (tieredUp != 11):
        #     if (not self.leveledUp) or (numBenchHeroes == 0):
        #         for i in range(4):
        #             for j in range(8):
        #                 if self.boardHeroes[i][j] is not None:
        #                     if not self.boardHeroes[i][j].underlord:
        #                         numHeroes += 1
        #
        #         reward -= (self.level - numHeroes) * (firstPlace * 0.05)

        # punish for having too much gold regardless
        if self.gold > 40:
            reward -= firstPlace * 0.005

        # if action in [0, 2, 3]:
        if action in [2, 3]:

            if self.gold >= 30:
                reward += firstPlace * 0.01
                self.rewardSummary['purchases'] += firstPlace * 0.01
            elif self.gold >= 20:
                reward += firstPlace * 0.0025
                self.rewardSummary['purchases'] += firstPlace * 0.0025
            elif self.gold >= 10:
                reward += firstPlace * 0.001
                self.rewardSummary['purchases'] += firstPlace * 0.001

        # note - to do : take into account tier of unit tiered up

        if tieredUp == 10:
            reward += firstPlace * 0.08
            self.rewardSummary['unitLevelUp'] += firstPlace * 0.08
        elif tieredUp == 11:
            reward += firstPlace * 0.3
            self.rewardSummary['unitLevelUp'] += firstPlace * 0.3

        if self.leveledUp:
            # don't want to reward for rushing early levels as I think that's just dumb
            if (self.level > 3):
                # if (self.level > 4) and ((self.boardUnitCount() + 1) >= self.level):
                unitCount = self.boardUnitCount()
                if unitCount > 0:
                    unitCount + 1  # adding +1 since we just leveled up, there is no way to have # units = level
                # award = pow(self.boardUnitCount()*self.level, 1.2)/(1000/firstPlace)
                award = (unitCount / self.level) * 0.1 * firstPlace
                # award = 10 + firstPlace * 0.00017 * (self.level ** 3) * ((self.boardUnitCount()+1) / self.level)
                # print(f"Awarded: {award} for leveling up with: {self.boardUnitCount()} heroes!")
                reward += award
                self.rewardSummary['mainLevelUp'] += award
                self.leveledUp = False

        # if earnedMoney != -1:
        #     reward += firstPlace * (1 - earnedMoney / 9) * 0.001

        # finished = self.finished()

        if self.finalPlacement != 0:

            if self.finalPlacement == 1:
                reward += firstPlace
                self.rewardSummary['finalPosition'] += firstPlace
            elif self.finalPlacement == 2:
                reward += firstPlace * 0.9
                self.rewardSummary['finalPosition'] += firstPlace * 0.9
            elif self.finalPlacement == 3:
                reward += firstPlace * 0.75
                self.rewardSummary['finalPosition'] += firstPlace * 0.75
            elif self.finalPlacement == 4:
                reward += firstPlace * 0.5
                self.rewardSummary['finalPosition'] += firstPlace * 0.5
            elif self.finalPlacement == 5:
                reward += firstPlace * 0.3
                self.rewardSummary['finalPosition'] += firstPlace * 0.3
            elif self.finalPlacement == 6:
                reward += firstPlace * 0.2
                self.rewardSummary['finalPosition'] += firstPlace * 0.2
            elif self.finalPlacement == 7:
                reward += firstPlace * 0.1
                self.rewardSummary['finalPosition'] += firstPlace * 0.1
            elif self.finalPlacement == 8:
                reward += firstPlace * 0
                self.rewardSummary['finalPosition'] += firstPlace * 0

            if self.round < 10:
                reward += firstPlace * 0.005 * self.round
                self.rewardSummary['roundsSurvived'] += firstPlace * 0.01 * self.round
            elif self.round < 18:
                reward += firstPlace * 0.01 * self.round
                self.rewardSummary['roundsSurvived'] += firstPlace * 0.02 * self.round
            elif self.round < 26:
                reward += firstPlace * 0.015 * self.round
                self.rewardSummary['roundsSurvived'] += firstPlace * 0.03 * self.round
            else:
                reward += firstPlace * 0.015 * 25
                self.rewardSummary['roundsSurvived'] += firstPlace * 0.03 * self.round

        # self.closeStore(skipCheck=True)

        return reward

    def finished(self):

        return self.gameStateLoader.detectGameEnd()

    def timeRunningOut(self):

        # if self.currentTime <= 10:
        firstPlace = 10

        if self.itemPicks is not None:

            for i in range(3):
                boughtItemId = self.itemPicks[i]
                item = self.items.itemDataID[boughtItemId]
                name = item['icon']
                if name not in self.items.banned:
                    self.selectItem(-1, i)
                    return -firstPlace * 0.03
        elif self.underlordPicks is not None:
            self.selectItem(-1, 0)
            return -firstPlace * 0.03
        # else:
        #     return 0

    def getGamePhase(self, skipCheck=False):

        if not skipCheck:
            self.closeStore(skipCheck=True)
            time.sleep(0.4)

        # start_time = time.time()
        # print("--- %s seconds to get actual get round ---" % (time.time() - start_time))

        # self.openStore(skipCheck=True)

        # self.gamePhase = self.gameStateLoader.getPhase()

        # self.round = self.HUD.getRound()
        return self.gameStateLoader.getPhase()

    def selectItem(self, x=-1, y=-1, selection=-1):

        # gamePhase = self.getGamePhase()

        # print(f"gamePhase: {gamePhase}")
        # x,y = self.switchXY(x, y)

        print(f"select item {x} - {y}")

        if self.pickTime():

            if self.itemPicks is not None:

                if y < 0 or y > 3:
                    # print('break 1')
                    self.mediumPunish = True
                    return -1

                return self.buyItem(y, self.itemPicks)

            elif self.underlordPicks is not None:

                if y < 0 or y > 3:
                    self.mediumPunish = True
                    # print('break 2')
                    return -1

                return self.buyUnderlord(self.underlordPicks, y)

        else:

            if not self.allowMove():
                self.mediumPunish = True
                return -1

            if self.heroToMove:
                # print("You have a hero selected to move, move it first!")
                self.smallPunish = True
                # print('break 3')
                return -1

            if x > 2 or y > 3:
                self.mediumPunish = True
                # print('uh oh 3')
                return -1

            if (y < 0) or (x < 0):
                self.mediumPunish = True
                return -1

            if self.itemObjects[x][y] is None:
                # print("there is no item to select here!")
                self.mediumPunish = True
                # print('break 4')
                return -1
            else:
                if y < 0 or y > 3:
                    self.mediumPunish = True
                    # print('break 5')
                    return -1
                if x < 0 or x > 2:
                    self.mediumPunish = True
                    # print('break 5')
                    return -1
                if self.itemObjects[x][y] is None:
                    self.smallPunish = True
                    # print('break 6')
                    return -1

                self.itemToMove = self.itemObjects[x][y]
                return 1

    def buyItem(self, selection, itemList):

        if selection > 3:
            self.mediumPunish = True
            return -1

        if selection == 3:
            if self.rerolledItem:

                self.strongPunish = True
                # print('break 7')
                return -1

            else:
                # self.updateWindowCoords()
                mouse1.position = (self.itemRerollX, self.itemRerollY)
                time.sleep(self.mouseSleepTime)
                mouse1.click(Button.left, 1)
                return 1
                # self.rerolledItem = True
                # self.choseItem = False
                # self.selected = False

        else:
            # self.updateWindowCoords()

            # self.rerolledItem = False
            # self.choseItem = True
            # self.selected = True

            idx = 0
            holderItem = None
            boughtItemId = itemList[selection]
            foundLocation = False

            item = self.items.itemDataID[boughtItemId]
            name = item['icon']

            if name in self.items.banned:
                self.strongPunish = True
                return -1

            # print(f"chose item: {name}")
            mouse1.position = (
                self.itemSelectX + (self.itemSelectXOffset * selection), self.itemSelectY)
            time.sleep(self.mouseSleepTime)

            while self.pickTime():
                mouse1.click(Button.left, 1)
                time.sleep(self.mouseSleepTime * 3)

            gsiItems = []

            if self.gsiItems is not None:

                for itemy in self.gsiItems:
                    gsiItems.append(itemy[1])

                gsiItems.sort()

            for i in range(3):
                for j in range(4):

                    itemObject = self.itemObjects[i][j]

                    # meaning we found where the new item went, but need to shift all the other items down 1
                    if holderItem is not None:
                        tempHolder = itemObject
                        self.itemObjects[i][j] = holderItem
                        self.itemObjects[i][j].x = i
                        self.itemObjects[i][j].y = j
                        self.itemlabels[i][j].config(text=holderItem.name)
                        holderItem = tempHolder

                        # meaning the next item doesn't exit, no more items left to shift
                        if holderItem is None:
                            return 1


                    # meaning it is our first item
                    elif gsiItems is None:
                        item = self.items.itemDataID[boughtItemId]
                        name = item['icon']
                        properID = self.items.itemIDMap[name]

                        melee = False
                        ranged = False
                        preventMana = False

                        if "melee_only" in self.items.itemData[name]:
                            melee = True
                        if "ranged_only" in self.items.itemData[name]:
                            ranged = True
                        if "requires_ability" in self.items.itemData[name]:
                            preventMana = True

                        holderItem = itemObject

                        self.itemObjects[i][j] = Item(name, (i, j),
                                                      ID=properID,
                                                      melee=melee,
                                                      ranged=ranged,
                                                      preventMana=preventMana,
                                                      localID=self.localItemID,
                                                      legacyID=boughtItemId)
                        self.localItemID += 1
                        self.itemlabels[i][j].config(text=name)

                        return 1

                    # meaning we are searching for a spot, and the current spots are taken
                    elif itemObject is not None:

                        # note I don't check the [0] (slot_index), I assume they are returned in order. If error
                        # check that

                        # found where the item we bought might go, need to check
                        # or we have found it previously, and are now shifting to after the existing duplicates

                        try:
                            temp = gsiItems[idx] == boughtItemId or foundLocation
                        except:
                            print(gsiItems)
                            print(idx)
                            raise RuntimeError("This fucking line")

                        if gsiItems[idx] == boughtItemId or foundLocation:

                            foundLocation = True
                            # if we already have this item before, then it goes to next spot
                            if itemObject.legacyID == boughtItemId:
                                continue
                            else:
                                # create a new local item and put it in the right spot
                                item = self.items.itemDataID[boughtItemId]
                                name = item['icon']
                                properID = self.items.itemIDMap[name]

                                melee = False
                                ranged = False
                                preventMana = False

                                if "melee_only" in self.items.itemData[name]:
                                    melee = True
                                if "ranged_only" in self.items.itemData[name]:
                                    ranged = True
                                if "requires_ability" in self.items.itemData[name]:
                                    preventMana = True

                                holderItem = itemObject

                                self.itemObjects[i][j] = Item(name, (i, j),
                                                              ID=properID,
                                                              melee=melee,
                                                              ranged=ranged,
                                                              preventMana=preventMana,
                                                              localID=self.localItemID,
                                                              legacyID=boughtItemId)
                                self.localItemID += 1
                                self.itemlabels[i][j].config(text=name)

                    # meaning that there are no existing copies of the item we just got
                    else:
                        item = self.items.itemDataID[boughtItemId]
                        name = item['icon']
                        properID = self.items.itemIDMap[name]
                        melee = False
                        ranged = False
                        preventMana = False

                        if "melee_only" in self.items.itemData[name]:
                            melee = True
                        if "ranged_only" in self.items.itemData[name]:
                            ranged = True
                        if "requires_ability" in self.items.itemData[name]:
                            preventMana = True

                        self.itemObjects[i][j] = Item(name, (i, j),
                                                      ID=properID,
                                                      melee=melee,
                                                      ranged=ranged,
                                                      preventMana=preventMana,
                                                      localID=self.localItemID,
                                                      legacyID=boughtItemId)
                        self.localItemID += 1
                        self.itemlabels[i][j].config(text=name)
                        return 1
                    idx += 1

    def buyUnderlord(self, underlords, selection):

        # self.updateWindowCoords()

        AnnaPreferences = [(2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7)]
        JullPreferences = [(0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (3, 0), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)]
        HobPreferences = [(2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7)]
        FurPreferences = [(1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]

        preferences = []
        ID = None
        name = None

        underlord = underlords[selection]

        if underlord[0] == 1:

            preferences = AnnaPreferences

            if underlord[1] == 0:  # damage support
                ID = 63
                name = 'damage_support'
            else:
                ID = 64
                name = 'healing_support'

        elif underlord[0] == 2:

            preferences = JullPreferences

            if underlord[1] == 0:  # agressive tank
                ID = 65
                name = 'aggressive_tank'
            else:
                ID = 66
                name = 'healing_tank'

        elif underlord[0] == 3:

            preferences = FurPreferences

            if underlord[1] == 0:  # healing stealing
                ID = 67
                name = 'healing_stealing'
            else:
                ID = 68
                name = 'rapid_furball'

        elif underlord[0] == 4:

            preferences = AnnaPreferences

            if underlord[1] == 0:  # high damage dealer
                ID = 69
                name = 'high_damage_dealer'
            else:
                ID = 70
                name = 'support_damage_dealer'
        else:
            # print('No clue what underlord that is!')
            return -1

        for x, y in preferences:

            if self.boardHeroes[x][y] is None:
                # print(f"Found a spot for underlord at: {x}-{y}")
                self.underlord = Hero(name, (y, x), self.underlordPics[name], True, ID=ID,
                                      localID=self.localHeroID, gold=0)
                self.localHeroID += 1
                self.updateHeroLabel(self.underlord)
                self.boardHeroes[x][y] = self.underlord

                mouse1.position = (self.itemSelectX - 20 + (self.itemSelectXOffset * selection), self.itemSelectY + 100)
                time.sleep(self.mouseSleepTime)

                while self.pickTime():
                    mouse1.click(Button.left, 1)
                    time.sleep(self.mouseSleepTime * 3)

                self.underlordPicks = None

                # if self.underlordPicks is not None:
                #     print("Underlord picks are still available")
                return 1

    def updateShop(self, units=True, hud=True, skipCheck=False):

        # if not skipCheck:
        #     self.openStore(update=units)
        #
        # shopImages, classes, value, inspect, statesList = self.shopChoices
        #
        # # start_time = time.time()
        # itemCounts = self.HUD.getHUD()
        # # print("--- %s seconds to get actual hud stats ---" % (time.time() - start_time))

        color = 'black'

        if self.lockedIn:
            color = 'gray'

        for i in range(5):

            try:
                heroName = self.underlords.underlordDataID[self.shopUnits[i]]['texturename']
                tempImage = self.profilePics[heroName]
                self.shopImages.append(tempImage)
                self.shopLabels[i].config(image=tempImage,
                                          text=f"{heroName}", bg=color)
            except:  # meaning we haven't recieved data for store yet
                return 1

        tempString = "\nUnit Count %d" % self.boardUnitCount() + "/%d" % self.level + "\nGold Count: %d" % self.gold \
                     + "\nHealth Count: %d" % self.health + "\nRemaining EXP: %d\n" % self.remainingEXP + "Rounds Won %d" % self.wins + "/%d" % self.round
        self.hudLabel.config(text=tempString)

        rerollText = "Reroll 2"

        if self.rerollCost == 0:
            # print('got free reroll')
            rerollText = 'Reroll 0'

        self.rerollButton.config(text=rerollText)

    def checkBetweenCombat(self):

        return self.combatType == 0 and self.underlordPicks is None and self.itemPicks is None and not self.checkState

    def sellHero(self):

        if not self.allowMove():
            self.mediumPunish = True
            return -1

        if self.heroToMove is None:
            return -1
        elif self.heroToMove.underlord:
            return -1

        x, y = self.heroToMove.coords
        earnedMoney = 0

        if self.heroToMove.item:
            self.heroToMove.item.hero = None

        if y == -1:
            mouse1.position = (self.benchX + (self.benchXOffset * x), self.benchY)
            if self.benchHeroes[x].item is not None:
                self.benchHeroes[x].item.hero = None
            earnedMoney = self.benchHeroes[x].gold + (self.benchHeroes[x].tier - 1) * 2
            self.resetLabel(self.benchHeroes[x])
            self.heroToMove = None
        else:

            x, y = self.switchXY(x, y)

            if self.boardHeroes[x][y] is None:
                self.mediumPunish = True
                return -1

            mouse1.position = (self.boardX + (self.boardXOffset * y), self.boardY + (self.boardYOffset * x))
            if self.boardHeroes[x][y].item is not None:
                self.boardHeroes[x][y].item.hero = None

            earnedMoney = self.boardHeroes[x][y].gold + (self.boardHeroes[x][y].tier - 1) * 2
            self.resetLabel(self.boardHeroes[x][y])
            self.heroToMove = None
        # print(f"Moving to board {mouse1.position}")

        # self.updateWindowCoords()

        time.sleep(self.mouseSleepTime * 2)

        mouse1.press(Button.left)

        time.sleep(self.mouseSleepTime * 2)

        mouse1.position = (self.x + 30, self.y + 820)

        time.sleep(self.mouseSleepTime * 2)

        mouse1.release(Button.left)
        time.sleep(self.mouseSleepTime * 2)
        return earnedMoney

    def boardUnitCount(self, check=False):

        numHeroes = 0
        labelHeroes = 0

        if check:
            for i in range(8):
                texty = self.benchLabels[i]['text']
                if texty != "" or self.benchHeroes[i]:
                    index = texty.find('-')
                    name = texty

                    if index != -1:
                        name = texty[:index - 1]
                    else:
                        name = texty

                    if self.benchHeroes[i] is None:
                        print(texty)
                        print(len(texty))
                        print(f"index: {i}")
                        raise Exception('benchUnit count error 55')
                    if not self.benchHeroes[i].underlord:
                        if self.benchHeroes[i].name != name:
                            print(self.benchHeroes[i].name)
                            print(len(self.benchHeroes[i].name))
                            print(texty)
                            print(len(texty))
                            print(f"index: {i}")
                            raise Exception('benchUnit count error 44')

            for i in range(4):
                for j in range(8):
                    texty = self.boardLabels[i][j]['text']
                    if texty != "" or self.boardHeroes[i][j] is not None:
                        index = texty.find('-')
                        name = texty

                        if len(name) > 1:
                            if self.boardHeroes[i][j] is None:
                                print("There should be a hero at spot (coords below)")
                                print(texty)
                                print(len(texty))
                                print(f"{i}-{j}")
                                raise Exception('boardunit count error 768')

                        if index != -1:
                            name = texty[:index - 1]
                        else:
                            name = texty
                        if not self.boardHeroes[i][j].underlord:
                            if self.boardHeroes[i][j].name != name:
                                print(self.boardHeroes[i][j].name)
                                print(len(self.boardHeroes[i][j].name))
                                print(texty)
                                print(len(texty))
                                print(f"{i}-{j}")
                                raise Exception('boardunit count error 33')

        for i in range(4):
            for j in range(8):
                if self.boardHeroes[i][j] is not None:
                    if not self.boardHeroes[i][j].underlord:
                        numHeroes += 1
        # if check:
        #     if labelHeroes != numHeroes:
        #         print("boardUnitCount does not line up!")
        #         raise Exception('boardUnitCount does not line up!')

        return numHeroes

    def switchXY(self, x, y):
        temp = x
        x = y
        y = temp
        return x, y

    def moveUnit(self, x=-1, y=-1):

        if self.heroToMove:
            print(f"selected hero: {self.heroToMove.name} --- cords: ${self.heroToMove.coords}")
        else:
            print("No hero selected")
        print(f"base cords: {x} - {y}")

        if x < 0:
            # print('moveUnit wrong x')
            self.mediumPunish = True
            return -1
        if y < -1:
            # print('moveUnit wrong y')
            self.mediumPunish = True
            return -1

        if not self.allowMove():
            self.mediumPunish = True
            # print('invalid phase move unit')
            return -1

        if self.heroToMove:  # If a hero has been selected to move previously
            if y == -1:  # Meaning we are moving onto a bench spot

                if x > 7:
                    self.mediumPunish = True
                    return -1

                if self.heroToMove.underlord:
                    # print("Can't place an underlord onto a bench!")
                    self.mediumPunish = True
                    self.heroToMove = None
                    return -1

                elif self.benchHeroes[x] is None:  # Making sure bench spot is open
                    self.benchHeroes[x] = self.heroToMove
                    self.resetLabel(self.heroToMove)
                    self.moveGameHero(self.heroToMove, x, -1)
                    self.heroToMove.coords = (x, -1)
                    self.updateHeroLabel(self.heroToMove)
                    self.heroToMove = None

                    print("bench swap 3")
                    self.boardUnitCount(True)

                else:
                    # keeping reference of hero in current spot

                    tempHero = self.benchHeroes[x]
                    oldCoords = self.heroToMove.coords
                    print("old cords: ")
                    print(oldCoords)

                    # moving selected hero to new spot
                    self.benchHeroes[x] = self.heroToMove
                    self.resetLabel(self.heroToMove)
                    self.moveGameHero(self.heroToMove, x, -1)
                    self.heroToMove.coords = (x, -1)
                    self.updateHeroLabel(self.heroToMove)
                    self.heroToMove = None

                    # print(oldCoords[0])

                    # meaning we are moving from bench to bench
                    if oldCoords[1] == -1:
                        tempHero.coords = (oldCoords[0], oldCoords[1])
                        self.benchHeroes[oldCoords[0]] = tempHero
                        print(
                            f"Board unit {self.benchHeroes[oldCoords[0]].name} move to New coords: {self.benchHeroes[oldCoords[0]].coords}")
                        self.updateHeroLabel(self.benchHeroes[oldCoords[0]])

                        print("bench swap 123")
                    else:
                        tempHero.coords = (oldCoords[0], oldCoords[1])
                        self.boardHeroes[oldCoords[1]][oldCoords[0]] = tempHero
                        print(
                            f"Bench unit {self.boardHeroes[oldCoords[1]][oldCoords[0]].name} move to New coords: {self.boardHeroes[oldCoords[1]][oldCoords[0]].coords}")
                        self.updateHeroLabel(self.boardHeroes[oldCoords[1]][oldCoords[0]])

                        print("bench swap 4")

                    # print(self.benchHeroes[oldCoords[0]])

                    self.boardUnitCount(True)

                    # print("Bench Spot Taken!")
                    # self.mediumPunish = True
                    # self.heroToMove = None
                    # return -1

            else:  # Meaning we are moving onto a board spot

                x, y = self.switchXY(x, y)

                if x > 3 or y > 7:
                    # print('the new wrong')
                    self.mediumPunish = True
                    return -1

                if self.boardUnitCount() >= self.level:  # Meaning we have no space on the board for more heroes
                    self.mediumPunish = True
                    self.heroToMove = None
                    # print('Not enough space on the board')
                    return -1

                if self.boardHeroes[x][y] is None:  # Making sure board spot is open
                    self.boardHeroes[x][y] = self.heroToMove
                    # print(f"moved: {self.boardHeroes[x][y].name} from {self.boardHeroes[x][y].coords}")
                    self.resetLabel(self.heroToMove)
                    # print(f"successfully moved unit onto board: {x}-{y}:::{self.allowMove()}")
                    self.moveGameHero(self.heroToMove, x, y)
                    self.heroToMove.coords = (y, x)
                    self.updateHeroLabel(self.heroToMove)
                    self.heroToMove = None

                    print("bench swap 6")
                    self.boardUnitCount(True)


                else:
                    # keeping reference of hero in current spot

                    tempHero = self.boardHeroes[x][y]
                    oldCoords = self.heroToMove.coords

                    if oldCoords[1] == -1:
                        if tempHero.underlord:
                            # can't swap bench unit onto an underlord!
                            self.mediumPunish = True
                            self.heroToMove = None
                            return -1

                    print("old cords: ")
                    print(oldCoords)

                    # moving selected hero to new spot

                    self.boardHeroes[x][y] = self.heroToMove
                    # print(f"moved: {self.boardHeroes[x][y].name} from {self.boardHeroes[x][y].coords}")
                    self.resetLabel(self.heroToMove)
                    # print(f"successfully moved unit onto board: {x}-{y}:::{self.allowMove()}")
                    self.moveGameHero(self.heroToMove, x, y)
                    self.heroToMove.coords = (y, x)
                    self.updateHeroLabel(self.heroToMove)
                    self.heroToMove = None

                    # print(oldCoords[0])

                    # meaning we are moving from board to bench
                    if oldCoords[1] == -1:

                        tempHero.coords = (oldCoords[0], oldCoords[1])
                        self.benchHeroes[oldCoords[0]] = tempHero
                        print(
                            f"Board unit {self.benchHeroes[oldCoords[0]].name} move to New coords: {self.benchHeroes[oldCoords[0]].coords}")

                        self.updateHeroLabel(self.benchHeroes[oldCoords[0]])
                        print("bench swap 1111")

                    else:

                        tempHero.coords = (oldCoords[0], oldCoords[1])
                        self.boardHeroes[oldCoords[1]][oldCoords[0]] = tempHero
                        print(
                            f"Bench unit {self.boardHeroes[oldCoords[1]][oldCoords[0]].name} move to New coords: {self.boardHeroes[oldCoords[1]][oldCoords[0]].coords}")
                        self.updateHeroLabel(self.boardHeroes[oldCoords[1]][oldCoords[0]])

                        print("bench swap 4232")

                    # print(self.benchHeroes[oldCoords[0]])

                    self.boardUnitCount(True)


        elif self.itemToMove:  # Meaning we are trying to attach an item to a hero

            print("equiping item")
            print(self.itemToMove)
            if y == -1:  # Meaning we are attaching an item to a unit on bench
                if self.benchHeroes[x] is not None:  # Making sure bench spot has a hero
                    self.updateHeroItem(self.benchHeroes[x])

                else:
                    # print("No Hero On This Bench!")
                    self.mediumPunish = True
                    self.itemToMove = None
                    return -1
            else:
                x, y = self.switchXY(x, y)
                if x > 3 or y > 7:
                    # print('the new wrong x 2')
                    self.mediumPunish = True
                    return -1

                if self.boardHeroes[x][y] is not None:  # Making sure board spot has a hero
                    if self.boardHeroes[x][y].underlord:
                        # print("Can't attach items to Underlords!")
                        self.mediumPunish = True
                        self.itemToMove = None
                        return -1

                    self.updateHeroItem(self.boardHeroes[x][y])

                else:
                    # print("No Hero On This Board!")
                    self.mediumPunish = True
                    self.itemToMove = None
                    return -1

        else:  # Meaning a hero has not yet been selected for movement, mark this hero as one to move
            if y == -1:  # Meaning we are moving onto a bench spot
                if self.benchHeroes[x] is not None:  # Making sure bench spot has a hero
                    self.heroToMove = self.benchHeroes[x]
                else:
                    # print("No Hero On This Bench!")
                    self.mediumPunish = True
                    self.heroToMove = None
                    return -1
            else:
                x, y = self.switchXY(x, y)
                check = self.boardHeroCoordCheck(x, y)
                if check == -1:
                    return check

                if self.boardHeroes[x][y] is not None:  # Making sure board spot has a hero
                    self.heroToMove = self.boardHeroes[x][y]
                else:
                    # print("No Hero On This Board!")
                    self.mediumPunish = True
                    self.heroToMove = None
                    return -1

        return 1

    def moveGameHero(self, hero, newX, newY):

        # self.updateWindowCoords()

        heroX, heroY = hero.coords

        if heroY == -1:
            mouse1.position = (self.benchX + (self.benchXOffset * heroX), self.benchY)
        else:
            # x, y = self.switchXY(heroX, heroY)
            mouse1.position = (self.boardX + (self.boardXOffset * heroX), self.boardY + (self.boardYOffset * heroY))
        # print(f"Moving to board {mouse1.position}")

        time.sleep(self.mouseSleepTime * 1.5)

        mouse1.press(Button.left)

        time.sleep(self.mouseSleepTime * 1.5)

        if newY == -1:  # Moving onto the bench
            mouse1.position = (self.benchX + (self.benchXOffset * newX), self.benchY)
        # print(f"Moving to bench {mouse1.position}")

        else:
            newX, newY = self.switchXY(newX, newY)
            mouse1.position = (self.boardX + (self.boardXOffset * newX), self.boardY + (self.boardYOffset * newY))
        # print(f"Moving to board {mouse1.position}")
        time.sleep(self.mouseSleepTime * 1.5)
        mouse1.release(Button.left)
        time.sleep(self.mouseSleepTime * 1.5)

    def getPunishment(self):

        sumTotal = 0

        if self.tinyPunish:
            self.tinyPunish = False
            sumTotal += 0.1
        if self.smallPunish:
            self.smallPunish = False
            sumTotal += 1
        if self.mediumPunish:
            self.mediumPunish = False
            sumTotal += 10
        if self.strongPunish:
            self.strongPunish = False
            sumTotal += 100

        return sumTotal

    def clickUp(self):

        # if self.combatType != 0 and not self.checkState:
        #     self.strongPunish = True
        #     return -1

        if self.pickTime():
            self.mediumPunish = True
            return -1

        if self.gold < 5:
            self.mediumPunish = True
            return -1

        if self.level == 10:
            self.smallPunish = True
            return -1

        if self.remainingEXP <= 5:
            self.leveledUp = True

        self.openStore(update=False, skipCheck=False)
        mouse1.position = (self.clickUpX, self.clickUpY)
        time.sleep(self.mouseSleepTime)
        mouse1.click(Button.left, 1)

        time.sleep(self.mouseSleepTime * 2)
        self.closeStore()

    def lockIn(self):

        # if self.combatType != 0 and not self.checkState:
        #     self.mediumPunish = True
        #     return -1

        if self.pickTime():
            self.mediumPunish = True
            return -1

        # punishing for locking (not unlocking) multiple times in the same round
        if self.round == self.lastLockedInRound and not self.lockedIn:
            self.strongPunish = True
            self.lockInPunish = True
            # print(f"Punishing repeated lock in")

        self.lastLockedInRound = self.round

        self.openStore(update=False, skipCheck=False)

        mouse1.position = (self.lockInX, self.lockInY)
        time.sleep(self.mouseSleepTime)

        mouse1.click(Button.left, 1)

        time.sleep(self.mouseSleepTime * 2)
        self.closeStore()

    def rerollStore(self):

        # if self.combatType != 0 and not self.checkState:
        #     self.mediumPunish = True
        #     return -1

        if self.pickTime():
            self.mediumPunish = True
            return -1

        if self.gold < 2:
            self.mediumPunish = True
            return -1

        self.openStore(update=False, skipCheck=False)
        mouse1.position = (self.rerollX, self.rerollY)
        time.sleep(self.mouseSleepTime)
        mouse1.click(Button.left, 1)
        time.sleep(self.mouseSleepTime)
        self.closeStore()

    def closeStore(self, skipCheck=False):

        # self.updateWindowCoords()

        if skipCheck:
            time.sleep(self.mouseSleepTime)
            mouse1.position = (self.shopX + 15, self.shopY + 15)
            time.sleep(self.mouseSleepTime)
            mouse1.click(Button.left, 1)
            time.sleep(self.mouseSleepTime)
        # elif self.combatType != 0:
        #     if self.shop.shopOpen():
        #         mouse1.position = (self.shopX, self.shopY)
        #         mouse1.click(Button.left, 1)
        #         time.sleep(self.mouseSleepTime)

    def openStore(self, update=True, skipCheck=False, finalForce=False):
        #
        # self.updateWindowCoords()

        # print(self.shop.shopOpen())

        # if self.combatType != 0 or self.round < 2 or finalForce:
        if self.combatType != 0 or self.round < 2 or finalForce:
            shopOpen = self.shop.shopOpen()
            # print('is shop open?')
            # print(shopOpen)
            # print('---')
            self.gameCrop = None  # reset crop afterwards

            if not shopOpen:
                mouse1.position = (self.shopX, self.shopY)
                mouse1.click(Button.left, 1)
                time.sleep(self.shopSleepTime)
        # uncomment below to force the store check. Only closes it by accident if it's internal representation of units
        # is wrong, and it misclicks empty spot on board
        # elif not skipCheck:
        #     shopOpen = self.shop.shopOpen(imageCrop=self.gameCrop)
        #     self.gameCrop = None # reset crop afterwards
        #
        #     if not shopOpen:
        #         mouse1.position = (self.shopX, self.shopY)
        #         mouse1.click(Button.left, 1)
        #         time.sleep(self.shopSleepTime)
        else:
            self.gameCrop = None
        # else:
        #     mouse1.position = (self.shopX, self.shopY)
        #     mouse1.click(Button.left, 1)
        #     time.sleep(self.mouseSleepTime)
        # if update:
        #     self.shopChoices = self.shop.labelShop()

    def updateWindowCoords(self):
        self.hwnd = win32gui.FindWindow(None, 'Dota Underlords')
        #        win32gui.SetForegroundWindow(self.hwnd)

        rect = win32gui.GetWindowRect(self.hwnd)
        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2] - self.x
        self.h = rect[3] - self.y
        self.shopX = self.x + 910
        self.shopY = self.y + 70
        self.rerollX = self.shopX
        self.rerollY = self.shopY + 82
        self.clickUpX = self.rerollX
        self.clickUpY = self.rerollY + 70
        self.benchX = self.x + 250
        self.benchXOffset = 90
        self.benchY = self.y + 800
        self.boardX = self.x + 300
        self.boardXOffset = 80
        self.boardY = self.y + 400
        self.boardYOffset = 70
        self.lockInX = self.shopX - 650
        self.lockInY = self.rerollY + 80
        self.itemX = self.shopX + 60
        self.itemXOffset = 20
        self.itemY = self.shopY + 60
        self.itemYOffset = 20
        self.itemYOffset = 20
        self.itemSelectY = self.y + 394
        self.itemSelectX = self.x + 290
        self.itemSelectXOffset = 220
        self.itemRerollX = self.itemSelectX + self.itemSelectXOffset
        self.itemRerollY = self.itemSelectY + 200
        self.itemMoveX = self.x + 965
        self.itemMoveXOffest = 40

        offset = self.items.findItemListOffset()
        if offset is None:
            offset = 0

        self.itemMoveY = self.y + offset + 185
        self.itemMoveYOffset = 35

    def boardHeroCoordCheck(self, x, y):
        if x > 3 or y > 7:
            # print('bad coords lmao')
            self.smallPunish = True
            return -1
        return 1

    def updateHeroItem(self, hero):

        if self.itemToMove.name in self.items.banned:
            # print('This item is not allowed to be used')
            return -1
        elif "melee_only" in self.items.itemData[self.itemToMove.name]:
            if not hero.melee:
                # print(f"{hero.name} is not melee!")
                self.mediumPunish = True
                return -1
        elif "ranged_only" in self.items.itemData[self.itemToMove.name]:
            if not hero.ranged:
                # print(f"{hero.name} is not ranged!")
                self.mediumPunish = True
                return -1
        elif "requires_ability" in self.items.itemData[self.itemToMove.name]:
            if hero.preventMana != False:
                # print(f"{hero.name} has mana ban?!")

                if hero.preventMana == 1:
                    # print('perma mana ban')
                    self.mediumPunish = True
                    return -1
                elif hero.preventMana[hero.tier - 1] != 0:
                    # print('mana ban til t3')
                    self.mediumPunish = True
                    return -1

        self.updateWindowCoords()  # Need to leave this to get proper item coords

        originalHero = self.itemToMove.hero

        mouse1.position = (self.itemMoveX + (self.itemMoveXOffset * self.itemToMove.coords[1]),
                           self.itemMoveY + (self.itemMoveYOffset * self.itemToMove.coords[0]))

        time.sleep(self.mouseSleepTime * 1.5)
        mouse1.press(Button.left)
        time.sleep(self.mouseSleepTime * 1.5)

        heroX, heroY = hero.coords

        if heroY == -1:
            mouse1.position = (self.benchX + (self.benchXOffset * heroX), self.benchY)
        else:
            # heroX, heroY = self.switchXY(heroX, heroY)
            mouse1.position = (self.boardX + (self.boardXOffset * heroX), self.boardY + (self.boardYOffset * heroY))

        time.sleep(self.mouseSleepTime * 1.5)
        mouse1.release(Button.left)

        if originalHero is not None:  # if item was equiped to someone before, now it no longer is

            if originalHero.item:
                originalHero.item.hero = None  # if the hero had an item, remove that items hero link

            originalHero.item = None
            self.updateHeroLabel(originalHero)

        if hero.item:
            hero.item.hero = None  # removing the existing's item on the new hero link

        hero.item = self.itemToMove
        self.itemToMove.hero = hero
        self.updateHeroLabel(hero)
        self.itemToMove = None

    def resetLabel(self, hero):

        x, y = hero.coords
        if y == -1:
            self.benchLabels[x].config(text="", bg='black', image=self.profilePics['None'])
            self.benchHeroes[x] = None
        else:
            x, y = self.switchXY(x, y)
            self.boardLabels[x][y].config(text="", bg='black', image=self.profilePics['None'])
            self.boardHeroes[x][y] = None

    def updateHeroLabel(self, hero):
        x, y = hero.coords
        color = 'black'

        if hero.tier == 2:
            color = 'blue'
        elif hero.tier == 3:
            color = 'yellow'
        elif hero.underlord:
            color = 'green'

        if y == -1:  # Meaning we are working with bench
            if hero.item is not None:
                self.benchLabels[x].config(image=hero.image, text=hero.name + ' - ' + hero.item.name, bg=color)
            else:
                self.benchLabels[x].config(image=hero.image, text=hero.name, bg=color)
        else:

            if hero.item is not None:
                self.boardLabels[y][x].config(
                    image=hero.image,
                    text=hero.name + ' - ' + hero.item.name,
                    bg=color)
            else:
                self.boardLabels[y][x].config(
                    image=hero.image,
                    text=hero.name,
                    bg=color)

    def buy(self, idx=0):

        # if self.checkBetweenCombat():
        #     self.strongPunish = True
        #     return -1

        if self.pickTime():
            self.mediumPunish = True
            return -1

        if self.shopUnits is None:
            self.smallPunish = True
            return -1

        self.openStore(skipCheck=False)
        validIDX = [0, 1, 2, 3, 4]

        if idx not in validIDX:
            self.mediumPunish = True
            return -1

        # # purchase history is never used, probably for xnull, which is already implemented so should never be raised
        # if idx in self.purchaseHistory:  # Note - note - still need to implement the validation logic at some point
        #     print("Invalid attempt to buy a unit!")
        #     raise RuntimeError("if idx in ---- find this error and figure out why this got triggered when it shouldn't")
        #     return -1

        result = self.handleLevelUp(idx)

        if result == -1:  # not hopefully this doesn't break things
            # self.closeStore()
            return -1

        self.openStore()

        if result == 10:  # meaning it tiered up, no need to create a new underlord on bench

            mouse1.position = (self.x + self.storeMap[idx], self.y + 130)
            time.sleep(self.mouseSleepTime)
            mouse1.click(Button.left, 1)

            time.sleep(self.mouseSleepTime)

            self.closeStore()

            return 10
        elif result == 11:

            mouse1.position = (self.x + self.storeMap[idx], self.y + 130)
            time.sleep(self.mouseSleepTime)
            mouse1.click(Button.left, 1)

            time.sleep(self.mouseSleepTime)

            self.closeStore()
            return 11

        for x in range(8):

            if self.benchHeroes[x] is None:
                heroData = self.underlords.underlordDataID[self.shopUnits[idx]]
                name = heroData['texturename']
                uniqueID = self.shop.classIDMap[name]

                self.benchHeroes[x] = self.createHero(name, uniqueID, x, -1,
                                                      self.localHeroID)
                self.localHeroID += 1

                self.benchLabels[x].config(text=f"{self.benchHeroes[x].name}",
                                           image=self.benchHeroes[x].image)

                mouse1.position = (self.x + self.storeMap[idx], self.y + 130)
                time.sleep(self.mouseSleepTime)
                mouse1.click(Button.left, 1)

                time.sleep(self.mouseSleepTime * 2)

                self.closeStore()
                return

        # Punishment for buying when no space on bench + no tier up possible goes here

    def createHero(self, heroName, uniqueID, x, y, localID):

        fullHero = self.underlords.underlordData[heroName]

        melee = False
        ranged = False
        preventMana = False

        # if 'goldCost' not in fullHero:
        #     print(f"couldnt find goldCost in {fullHero}")
        #     print(heroName)

        gold = fullHero['goldCost']

        if fullHero['attackRange'] == 1:
            melee = True
        else:
            ranged = True

        if 'prevent_mana_items' in fullHero:
            preventMana = fullHero['prevent_mana_items']

        return Hero(heroName, (x, y),
                    self.profilePics[heroName],
                    ID=uniqueID,
                    gold=gold,
                    melee=melee,
                    ranged=ranged,
                    preventMana=preventMana,
                    localID=localID)

    def findOriginalHero(self, heros):

        original = heros[0]

        for hero in heros:
            # If we are debating between a unit on the bench (y=-1) or board, board takes precedence
            if hero.coords[1] != -1 and original.coords[1] == -1:
                original = hero
            elif hero.coords[1] == -1 and original.coords[1] != -1:
                continue
            elif hero.localID < original.localID:
                original = hero

        return original

    def handleLevelUp(self, idx):

        tieredUp = False
        heroData = self.underlords.underlordDataID[self.shopUnits[idx]]
        name = heroData['texturename']

        if name == 'xnull':
            self.mediumPunish = True
            # print("Can't buy a null!")
            return -1

        if self.underlords.underlordData[name]['goldCost'] > self.gold:
            self.mediumPunish = True
            # print('Not enough money to buy!')
            return -1

        # print(f"bought: {name}")

        # Adding +1 to represent the shop unit coming in
        units = {"tierTwo": 0, "tierOne": 0 + 1, "tierTwoHeroes": [], "tierOneHeroes": [], "tieredUp2": False,
                 "tieredUp3": False}

        for i in range(4):
            for j in range(8):

                if self.boardHeroes[i][j]:
                    if self.boardHeroes[i][j].name == name:

                        if self.boardHeroes[i][j].tier == 1:
                            units["tierOne"] += 1
                            units["tierOneHeroes"].append(self.boardHeroes[i][j])

                        elif self.boardHeroes[i][j].tier == 2:
                            units["tierTwo"] += 1
                            units["tierTwoHeroes"].append(self.boardHeroes[i][j])

        for i in range(8):
            if self.benchHeroes[i]:
                if self.benchHeroes[i].name == name:

                    if self.benchHeroes[i].tier == 1:
                        units["tierOne"] += 1
                        units["tierOneHeroes"].append(self.benchHeroes[i])

                    elif self.benchHeroes[i].tier == 2:
                        units["tierTwo"] += 1
                        units["tierTwoHeroes"].append(self.benchHeroes[i])

        item = None
        ID = 0

        if units["tierOne"] == self.levelThresh:  # If there is enough tier ones to make a tier 2,
            # first instance hero levels up, the rest should be removed from reference and update labels?

            originalHero = self.findOriginalHero(units["tierOneHeroes"])

            if originalHero.item:
                item = originalHero.item
                ID = originalHero.localID

            originalHero.tier += 1

            units["tierTwoHeroes"].append(originalHero)

            units["tierTwo"] += 1
            units["tieredUp2"] = True

            for hero in units["tierOneHeroes"]:
                if hero.localID != originalHero.localID:
                    if hero.item:
                        if hero.localID > ID:

                            if item:
                                item.hero = None  # reseting the linked hero on the existing item (hero is gone now)

                            item = hero.item
                            ID = hero.localID
                    if self.heroToMove:
                        if self.heroToMove.localID == hero.localID:
                            self.heroToMove = None
                    self.resetLabel(hero)

            if item:
                originalHero.item = item
            self.updateHeroLabel(originalHero)  # Updating label to for color to indicate tier

        if units["tierTwo"] == self.levelThresh:

            originalHero = self.findOriginalHero(units["tierTwoHeroes"])

            if originalHero.item and originalHero.localID > ID:
                if item:
                    item.hero = None  # reseting the linked hero on the existing item (hero is gone now)

                item = originalHero.item
                ID = originalHero.localID

            originalHero.tier += 1

            units["tieredUp3"] = True

            for hero in units["tierTwoHeroes"]:
                if hero.localID != originalHero.localID:
                    if hero.item:
                        if hero.localID > ID:
                            if item:
                                item.hero = None  # reseting the linked hero on the existing item (hero is gone now)
                            item = hero.item
                            ID = hero.localID
                    if self.heroToMove:
                        if self.heroToMove.localID == hero.localID:
                            self.heroToMove = None
                    self.resetLabel(hero)
            if item:
                originalHero.item = item
            self.updateHeroLabel(originalHero)  # Updating label to for color to indicate tier

        # if we tiered up, return that
        if units["tieredUp3"] == True:  # A tier 3 implies a tier 2 was upgraded, so this is returned first
            return 11
        elif units["tieredUp2"] == True:
            return 10
        else:  # If we did not tier up, check that there is space on the bench for the unit

            freeSpace = False
            for i in self.benchHeroes:
                if i is None:
                    freeSpace = True

            if not freeSpace:
                # print("There is no space on bench to buy units!")
                self.mediumPunish = True
                return -1

        return tieredUp


def openVision():
    root = Tk()
    # root.geometry("600x105")
    root.resizable(0, 0)
    stopFlag = Event()
    thread = UnderlordInteract(root, training=False)
    # thread.start()
    # this will stop the timer
    # stopFlag.set()
    # shopFrame.pack()

    root.mainloop()

# openVision()
