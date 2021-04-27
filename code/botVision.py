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


class UnderlordInteract():
    def __init__(self, rootWindow, training=False):
        # Thread.__init__(self)
        # self.stopped = event
        self.rootWindow = rootWindow

        self.items = Items()

        self.hwnd = win32gui.FindWindow(None, 'Dota Underlords')
        #        win32gui.SetForegroundWindow(self.hwnd)

        rect = win32gui.GetWindowRect(self.hwnd)
        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2] - self.x
        self.h = rect[3] - self.y
        self.shopX = self.x + 905
        self.shopY = self.y + 65
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
        self.gameStateLoader = state()

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

        self.shop = Shop()
        self.HUD = HUD()
        self.itemIDmap = self.items.itemIDMap
        self.underlords = Underlords()
        self.bench = numpy.zeros([1, 8])
        self.board = numpy.zeros([4, 8])
        self.profilePics = loadProfiles()
        self.underlordPics = loadUnderlodProfiles()
        self.shopChoices = None
        self.storeMap = [350, 450, 575, 700, 800]  # super dumb and outdated to get X offset for purchase unit. change
        # later if I ever feel like it
        self.purchaseHistory = []
        self.gold = -1
        self.health = -1
        self.remainingEXP = -1
        self.level = -1
        self.round = -1
        self.freeRerollAvailable = False
        self.lockedIn = False
        self.leveledUp = False

        # shopImages, classes, value, inspect, statesList = self.shop.labelShop()

        # self.shopImages

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

        self.checkState = False  # note make sure to False this for production

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
            label.grid(row=0, column=i + 1, padx=5, pady=5)
            if not training:
                self.shopLabels.append(label)
                button = tkinter.Button(
                    master=self.shopFrame,
                    text="Purchase",
                    width=10,
                    height=1,
                    bg="blue",
                    fg="yellow",
                    command=lambda idx=i: self.buy(idx=idx)
                )
                button.grid(row=1, column=i + 1)

        self.itemFrame = Frame(master=self.shopFrame, relief=tkinter.RAISED, borderwidth=1)
        self.itemFrame.grid(row=0, column=6)

        for i in range(3):
            for j in range(4):

                label = Label(master=self.itemFrame, foreground='white', background='black',
                              text=f"item #{i}-{j}", compound='top')
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

        hudRow = 14

        # 8 bench portrait slots
        for x in range(8):
            newLabel = Label(master=self.shopFrame, foreground='white', background='black',
                             text=f"None", compound='top')
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
                                 text=f"None", compound='top')
                newLabel.grid(row=3 + (2 * i), column=j, padx=3, pady=2)
                self.boardLabels[i][j] = newLabel

                if not training:
                    tempButton = tkinter.Button(master=self.shopFrame, text="Move", width=4, height=1,
                                                command=lambda pos=i, idx=j: self.moveUnit(x=pos, y=idx))
                    tempButton.grid(row=4 + (2 * i), column=j)

        self.shopFrame.pack()

    def resetEnv(self, training=False):

        self.gamePhase = None
        self.gameStateLoader = state()

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
        self.gold = -1
        self.health = -1
        self.remainingEXP = -1
        self.level = -1
        self.round = -1
        self.freeRerollAvailable = False
        self.lockedIn = False
        self.leveledUp = False

        # shopImages, classes, value, inspect, statesList = self.shop.labelShop()

        # self.shopImages


        self.oldShopImages = self.shopImages
        self.shopImages = []
        self.benchHeroes = [None, None, None, None, None, None, None, None]
        self.boardHeroes = numpy.full((4, 8), None)
        self.itemObjects = numpy.full((3, 4), None)
        self.underlord = None

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
                                             text=f"item #{i}-{j}", compound='top', image='')

        hudRow = 14

        # 8 bench portrait slots
        for x in range(8):
            self.benchLabels[x].config(foreground='white', background='black',
                                       text=f"None", compound='top', image='')

        # self.shopFrame.grid(row=1, column=0, pady=0, columnspan=5)
        self.hudLabel.config(foreground='white', background='black',
                             text="Hi", compound='top', image='')

        for i in range(4):
            for j in range(8):
                self.boardLabels[i][j].config(foreground='white', background='black',
                                              text=f"None", compound='top', image='')

        self.shopFrame.pack()

    def testFunction(self, param1, param2):
        # print(self.gameStateLoader.getPhase())
        # print(self.closeStore())
        # list = itemNameList()
        #
        # for item in list:
        #     if "melee_only" in self.items.itemData[item]:
        #         print(item)
        #     if "ranged_only" in self.items.itemData[item]:
        #         print(item)
        #     if "requires_ability" in self.items.itemData[item]:
        #         print(item)
        # print(self.shop.classes)
        # #
        # for profile in self.profilePics.keys() :
        #     print(self.underlords.underlordData[profile])
        # tempHeroName = 'luna'
        # fullHero = self.underlords.underlordData[tempHeroName]
        #
        # melee = False
        # ranged = False
        # preventMana = False
        # gold = fullHero['goldCost']
        #
        # if fullHero['attackRange'] == 1:
        #     melee = True
        # else:
        #     ranged = True
        #
        # if 'prevent_mana_items' in fullHero:
        #     preventMana = fullHero['prevent_mana_items']
        #
        # tempHero = Hero(tempHeroName, (-1, -1),
        #                 self.profilePics[tempHeroName],
        #                 ID=123,
        #                 gold=gold,
        #                 melee=melee,
        #                 ranged=ranged,
        #                 preventMana=preventMana)
        #
        # self.itemToMove = Item("dragon_lance", (0, 0), ID=123)
        #
        # self.updateHeroItem(tempHero)
        # print(self.getObservation())
        self.resetEnv()

    def returnToMainScreen(self):
        self.updateWindowCoords()
        mouse1.position = (self.shopX, self.shopY + 100)
        mouse1.click(Button.left, 1)

        self.gameStateLoader.currentPhase = None

    def startNewGame(self):
        self.updateWindowCoords()

        mouse1.position = (self.shopX, self.shopY + 720)
        mouse1.click(Button.left, 1)

        time.sleep(self.shopSleepTime)

        mouse1.position = (self.x + 700, self.shopY + 200)
        mouse1.click(Button.left, 1)

        time.sleep(self.shopSleepTime)

        mouse1.position = (self.shopX, self.shopY + 720)
        mouse1.click(Button.left, 1)
        flag = True

        while flag:
            time.sleep(0.1)

            phase = self.getGamePhase()
            if phase is not None:
                flag = False

    def getObservation(self):

        position = self.finished()

        if position != -1:
            obs = (
                position, 0, 0, 0, 0, 0, 0, 0,
                [0, 0], 0, 0, 0,
                # store heros
                [0, 0, 0, 0, 0],
                # bench heroes
                [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                # board heroes
                [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                # underlords to pick
                [0, 0, 0, 0],
                # local Items,
                [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                # items to pick
                [0, 0, 0]
            )
            return obs

        if position == -1:
            position = 0
        phase = self.getGamePhase()

        if phase not in ['select', 'choose']:
            self.updateShop()

        health = None

        if self.lost == False:
            health = 100
        else:
            health = self.health

        gamePhase = -1

        if phase == 'select':
            gamePhase = 1
        elif phase == 'choose':
            gamePhase = 2
        elif phase == 'preparing':
            gamePhase = 3
        elif gamePhase == 'combat':
            gamePhase = 4
        elif gamePhase == 'countdown':
            gamePhase = 5

        heroToMove = None

        if self.heroToMove is not None:

            isUnderlord = 0

            if self.heroToMove.underlord:
                isUnderlord = 2
            else:
                isUnderlord = 1

            heroToMove = [self.heroToMove.id + 1, isUnderlord]
        else:
            heroToMove = [0, 0]

        itemToMove = None

        if self.itemToMove == None:
            itemToMove = 0
        else:
            itemToMove = self.itemToMove.localID

        shopImages, classes, value, inspect, statesList = self.shopChoices
        shopHeros = []

        for idx in range(5):
            shopHeros.append(statesList[idx] + 1)

        benchHeros = []
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

                tempHero = [self.benchHeroes[i].id + 1, self.benchHeroes[i].localID, self.benchHeroes[i].tier,
                            self.benchHeroes[i].gold, itemID,
                            self.benchHeroes[i].coords[0],
                            self.benchHeroes[i].coords[1], isUnderlord]
            else:
                tempHero = [0, 0, 0, 0, 0, 0, 0, 0]
            benchHeros.append(tempHero)

        boardHeroes = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0]]
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

                    tempHero = [self.boardHeroes[i][j].id + 1, self.boardHeroes[i][j].localID,
                                self.boardHeroes[i][j].tier, self.boardHeroes[i][j].gold,
                                itemID, self.boardHeroes[i][j].coords[0],
                                self.boardHeroes[i][j].coords[1], isUnderlord]

                    boardHeroes[idx] = tempHero
                    idx += 1

        underlordsPick = []

        if gamePhase == 2:

            underlords = self.underlords.checkUnderlords()

            for i in range(4):
                underlord = underlords[0]

                underlordID = None

                if underlord == 'aggressive_tank':
                    underlordID = 63
                elif underlord == 'healing_tank':
                    underlordID = 64
                elif underlord == 'damage_support':
                    underlordID = 65
                elif underlord == 'healing_support':
                    underlordID = 66
                elif underlord == 'healing_stealing':
                    underlordID = 67
                elif underlord == 'rapid_furball':
                    underlordID = 68
                elif underlord == 'high_damage_dealer':
                    underlordID = 69
                elif underlord == 'support_damage_dealer':
                    underlordID = 70
                else:
                    raise RuntimeError("Found a no match for underlord in obs!")
                underlordsPick.append(underlordID)

        else:
            underlordsPick = [0, 0, 0, 0]

        localItems = []

        for i in range(3):
            for j in range(4):
                if self.itemObjects[i][j] is not None:
                    item = self.itemObjects[i][j]
                    heroID = 0

                    if item.hero is not None:
                        heroID = item.hero.localID

                    localItems.append(item.ID + 1, heroID, item.coords[0] + 1, item.coords[1] + 1)
                else:
                    localItems.append([0, 0, 0, 0, 0])

        itemPick = []

        if gamePhase == 1:

            items = self.items.checkItems()

            for item in items:
                itemPick.append(self.itemIDmap[item])

        else:
            itemPick = [0, 0, 0]

        reroll = 0

        if self.freeRerollAvailable:
            reroll = 1

        lockedIn = 0

        if self.lockedIn:
            lockedIn = 1

        rerolledItem = 0

        if self.rerolledItem:
            rerolledItem = 1

        obs = (
            position, health, self.gold, self.level, self.remainingEXP, self.round, lockedIn, gamePhase,
            heroToMove, itemToMove, reroll, rerolledItem,
            # store heros
            shopHeros,
            # bench heroes
            benchHeros[0], benchHeros[1], benchHeros[2], benchHeros[3], benchHeros[4], benchHeros[5], benchHeros[6],
            benchHeros[7],
            # board heroes
            boardHeroes[0], boardHeroes[1], boardHeroes[2], boardHeroes[3], boardHeroes[4], boardHeroes[5],
            boardHeroes[6], boardHeroes[7], boardHeroes[8], boardHeroes[9],
            # underlords to pick
            underlordsPick,
            # local Items,
            localItems[0], localItems[1], localItems[2], localItems[3], localItems[4], localItems[5],
            localItems[6], localItems[7], localItems[8], localItems[9], localItems[10], localItems[11],
            # items to pick
            itemPick
        )

        print(f"Time left: {self.HUD.getClockTimeLeft()}")
        return obs

    def act(self, action, x, y, selection):

        tieredUp = None
        firstPlace = 1000
        earnedMoney = -1

        if action == 0:
            self.rerollStore()
        elif action == 1:
            self.lockIn()
        elif action == 2:
            self.clickUp()
        elif action == 3:
            tieredUp = self.buy(x)
        elif action == 4:
            earnedMoney = self.sellHero(x, y)
        elif action == 5:
            self.selectItem(x, y, selection)
        elif action == 6:
            self.selectItem(x, y, selection)
        elif action == 7:
            self.moveUnit(x, y)
        elif action == 8:
            self.moveUnit(x, y)

        reward = 0

        if self.smallPunish:
            self.smallPunish = False
            reward -= firstPlace * 0.01
        elif self.mediumPunish:
            self.mediumPunish = False
            reward -= firstPlace * 0.065
        elif self.strongPunish:
            self.strongPunish = False
            reward -= firstPlace * 0.1

        numHeroes = 0

        if not self.leveledUp:
            for i in range(4):
                for j in range(8):
                    if self.boardHeroes[i][j] is not None:
                        numHeroes += 1

            reward -= (self.level - numHeroes) * (firstPlace * 0.05)

        if action in [0, 2, 3]:
            if self.gold > 40:
                reward -= 0.05
            elif self.gold >= 30:
                reward += firstPlace * 0.02
            elif self.gold >= 20:
                reward += firstPlace * 0.005
            elif self.gold >= 10:
                reward += firstPlace * 0.001

        # note - to do : take into account tier of unit tiered up

        if tieredUp == 10:
            reward += firstPlace * 0.01
        elif tieredUp == 11:
            reward += firstPlace * 0.03

        if self.leveledUp:
            reward += firstPlace * 0.03

        if earnedMoney != -1:
            reward += firstPlace * (1 - earnedMoney / 9) * 0.001

        finished = self.finished()

        if finished != -1:

            if finished == 1:
                reward == firstPlace
            elif finished == 2:
                reward == firstPlace * 0.9
            elif finished == 3:
                reward == firstPlace * 0.75
            elif finished == 4:
                reward == firstPlace * 0.5
            elif finished == 5:
                reward == firstPlace * 0.3
            elif finished == 6:
                reward == firstPlace * 0.2
            elif finished == 7:
                reward == firstPlace * 0.1
            elif finished == 8:
                reward == firstPlace * 0

        if self.gamePhase in ['select', 'choose']:
            reward -= self.timeRunningOut()

        return reward

    def finished(self):

        return self.gameStateLoader.detectGameEnd()

    def timeRunningOut(self):

        timeLeft = self.HUD.getClockTimeLeft()

        if timeLeft <= 5:

            self.selectItem(selection=0)
            return - 100
        else:
            return 0

    def getGamePhase(self):

        self.closeStore()

        newRound = self.HUD.getRound()

        if newRound > self.round:
            self.lockedIn = False

        self.round = newRound
        # self.gamePhase = self.gameStateLoader.getPhase()

        return self.gameStateLoader.getPhase()

    def selectItem(self, x=-1, y=-1, selection=-1):

        gamePhase = self.getGamePhase()

        print(f"gamePhase: {gamePhase}")

        if gamePhase in self.SelectItem:

            if selection < -1 or selection > 3:
                print('break 1')
                self.mediumPunish = True
                return -1

            items = self.items.checkItems()

            if items[0] is None:
                raise RuntimeError("item select Uh Oh")
                return -1

            self.buyItem(selection, items)

        elif gamePhase in self.SelectUnderlord:

            underlords = self.underlords.checkUnderlords()

            if underlords[0] is None:
                print("No Underlord or item available for selection!")
                raise RuntimeError("Underlord Uh Oh")
                return -1

            if selection < -1 or selection > 3:
                self.mediumPunish = True
                print('break 2')
                return -1

            self.buyUnderlord(underlords[selection], selection)

        else:

            if self.heroToMove:
                # print("You have a hero selected to move, move it first!")
                self.smallPunish = True
                print('break 3')
                return -1

            if x > 2 or y > 3:
                self.mediumPunish = True
                print('uh oh 3')
                return -1

            if self.itemObjects[x][y] is None:
                # print("there is no item to select here!")
                self.mediumPunish = True
                print('break 4')
                return -1
            else:
                if y < 0 or y > 3:
                    self.mediumPunish = True
                    print('break 5')
                    return -1
                if x < 0 or x > 2:
                    self.mediumPunish = True
                    print('break 5')
                    return -1
                if self.itemObjects[x][y] is None:
                    self.smallPunish = True
                    print('break 6')
                    return -1

                self.itemToMove = self.itemObjects[x][y]

    def buyItem(self, selection, itemList):

        if selection == 3:
            if self.rerolledItem:

                self.strongPunish = True
                print('break 7')
                return -1

            else:
                self.updateWindowCoords()
                mouse1.position = (self.itemRerollX, self.itemRerollY)
                mouse1.click(Button.left, 1)
                self.rerolledItem = True
                self.choseItem = False
                self.selected = False

        else:
            self.updateWindowCoords()
            mouse1.position = (self.itemSelectX + (self.itemSelectXOffset * selection), self.itemSelectY)
            mouse1.click(Button.left, 1)
            self.rerolledItem = False
            self.choseItem = True
            self.selected = True
            for i in range(3):
                for j in range(4):
                    if self.itemObjects[i][j] is None:

                        name = itemList[selection]
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
                                                      ID=self.itemIDmap[name],
                                                      melee=melee,
                                                      ranged=ranged,
                                                      preventMana=preventMana,
                                                      localID=self.localItemID)
                        self.localItemID += 1
                        self.itemlabels[i][j].config(text=self.itemObjects[i][j].name)
                        return

    def buyUnderlord(self, underlord, selection):

        self.updateWindowCoords()
        mouse1.position = (self.itemSelectX + (self.itemSelectXOffset * selection), self.itemSelectY)
        mouse1.click(Button.left, 1)

        AnnaPreferences = [(2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7)]
        JullPreferences = [(0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (3, 0), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)]
        HobPreferences = [(2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7)]
        FurPreferences = [(1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]

        preferences = []
        ID = None

        if underlord == 'aggressive_tank':
            preferences = JullPreferences
            ID = 63
        elif underlord == 'healing_tank':
            preferences = JullPreferences
            ID = 64
        elif underlord == 'damage_support':
            preferences = AnnaPreferences
            ID = 65
        elif underlord == 'healing_support':
            preferences = AnnaPreferences
            ID = 66
        elif underlord == 'healing_stealing':
            preferences = FurPreferences
            ID = 67
        elif underlord == 'rapid_furball':
            preferences = FurPreferences
            ID = 68
        elif underlord == 'high_damage_dealer':
            preferences = AnnaPreferences
            ID = 69
        elif underlord == 'support_damage_dealer':
            preferences = AnnaPreferences
            ID = 70

        else:
            print('No clue what underlord that is!')
            return -1

        for x, y in preferences:

            if self.boardHeroes[x][y] is None:
                print(f"Found a spot for underlord at: {x}-{y}")
                self.underlord = Hero(underlord, (x, y), self.underlordPics[underlord], True, ID=ID,
                                      localID=self.localHeroID)
                self.localHeroID += 1
                self.updateHeroLabel(self.underlord)
                self.boardHeroes[x][y] = self.underlord
                return

    def updateShop(self):

        self.openStore()

        shopImages, classes, value, inspect, statesList = self.shopChoices

        itemCounts = self.HUD.getHUD()

        for i in range(5):
            tempImage = ImageTk.PhotoImage(shopImages[i])
            self.shopImages.append(tempImage)
            self.shopLabels[i].config(image=tempImage,
                                      text=f"{classes[statesList[i]]} {value[i] * 100:2.1f}%")
            # print(f"{classes[statesList[i]]} {value[i] * 100:2.1f}%")

        # itemImage = ImageTk.PhotoImage(itemImage)
        tempString = "\nUnit Count %d" % itemCounts[2] + "\nGold Count: %d" % itemCounts[0] \
                     + "\nHealth Count: %d" % itemCounts[1] + "\nRemaining EXP: %d" % (itemCounts[4] - itemCounts[3])
        self.hudLabel.config(text=tempString)
        self.gold = itemCounts[0]

        if self.health != -1:
            if self.lost == False and (itemCounts[1] > self.health):
                self.lost = True

        self.freeRerollAvailable = self.shop.freeReroll()  # note to do enable later

        newLevel = itemCounts[2]

        if newLevel > self.level:
            self.leveledUp = True
        else:
            self.leveledUp = False

        self.level = itemCounts[2]
        self.health = itemCounts[1]
        self.remainingEXP = (itemCounts[4] - itemCounts[3])

    def sellHero(self, x=-1, y=-1):

        if self.getGamePhase() not in self.UnitItemMove and not self.checkState:
            self.mediumPunish = True
            return -1

        if x < -1 or x > 7:
            print('wrong x')
            self.mediumPunish = True
            return -1
        if y < -1 or y > 3:
            print('wrong y')
            self.mediumPunish = True
            return -1

        if x == -1:
            if self.heroToMove is None:
                # print("No Hero Selected to Sell")
                self.mediumPunish = True
                return -1
            else:
                x, y = self.heroToMove.coords
        else:

            check = self.boardHeroCoordCheck(x, y)
            if check == -1:
                return check

            if y == -1:
                if self.benchHeroes[x] is None:
                    # print(f"No hero on bench spot {x + 1} to sell!")
                    self.mediumPunish = True
                    return -1
            elif self.boardHeroes[x][y] is None:
                # print(f"No hero on board spot {x + 1}-{y + 1} to sell!")
                self.mediumPunish = True
                return -1

        earnedMoney = 0

        if y == -1:
            mouse1.position = (self.benchX + (self.benchXOffset * x), self.benchY)
            earnedMoney = self.benchHeroes[x].gold + (self.benchHeroes[x].tier - 1) * 2
            self.resetLabel(self.benchHeroes[x])
            self.heroToMove = None
        else:
            mouse1.position = (self.boardX + (self.boardXOffset * y), self.boardY + (self.boardYOffset * x))
            earnedMoney = self.boardHeroes[x][y].gold + (self.boardHeroes[x][y].tier - 1) * 2
            self.resetLabel(self.boardHeroes[x][y])
            self.heroToMove = None
        # print(f"Moving to board {mouse1.position}")

        self.updateWindowCoords()

        mouse1.press(Button.left)

        time.sleep(self.mouseSleepTime)

        mouse1.position = (self.x + 50, self.y + 800)

        time.sleep(self.mouseSleepTime)

        mouse1.release(Button.left)
        return earnedMoney

    def moveGameHero(self, hero, newX, newY):

        self.updateWindowCoords()

        heroX, heroY = hero.coords

        if heroY == -1:
            mouse1.position = (self.benchX + (self.benchXOffset * heroX), self.benchY)
        else:
            mouse1.position = (self.boardX + (self.boardXOffset * heroY), self.boardY + (self.boardYOffset * heroX))
        # print(f"Moving to board {mouse1.position}")

        mouse1.press(Button.left)

        time.sleep(self.mouseSleepTime)

        if newY == -1:  # Moving onto the bench
            mouse1.position = (self.benchX + (self.benchXOffset * newX), self.benchY)
        # print(f"Moving to bench {mouse1.position}")

        else:
            mouse1.position = (self.boardX + (self.boardXOffset * newY), self.boardY + (self.boardYOffset * newX))
        # print(f"Moving to board {mouse1.position}")
        time.sleep(self.mouseSleepTime)
        mouse1.release(Button.left)

    def getPunishment(self):

        if self.smalLPunish:
            self.smallPunish = False
            return 1
        elif self.mediumPunish:
            self.mediumPunish = False
            return 10
        elif self.strongPunish:
            self.strongPunish = False
            return 100

    def clickUp(self):

        if self.getGamePhase() not in self.StoreInteract and not self.checkState:
            self.strongPunish = True
            return -1

        if self.gold < 5:
            self.mediumPunish = True
            return -1

        if self.level == 10:
            self.smallPunish = True
            return -1

        self.openStore(update=False)
        mouse1.position = (self.clickUpX, self.clickUpY)
        mouse1.click(Button.left, 1)
        time.sleep(self.mouseSleepTime)
        self.updateShop()

    def lockIn(self):

        if self.getGamePhase() not in self.StoreInteract and not self.checkState:
            self.mediumPunish = True
            return -1

        self.openStore(update=False)

        if self.lockedIn:
            self.lockedIn = False
        else:
            self.lockedIn = True

        mouse1.position = (self.lockInX, self.lockInY)
        mouse1.click(Button.left, 1)

    def rerollStore(self):

        gamePhase = self.getGamePhase()

        if gamePhase not in self.StoreInteract and not self.checkState:
            self.mediumPunish = True
            return -1

        if self.gold < 2:
            self.mediumPunish = True
            return -1

        self.openStore(update=False)
        mouse1.position = (self.rerollX, self.rerollY)
        mouse1.click(Button.left, 1)
        self.lockedIn = False

        self.updateShop()

    def closeStore(self):

        self.updateWindowCoords()

        if self.shop.shopOpen():
            mouse1.position = (self.shopX, self.shopY)
            mouse1.click(Button.left, 1)
            time.sleep(2 * self.mouseSleepTime)

    def openStore(self, update=True):

        self.updateWindowCoords()

        if not self.shop.shopOpen():
            mouse1.position = (self.shopX, self.shopY)
            mouse1.click(Button.left, 1)
            time.sleep(self.shopSleepTime)
        if update:
            self.shopChoices = self.shop.labelShop()

    def updateWindowCoords(self):
        self.hwnd = win32gui.FindWindow(None, 'Dota Underlords')
        #        win32gui.SetForegroundWindow(self.hwnd)

        rect = win32gui.GetWindowRect(self.hwnd)
        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2] - self.x
        self.h = rect[3] - self.y
        self.shopX = self.x + 905
        self.shopY = self.y + 65
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

    def moveUnit(self, x=-1, y=-1):

        print(f"base cords: {x} - {y}")

        if x < -1:
            print('moveUnit wrong x')
            self.mediumPunish = True
            return -1
        if y < -1:
            print('moveUnit wrong y')
            self.mediumPunish = True
            return -1

        if self.getGamePhase() not in self.UnitItemMove and not self.checkState:
            self.mediumPunish = True
            print('invalid phase move unit')
            return -1

        if self.heroToMove:  # If a hero has been selected to move previously
            if y == -1:  # Meaning we are moving onto a bench spot

                if x > 7:
                    self.mediumPunish = True
                    return -1

                if self.heroToMove.underlord:
                    print("Can't place an underlord onto a bench!")
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

                else:
                    print("Bench Spot Taken!")
                    self.mediumPunish = True
                    self.heroToMove = None
                    return -1

            else:  # Meaning we are moving onto a board spot

                if x > 3 or y > 7:
                    print('the new wrong')
                    self.mediumPunish = True
                    return -1

                numHeroes = 0

                for i in range(3):
                    for j in range(7):
                        if self.boardHeroes[i][j] is not None:
                            numHeroes += 1

                if numHeroes >= self.level:  # Meaning we have no space on the board for more heroes
                    self.mediumPunish = True
                    self.heroToMove = None
                    return -1

                if self.boardHeroes[x][y] is None:  # Making sure board spot is open
                    self.boardHeroes[x][y] = self.heroToMove
                    self.resetLabel(self.heroToMove)
                    self.moveGameHero(self.heroToMove, x, y)
                    self.heroToMove.coords = (x, y)
                    self.updateHeroLabel(self.heroToMove)
                    self.heroToMove = None

                else:
                    print("Board Spot Taken!")
                    self.mediumPunish = True
                    self.heroToMove = None
                    return -1

        elif self.itemToMove:  # Meaning we are trying to attach an item to a hero

            if y == -1:  # Meaning we are attaching an item to a unit on bench
                if self.benchHeroes[x] is not None:  # Making sure bench spot has a hero
                    self.updateHeroItem(self.benchHeroes[x])

                else:
                    # print("No Hero On This Bench!")
                    self.mediumPunish = True
                    self.itemToMove = None
                    return -1
            else:
                if self.boardHeroes[x][y] is not None:  # Making sure board spot has a hero
                    if self.boardHeroes[x][y].underlord:
                        # print("Can't attach items to Underlords!")
                        self.mediumPunish = True
                        self.itemToMove = None
                        return -1

                    self.updateHeroItem(self.boardHeroes[x][y])

                else:
                    print("No Hero On This Board!")
                    self.mediumPunish = True
                    self.itemToMove = None
                    return -1

        else:  # Meaning a hero has not yet been selected for movement, mark this hero as one to move
            if y == -1:  # Meaning we are moving onto a bench spot
                if self.benchHeroes[x] is not None:  # Making sure bench spot has a hero
                    self.heroToMove = self.benchHeroes[x]
                else:
                    print("No Hero On This Bench!")
                    self.mediumPunish = True
                    self.heroToMove = None
                    return -1
            else:

                check = self.boardHeroCoordCheck(x, y)
                if check == -1:
                    return check

                if self.boardHeroes[x][y] is not None:  # Making sure board spot has a hero
                    self.heroToMove = self.boardHeroes[x][y]
                else:
                    print("No Hero On This Board!")
                    self.mediumPunish = True
                    self.heroToMove = None
                    return -1

        return 1

    def boardHeroCoordCheck(self, x, y):
        if x > 4 or y > 7:
            print('bad coords lmao')
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

        self.updateWindowCoords()

        originalHero = self.itemToMove.hero

        mouse1.position = (self.itemMoveX + (self.itemMoveXOffset * self.itemToMove.coords[1]),
                           self.itemMoveY + (self.itemMoveYOffset * self.itemToMove.coords[0]))

        mouse1.press(Button.left)
        time.sleep(self.mouseSleepTime)

        heroX, heroY = hero.coords

        if heroY == -1:
            mouse1.position = (self.benchX + (self.benchXOffset * heroX), self.benchY)
        else:
            mouse1.position = (self.boardX + (self.boardXOffset * heroY), self.boardY + (self.boardYOffset * heroX))

        time.sleep(self.mouseSleepTime)
        mouse1.release(Button.left)

        if originalHero is not None:
            originalHero.item = None
            self.updateHeroLabel(originalHero)

        hero.item = self.itemToMove
        self.itemToMove.hero = hero
        self.updateHeroLabel(hero)
        self.itemToMove = None

    def resetLabel(self, hero):

        x, y = hero.coords
        if y == -1:
            self.benchLabels[x].config(text="None", bg='black', image=self.profilePics['None'])
            self.benchHeroes[x] = None
        else:
            self.boardLabels[x][y].config(text="None", bg='black', image=self.profilePics['None'])
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
                self.boardLabels[x][y].config(
                    image=hero.image,
                    text=hero.name + ' - ' + hero.item.name,
                    bg=color)
            else:
                self.boardLabels[x][y].config(
                    image=hero.image,
                    text=hero.name,
                    bg=color)

    def buy(self, idx=0):

        if self.getGamePhase() not in self.StoreInteract and not self.checkState:
            self.strongPunish = True
            return -1

        self.openStore()
        validIDX = [0, 1, 2, 3, 4]

        if idx not in validIDX:
            self.smallPunish = True
            return -1

        # purchase history is never used, probably for xnull, which is already implemented so should never be raised
        if idx in self.purchaseHistory:  # Note - note - still need to implement the validation logic at some point
            print("Invalid attempt to buy a unit!")
            raise RuntimeError("if idx in ---- find this error and figure out why this got triggered when it shouldn't")
            return -1

        # self.openStore() #note might need to enable this if it causes bugs
        shopImages, classes, value, inspect, statesList = self.shopChoices

        result = self.benchLevelUp(idx)

        if result == -1:  # not hopefully this doesn't break things
            return -1

        mouse1.position = (self.x + self.storeMap[idx], self.y + 130)
        mouse1.click(Button.left, 1)

        time.sleep(self.mouseSleepTime)

        if result == 10:  # meaning it tiered up, no need to create a new underlord on bench
            self.updateShop()
            return 10
        elif result == 11:
            self.updateShop()
            return 11

        for x in range(8):

            if self.benchHeroes[x] is None:
                self.benchHeroes[x] = self.createHero(classes[statesList[idx]], statesList[idx], x, -1,
                                                      self.localHeroID)
                self.localHeroID += 1

                self.benchLabels[x].config(text=f"{self.benchHeroes[x].name}",
                                           image=self.benchHeroes[x].image)
                self.updateShop()
                return

    def createHero(self, heroName, uniqueID, x, y, localID):

        fullHero = self.underlords.underlordData[heroName]

        melee = False
        ranged = False
        preventMana = False
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

    def boardLevelUp(self, idx):

        # Adding +1 to represent the shop unit coming in
        board = {"tierTwo": 0, "tierOne": 0 + 1, "tierTwoHeroes": [], "tierOneHeroes": [], "tieredUp2": False,
                 "tieredUp3": False}
        shopImages, classes, value, inspect, statesList = self.shopChoices

        for i in range(4):
            for j in range(8):

                if self.boardHeroes[i][j]:
                    if self.boardHeroes[i][j].name == classes[statesList[idx]]:

                        if self.boardHeroes[i][j].tier == 1:
                            board["tierOne"] += 1
                            board["tierOneHeroes"].append(self.boardHeroes[i][j])

                        elif self.boardHeroes[i][j].tier == 2:
                            board["tierTwo"] += 1
                            board["tierTwoHeroes"].append(self.boardHeroes[i][j])

        if board["tierOne"] == self.levelThresh:  # If there is enough tier ones to make a tier 2,
            # first instance hero levels up, the rest should be removed from reference and update labels?

            board["tierOneHeroes"][0].tier += 1

            board["tierTwoHeroes"].append(board["tierOneHeroes"][0])
            self.updateHeroLabel(board["tierOneHeroes"][0])  # Updating label to for color to indicate tier
            board["tierTwo"] += 1
            board["tieredUp"] = True

            for x in range(1, len(board["tierOneHeroes"])):
                specificHero = board["tierOneHeroes"][x]
                self.resetLabel(specificHero)

        if board["tierTwo"] == self.levelThresh:  # If there is enough tier ones to make a tier 2,
            # first instance hero levels up, the rest should be removed from reference and update labels?

            board["tierTwoHeroes"][0].tier += 1
            self.updateHeroLabel(board["tierTwoHeroes"][0])  # Updating label to for color to indicate tier
            board["tieredUp"] = True

            for x in range(1, len(board["tierTwoHeroes"])):
                specificHero = board["tierTwoHeroes"][x]
                self.resetLabel(specificHero)

        return board

    def benchLevelUp(self, idx):

        tieredUp = False
        shopImages, classes, value, inspect, statesList = self.shopChoices

        if classes[statesList[idx]] == 'xnull':
            self.mediumPunish = True
            print('fuck 1')
            return -1
        else:
            print(f"bought: {classes[statesList[idx]]}")

        if self.underlords.underlordData[classes[statesList[idx]]]['goldCost'] > self.gold:
            self.mediumPunish = True
            print('fuck 2')
            return -1

        boardScan = self.boardLevelUp(idx)

        if statesList[idx] == len(classes) - 1:
            raise RuntimeError("Wtf is this even. Note to come back to later?")
            return -1

        if boardScan["tieredUp2"] == True:
            print('fuck 3')
            return 10  # The shop unit will be consumed to tier up the units strictly on the board, bench is
            # untouched - NOTE - note - make sure bench labels are not updated as a result of this in future
            # make seperate function to update board labels!
        if boardScan["tieredUp3"] == True:
            return 11

        bench = {"tierTwo": boardScan["tierTwo"], "tierOne": boardScan["tierOne"],
                 "tierTwoHeroes": boardScan["tierTwoHeroes"],
                 "tierOneHeroes": boardScan["tierOneHeroes"]}

        for i in range(8):

            if self.benchHeroes[i]:
                if self.benchHeroes[i].name == classes[statesList[idx]]:

                    if self.benchHeroes[i].tier == 1:
                        bench["tierOne"] += 1
                        bench["tierOneHeroes"].append(self.benchHeroes[i])

                    elif self.benchHeroes[i].tier == 2:
                        bench["tierTwo"] += 1
                        bench["tierTwoHeroes"].append(self.benchHeroes[i])

        if bench["tierOne"] == self.levelThresh:  # If there is enough tier ones to make a tier 2,
            # first instance hero levels up, the rest should be removed from reference and update labels?

            bench["tierOneHeroes"][0].tier += 1

            # if bench["tierOneHeroes"][0].coords[1] == -1:
            #     self.benchLabels[bench["tierOneHeroes"][0].coords[0]].config(bg="blue")
            self.updateHeroLabel(bench["tierOneHeroes"][0])  # Updating label to for color to indicate tier

            bench["tierTwoHeroes"].append(bench["tierOneHeroes"][0])
            bench["tierTwo"] += 1
            tieredUp = 10

            for x in range(1, len(bench["tierOneHeroes"])):
                specificHero = bench["tierOneHeroes"][x]
                self.resetLabel(specificHero)

        if bench["tierTwo"] == self.levelThresh:

            bench["tierTwoHeroes"][0].tier += 1

            # if bench["tierTwoHeroes"][0].coords[1] == -1:
            #     self.benchLabels[bench["tierTwoHeroes"][0].coords[0]].config(bg="yellow")
            self.updateHeroLabel(bench["tierTwoHeroes"][0])  # Updating label to for color to indicate tier

            tieredUp = 11

            for x in range(1, len(bench["tierTwoHeroes"])):
                specificHero = bench["tierTwoHeroes"][x]
                self.resetLabel(specificHero)

        if tieredUp != 10:
            freeSpace = False

            for i in self.benchHeroes:
                if i is None:
                    freeSpace = True

            if not freeSpace:
                print("There is no space on bench to buy units!")
                self.mediumPunish = True
                return -1

        return tieredUp


def openVision():
    root = Tk()
    # root.geometry("600x105")
    root.resizable(0, 0)
    stopFlag = Event()
    thread = UnderlordInteract(root)
    # thread.start()
    # this will stop the timer
    # stopFlag.set()
    # shopFrame.pack()

    root.mainloop()


# openVision()
