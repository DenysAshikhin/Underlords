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


class ShopThread():
    def __init__(self, rootWindow, training=False):
        # Thread.__init__(self)
        # self.stopped = event
        self.rootWindow = rootWindow

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
        self.itemSelectX = self.x + 350
        self.itemSelectXOffset = 220
        self.itemRerollX = self.itemSelectX + self.itemSelectXOffset
        self.itemRerollY = self.itemSelectY + 200
        self.itemMoveX = self.x + 965
        self.itemMoveXOffset = 40
        self.itemMoveY = self.y + 290
        self.itemMoveYOffset = 35
        self.gameState = None
        self.gameStateLoader = state()

        self.updateWindowCoords()

        self.choseItem = False
        self.rerolledItem = False
        self.selected = False

        self.heroToMove = None
        self.itemToMove = None

        self.shopSleepTime = 0.4
        self.mouseSleepTime = 0.25

        self.shop = Shop()
        self.HUD = HUD()
        self.items = Items()
        self.itemIDmap = self.items.itemIDMap
        self.underlords = Underlords()
        self.bench = numpy.zeros([1, 8])
        self.board = numpy.zeros([4, 8])
        self.profilePics = loadProfiles()
        self.underlordPics = loadUnderlodProfiles()
        self.shopChoices = None
        self.storeMap = [350, 450, 575, 700, 800]
        self.purchaseHistory = []
        self.gold = -1
        self.health = -1
        self.level = -1

        shopImages, classes, value, inspect, statesList = self.shop.labelShop()

        self.shopLabels = []
        self.shopImages = []
        self.benchLabels = []
        self.benchHeroes = [None, None, None, None, None, None, None, None]
        self.boardLabels = numpy.full((4, 8), None)
        self.boardHeroes = numpy.full((4, 8), None)
        self.itemObjects = numpy.full((3, 4), None)
        self.itemlabels = numpy.full((3, 4), None)
        self.underlord = None

        # self.boardHeroes = numpy.empty((4, 8))
        # self.boardHeroes[:] = None
        self.boardHeroes = self.boardHeroes.tolist()

        self.levelThresh = 2  # level threshold for tiering up a unit

        self.hudLabel = None
        self.toBuy = None
        shopFrame = Frame(
            master=rootWindow,
            relief=tkinter.RAISED,
            borderwidth=1
        )
        tempImage = ImageTk.PhotoImage(shopImages[0])

        # Initialize 5 pictures for shop, 5 purchase buttons
        for i in range(5):
            # print(f"Confidence {statesList[i] * 100}")
            label = Label(master=shopFrame, foreground='white', background='black', image=tempImage,
                          text=f"{classes[statesList[i]]} {value[i] * 100:.1f}%", compound='top')
            label.grid(row=0, column=i + 1, padx=5, pady=5)
            if not training:
                self.shopLabels.append(label)
                button = tkinter.Button(
                    master=shopFrame,
                    text="Purchase",
                    width=10,
                    height=1,
                    bg="blue",
                    fg="yellow",
                    command=lambda pos=self.storeMap[i], idx=i: self.buy(xPos=pos, idx=idx)
                )
                button.grid(row=1, column=i + 1)

        self.itemFrame = Frame(master=shopFrame, relief=tkinter.RAISED, borderwidth=1)
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
            newLabel = Label(master=shopFrame, foreground='white', background='black',
                             text=f"None", compound='top')
            newLabel.grid(row=hudRow + 2, column=x, padx=5, pady=5)
            self.benchLabels.append(newLabel)
            if not training:
                tempButton = tkinter.Button(master=shopFrame, text="Move", width=4, height=1,
                                            command=lambda pos=x, idx=-1: self.moveUnit(x=pos, y=idx))
                tempButton.grid(row=hudRow + 3, column=x)

        # shopFrame.grid(row=1, column=0, pady=0, columnspan=5)
        self.hudLabel = Label(master=shopFrame, foreground='white', background='black',
                              text="Hi", compound='top')

        self.hudLabel.grid(row=hudRow, column=4, padx=5, pady=5)

        self.rerollButton = tkinter.Button(
            master=shopFrame,
            text="Reroll",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=self.rerollStore
        )
        self.rerollButton.grid(row=hudRow, column=3)

        self.buyItem1 = tkinter.Button(
            master=shopFrame,
            text="buyItem1",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=lambda pos=0: self.selectItem(selection=pos)
        )
        self.buyItem1.grid(row=hudRow + 1, column=0)
        self.buyItem2 = tkinter.Button(
            master=shopFrame,
            text="buyItem2",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=lambda pos=1: self.selectItem(selection=pos)
        )
        self.buyItem2.grid(row=hudRow + 1, column=1)
        self.buyItem3 = tkinter.Button(
            master=shopFrame,
            text="buyItem3",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=lambda pos=2: self.selectItem(selection=pos)
        )
        self.buyItem3.grid(row=hudRow + 1, column=2)
        self.buyItem4 = tkinter.Button(
            master=shopFrame,
            text="buyItem4",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=lambda pos=3: self.selectItem(selection=pos)
        )
        self.buyItem4.grid(row=hudRow + 1, column=3)

        self.testButton = tkinter.Button(
            master=shopFrame,
            text='Test Button',
            width=10,
            height=1,
            bg='blue',
            fg='yellow',
            # command=lambda underlor='healing_tank', selecty=3: self.buyUnderlord(underlord=underlor, selection=selecty)
            command=lambda x=3, y=2: self.testFunction(x, y)
        )
        self.testButton.grid(row=hudRow + 1, column=4)

        self.refreshStore = tkinter.Button(
            master=shopFrame,
            text='Refresh Store',
            width=10,
            height=1,
            bg='blue',
            fg='yellow',
            # command=lambda underlor='healing_tank', selecty=3: self.buyUnderlord(underlord=underlor, selection=selecty)
            command=self.updateShop
        )
        self.refreshStore.grid(row=hudRow + 1, column=5)

        self.sellButton = tkinter.Button(
            master=shopFrame,
            text="Sell",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=self.sellHero
        )
        self.sellButton.grid(row=hudRow, column=2)

        self.lockIn = tkinter.Button(
            master=shopFrame,
            text="Lock in",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=self.lockIn
        )
        self.lockIn.grid(row=hudRow, column=1)

        self.clickUpButton = tkinter.Button(
            master=shopFrame,
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
                newLabel = Label(master=shopFrame, foreground='white', background='black',
                                 text=f"None", compound='top')
                newLabel.grid(row=3 + (2 * i), column=j, padx=3, pady=2)
                self.boardLabels[i][j] = newLabel

                if not training:
                    tempButton = tkinter.Button(master=shopFrame, text="Move", width=4, height=1,
                                                command=lambda pos=i, idx=j: self.moveUnit(x=pos, y=idx))
                    tempButton.grid(row=4 + (2 * i), column=j)

        shopFrame.pack()

    def testFunction(self, param1, param2):

        # self.updateWindowCoords()
        #
        # testX = self.x + 965
        # testXOffest = 40
        #
        # testY = self.y + 145
        # testYOffset = 35
        #
        # mouse1.position = (testX + (testXOffest * param1), testY + (testYOffset * param2))

        # for i in range(3):
        #     for j in range(4):
        #         if self.itemObjects[i][j] is None:
        #             self.itemObjects[i][j] = Item(f"temp item: {i} - {j}", (i, j))
        #             self.itemlabels[i][j].config(text=self.itemObjects[i][j].name)
        #             return
        #
        found = False
        i = 0
        bannedItems = []
        notBannedItems = []

        fullItemList = itemNameList()

        print(fullItemList)

        self.shopChoices = self.shop.labelShop()

        shopImages, classes, value, inspect, statesList = self.shopChoices

        for underlord in classes:

            for item in fullItemList:

                self.itemToMove = Item(item, (0, 0), ID=0)
                hero = Hero(underlord, (0, 0), None, False, 0)

                if self.updateHeroItem(hero) == -1:
                    if item not in bannedItems:
                        bannedItems.append(item)


        print(f"Items that were banned:")
        print(bannedItems)

        print(f"Items that should be banned:")
        print(self.items.banned)
        print("dragon lance, refresher orb, battle fury")
        self.itemToMove = Item('refresher orb', (0, 0), ID=0)
        hero = Hero('slark', (0, 0), None, False, 0)
        hero.tier = 2
        print(f"result of test: {self.updateHeroItem(hero)}")

    def selectItem(self, x=-1, y=-1, selection=-1):

        if selection != -1:

            items = self.items.checkItems()

            if items[0] is None:

                underlords = self.underlords.checkUnderlords()

                if underlords[0] is None:

                    print("No Underlord or item available for selection!")
                    return -1

                else:
                    self.buyUnderlord(underlords[selection], selection)
            else:
                self.buyItem(selection, items)

        else:

            if self.heroToMove:
                print("You have a hero selected to move, move it first!")
                return -1

            if self.itemObjects[x][y] is None:
                print("there is no item to select here!")
            else:
                self.itemToMove = self.itemObjects[x][y]

    def buyItem(self, selection, itemList):

        if selection == 3:
            if self.rerolledItem:
                raise RuntimeError("Can't reroll an item twice - Was this properly implemented?")
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
                        self.itemObjects[i][j] = Item(itemList[selection], (i, j),
                                                      ID=self.itemIDmap[itemList[selection]])
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
        elif underlord == 'rapid_furbal':
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
                self.underlord = Hero(underlord, (x, y), self.underlordPics[underlord], True, ID=ID)
                self.updateHeroLabel(self.underlord)
                self.boardHeroes[x][y] = self.underlord
                return

    def updateShop(self):

        self.openStore()

        time.sleep(self.shopSleepTime)

        self.shopChoices = self.shop.labelShop()

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
                     + "\nHealth Count: %d" % itemCounts[1]
        self.hudLabel.config(text=tempString)
        self.gold = itemCounts[0]
        self.level = itemCounts[2]
        self.health = itemCounts[1]

    def sellHero(self, x=-1, y=-1):

        if x == -1:
            if self.heroToMove is None:
                print("No Hero Selected to Sell")
                return -1
            else:
                x, y = self.heroToMove.coords
        else:
            if y == -1:
                if self.benchHeroes[x] is None:
                    print(f"No hero on bench spot {x + 1} to sell!")
                    return -1
            elif self.boardheroes[x][y] is None:
                print(f"No hero on board spot {x + 1}-{y + 1} to sell!")
                return -1

        if y == -1:
            mouse1.position = (self.benchX + (self.benchXOffset * x), self.benchY)
            self.resetLabel(self.benchHeroes[x])
            self.heroToMove = None
        else:
            mouse1.position = (self.boardX + (self.boardXOffset * y), self.boardY + (self.boardYOffset * x))
            self.resetLabel(self.boardHeroes[x][y])
            self.heroToMove = None
        # print(f"Moving to board {mouse1.position}")

        self.updateWindowCoords()

        mouse1.press(Button.left)

        time.sleep(self.mouseSleepTime)

        mouse1.position = (self.x + 50, self.y + 800)

        time.sleep(self.mouseSleepTime)

        mouse1.release(Button.left)

        return -1

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

    def clickUp(self):
        self.openStore()
        mouse1.position = (self.clickUpX, self.clickUpY)
        mouse1.click(Button.left, 1)
        self.shopChoices = self.shop.labelShop()
        self.updateShop()

    def lockIn(self):

        self.openStore()
        mouse1.position = (self.lockInX, self.lockInY)
        mouse1.click(Button.left, 1)

    def rerollStore(self):
        self.openStore()
        mouse1.position = (self.rerollX, self.rerollY)
        mouse1.click(Button.left, 1)
        self.shopChoices = self.shop.labelShop()
        self.updateShop()

    def openStore(self):

        self.updateWindowCoords()

        if not self.shop.shopOpen():
            mouse1.position = (self.shopX, self.shopY)
            mouse1.click(Button.left, 1)

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
        self.itemSelectX = self.x + 350
        self.itemSelectXOffset = 220
        self.itemRerollX = self.itemSelectX + self.itemSelectXOffset
        self.itemRerollY = self.itemSelectY + 200
        self.itemMoveX = self.x + 965
        self.itemMoveXOffest = 40
        self.itemMoveY = self.y + 290
        self.itemMoveYOffset = 35

    def moveUnit(self, x=-1, y=-1):

        if self.heroToMove:  # If a hero has been selected to move previously
            if y == -1:  # Meaning we are moving onto a bench spot

                if self.heroToMove.underlord:
                    print("Can't place an underlord onto a bench!")
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
                    return -1
            else:  # Meaning we are moving onto a board spot
                if self.boardHeroes[x][y] is None:  # Making sure board spot is open
                    self.boardHeroes[x][y] = self.heroToMove
                    self.resetLabel(self.heroToMove)
                    self.moveGameHero(self.heroToMove, x, y)
                    self.heroToMove.coords = (x, y)
                    self.updateHeroLabel(self.heroToMove)
                    self.heroToMove = None

                else:
                    print("Board Spot Taken!")
                    return -1

        elif self.itemToMove:  # Meaning we are trying to attach an item to a hero

            if y == -1:  # Meaning we are attaching an item to a unit on bench
                if self.benchHeroes[x] is not None:  # Making sure bench spot has a hero
                    self.updateHeroItem(self.benchHeroes[x])

                else:
                    print("No Hero On This Bench!")
                    return -1
            else:
                if self.boardHeroes[x][y] is not None:  # Making sure board spot has a hero
                    if self.boardHeroes[x][y].underlord:
                        print("Can't attach items to Underlords!")
                        return -1
                    self.updateHeroItem(self.boardHeroes[x][y])

                else:
                    print("No Hero On This Board!")
                    return -1

        else:  # Meaning a hero has not yet been selected for movement, mark this hero as one to move
            if y == -1:  # Meaning we are moving onto a bench spot
                if self.benchHeroes[x] is not None:  # Making sure bench spot has a hero
                    self.heroToMove = self.benchHeroes[x]
                else:
                    print("No Hero On This Bench!")
                    return -1
            else:
                if self.boardHeroes[x][y] is not None:  # Making sure board spot has a hero
                    self.heroToMove = self.boardHeroes[x][y]
                else:
                    print("No Hero On This Board!")
                    return -1

        return 1

    def updateHeroItem(self, hero):

        if self.itemToMove.name in self.items.banned:
            # print('This item is not allowed to be used')
            return -1
        elif self.itemToMove.name in self.items.unique:

            if hero.name in self.items.bannedUnderlords[self.itemToMove.name]:
                # print('This item cannot be equipped on this hero')

                if hero.name in self.items.bannedUnderlords['t3 refresher orb'] and self.itemToMove.name == 'refresher orb' and hero.tier == 3:
                    return
                return -1

        # self.updateWindowCoords()
        #
        originalHero = self.itemToMove.hero
        #
        # mouse1.position = (self.itemMoveX + (self.itemMoveXOffset * self.itemToMove.coords[1]),
        #                    self.itemMoveY + (self.itemMoveYOffset * self.itemToMove.coords[0]))
        #
        # mouse1.press(Button.left)
        # time.sleep(self.mouseSleepTime)

        heroX, heroY = hero.coords

        # if heroY == -1:
        #     mouse1.position = (self.benchX + (self.benchXOffset * heroX), self.benchY)
        # else:
        #     mouse1.position = (self.boardX + (self.boardXOffset * heroY), self.boardY + (self.boardYOffset * heroX))
        #
        # time.sleep(self.mouseSleepTime)
        # mouse1.release(Button.left)

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

    def buy(self, xPos=350, idx=0):
        if idx in self.purchaseHistory:  # Note - note - still need to implement the validation logic at some point
            print("Invalid attempt to buy a unit!")
            return -1

        freeSpace = False

        for i in self.benchHeroes:
            if i is None:
                freeSpace = True

        if not freeSpace:
            print("There is no space on bench to buy units!")
            return -1

        self.openStore()

        mouse1.position = (self.x + xPos, self.y + 130)
        mouse1.click(Button.left, 1)

        if self.benchLevelUp(idx):
            return 1

        shopImages, classes, value, inspect, statesList = self.shopChoices

        for x in range(8):

            if self.benchHeroes[x] is None:
                self.benchHeroes[x] = Hero(classes[statesList[idx]], (x, -1),
                                           self.profilePics[classes[statesList[idx]]],
                                           ID=statesList[idx])

                self.benchLabels[x].config(text=f"{self.benchHeroes[x].name}",
                                           image=self.benchHeroes[x].image)
                self.updateShop()
                return

    def boardLevelUp(self, idx):

        # Adding +1 to represent the shop unit coming in
        board = {"tierTwo": 0, "tierOne": 0 + 1, "tierTwoHeroes": [], "tierOneHeroes": [], "tieredUp": False}
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
        boardScan = self.boardLevelUp(idx)

        if statesList[idx] == len(classes) - 1:
            return True

        if boardScan["tieredUp"] == True:
            return True  # The shop unit will be consumed to tier up the units strictly on the board, bench is
            # untouched - NOTE - note - make sure bench labels are not updated as a result of this in future
            # make seperate function to update board labels!

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
            tieredUp = True

            for x in range(1, len(bench["tierOneHeroes"])):
                specificHero = bench["tierOneHeroes"][x]
                self.resetLabel(specificHero)

        if bench["tierTwo"] == self.levelThresh:

            bench["tierTwoHeroes"][0].tier += 1

            # if bench["tierTwoHeroes"][0].coords[1] == -1:
            #     self.benchLabels[bench["tierTwoHeroes"][0].coords[0]].config(bg="yellow")
            self.updateHeroLabel(bench["tierTwoHeroes"][0])  # Updating label to for color to indicate tier

            tieredUp = True

            for x in range(1, len(bench["tierTwoHeroes"])):
                specificHero = bench["tierTwoHeroes"][x]
                self.resetLabel(specificHero)

        return tieredUp


def openVision():
    root = Tk()
    # root.geometry("600x105")
    root.resizable(0, 0)
    stopFlag = Event()
    thread = ShopThread(root)
    # thread.start()
    # this will stop the timer
    # stopFlag.set()
    # shopFrame.pack()

    root.mainloop()


openVision()
