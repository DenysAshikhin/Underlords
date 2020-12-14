import os
import time
import tkinter
from threading import Event, Thread
from tkinter import Frame, Tk, Label

import numpy
import win32gui
from PIL import ImageTk, Image
from HUD import HUD
from Shop import Shop

from hero import Hero
from pynput.mouse import Button, Controller as MouseController

mouse1 = MouseController()


def loadProfiles():
    root = os.path.join(os.path.dirname(os.getcwd()), "final profile pics")
    profileMap = {}
    for file in os.listdir(root):
        img = Image.open(os.path.join(root, file))
        img = ImageTk.PhotoImage(img)
        profileMap[file[: -4]] = img
    return profileMap


class ShopThread(Thread):
    def __init__(self, event, rootWindow):
        Thread.__init__(self)
        self.stopped = event
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
        self.benchX = 200
        self.benchXOffset = 40
        self.benchY = 600
        self.boardX = 210
        self.boardXOffset = 40
        self.boardY = 300
        self.boardYOffset = 20

        self.heroToMove = None

        self.shop = Shop()
        self.HUD = HUD()
        self.bench = numpy.zeros([1, 8])
        self.board = numpy.zeros([4, 8])
        self.profilePics = loadProfiles()
        self.bought = None
        self.shopChoices = None
        self.storeMap = [350, 450, 575, 700, 800]
        self.purchaseHistory = []
        self.updateShop = False

        shopImages, classes, value, inspect, statesList = self.shop.labelShop()

        self.shopLabels = []
        self.shopImages = []
        self.benchLabels = []
        self.benchHeroes = [None, None, None, None, None, None, None, None]
        self.boardLabels = numpy.full((4, 8), None)
        self.boardHeroes = numpy.full((4, 8), None)
        # self.boardHeroes = numpy.empty((4, 8))
        # self.boardHeroes[:] = None
        self.boardHeroes = self.boardHeroes.tolist()

        self.levelThresh = 2

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

        hudRow = 14

        # 8 bench portrait slots
        for x in range(8):
            newLabel = Label(master=shopFrame, foreground='white', background='black',
                             text=f"None", compound='top')
            newLabel.grid(row=hudRow + 1, column=x, padx=5, pady=5)
            self.benchLabels.append(newLabel)
            tempButton = tkinter.Button(master=shopFrame, text="Move", width=4, height=1,
                                        command=lambda pos=x, idx=-1: self.moveUnit(x=pos, y=idx))
            tempButton.grid(row=hudRow + 2, column=x)

        # shopFrame.grid(row=1, column=0, pady=0, columnspan=5)
        self.hudLabel = Label(master=shopFrame, foreground='white', background='black',
                              text="Hi", compound='top')

        self.hudLabel.grid(row=hudRow, column=3, padx=5, pady=5)

        self.rerollButton = tkinter.Button(
            master=shopFrame,
            text="Reroll",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=self.rerollStore
        )
        self.rerollButton.grid(row=hudRow, column=1)

        self.clickUpButton = tkinter.Button(
            master=shopFrame,
            text="Click Up",
            width=10,
            height=1,
            bg="blue",
            fg="yellow",
            command=self.clickUp
        )
        self.clickUpButton.grid(row=hudRow, column=2)

        for i in range(4):
            for j in range(8):
                newLabel = Label(master=shopFrame, foreground='white', background='black',
                                 text=f"None", compound='top')
                newLabel.grid(row=3 + (2 * i), column=j, padx=3, pady=2)
                self.boardLabels[i][j] = newLabel
                tempButton = tkinter.Button(master=shopFrame, text="Move", width=4, height=1,
                                            command=lambda pos=i, idx=j: self.moveUnit(x=pos, y=idx))
                tempButton.grid(row=4 + (2 * i), column=j)

        shopFrame.pack()

    def run(self):
        while not self.stopped.wait(1):
            #  print("Updating store")
            if self.shopChoices is not None and self.bought is not None or self.updateShop:

                if self.updateShop:
                    self.shopChoices = self.shop.labelShop()

                shopImages, classes, value, inspect, statesList = self.shopChoices

                itemCounts, itemImage = self.HUD.getHUD()

                for i in range(5):
                    tempImage = ImageTk.PhotoImage(shopImages[i])
                    self.shopImages.append(tempImage)
                    self.shopLabels[i].config(image=tempImage,
                                              text=f"{classes[statesList[i]]} {value[i] * 100:2.1f}%")
                    # print(f"{classes[statesList[i]]} {value[i] * 100:2.1f}%")

                # itemImage = ImageTk.PhotoImage(itemImage)
                tempString = "\nUnit Count %d" % itemCounts[2] + "\nGold Count: %d" % itemCounts[
                    0] + "\nHealth Count: %d" % \
                             itemCounts[1]
                self.hudLabel.config(text=tempString)

                if self.bought is not None:
                    for x in range(8):

                        if self.benchHeroes[x] is None:
                            self.benchHeroes[x] = Hero(classes[statesList[self.bought]], (x, -1),
                                                       self.profilePics[classes[statesList[self.bought]]])

                            self.bought = None
                            self.benchLabels[x].config(text=f"{self.benchHeroes[x].name}",
                                                       image=self.benchHeroes[x].image)
                            self.updateShop = True
                            break
                else:
                    self.updateShop = False

    def moveGameHero(self, hero, newX, newY):

        self.updateWindowCoords()

        heroX, heroY = hero.coords

        if heroY == -1:
            mouse1.position = (self.benchX + (self.benchXOffset * heroX), self.benchY)
        else:
            mouse1.position = (self.boardX + (self.boardXOffset * heroY), self.boardY + (self.boardYOffset * heroX))
           # print(f"Moving to board {mouse1.position}")

        mouse1.press(Button.left)

        time.sleep(0.25)

        if newY == -1:  # Moving onto the bench
            mouse1.position = (self.benchX + (self.benchXOffset * newX), self.benchY)
           # print(f"Moving to bench {mouse1.position}")

        else:
            mouse1.position = (self.boardX + (self.boardXOffset * newY), self.boardY + (self.boardYOffset * newX))
           # print(f"Moving to board {mouse1.position}")
        time.sleep(0.25)
        mouse1.release(Button.left)

    def clickUp(self):
        self.openStore()
        mouse1.position = (self.clickUpX, self.clickUpY)
        mouse1.click(Button.left, 1)
        self.shopChoices = self.shop.labelShop()
        self.updateShop = True

    def rerollStore(self):
        self.openStore()
        mouse1.position = (self.rerollX, self.rerollY)
        mouse1.click(Button.left, 1)
        time.sleep(0.5)
        self.shopChoices = self.shop.labelShop()
        self.updateShop = True

    def openStore(self):

        self.updateWindowCoords()

        if not self.shop.shopOpen():
            mouse1.position = (self.shopX, self.shopY)
            mouse1.click(Button.left, 1)
            time.sleep(1)
        self.shopChoices = self.shop.labelShop()

    def updateWindowCoords(self):
        self.hwnd = win32gui.FindWindow(None, 'Dota Underlords')
        win32gui.SetForegroundWindow(self.hwnd)

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

        self.benchX = self.x + 260
        self.benchXOffset = 88
        self.benchY = self.y + 820
        self.boardX = self.x + 330
        self.boardXOffset = 73
        self.boardY = self.y + 420
        self.boardYOffset = 70

    def moveUnit(self, x=-1, y=-1):

        if self.heroToMove:  # If a hero has been selected to move previously
            if y == -1:  # Meaning we are moving onto a bench spot
                if self.benchHeroes[x] is None:  # Making sure bench spot is open
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
                    print("calling board move")
                    self.boardHeroes[x][y] = self.heroToMove
                    self.resetLabel(self.heroToMove)
                    self.moveGameHero(self.heroToMove, x, y)
                    self.heroToMove.coords = (x, y)
                    self.updateHeroLabel(self.heroToMove)
                    self.heroToMove = None

                else:
                    print("Board Spot Taken!")
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

        if y == -1:  # Meaning we are working with bench
            self.benchLabels[x].config(image=hero.image, text=hero.name, bg=color)
        else:

            self.boardLabels[x][y].config(
                image=hero.image,
                text=hero.name,
                bg=color)

    def buy(self, xPos=350, idx=0):

        if idx in self.purchaseHistory:  # Note - note - still need to implement the validation logic at some point
            print("Invalid attempt to buy a unit!")
            return -1

        self.openStore()

        mouse1.position = (self.x + xPos, self.y + 130)
        mouse1.click(Button.left, 1)

        if self.benchLevelUp(idx):
            self.bought = None
            return 1

        self.bought = idx

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

        bench = {"tierTwo": boardScan["tierTwo"], "tierOne": boardScan["tierOne"], "tierTwoHeroes": [],
                 "tierOneHeroes": []}

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
    thread = ShopThread(stopFlag, root)
    thread.start()
    # this will stop the timer
    # stopFlag.set()
    # shopFrame.pack()

    root.mainloop()


openVision()
