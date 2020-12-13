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
        self.shop = Shop()
        self.HUD = HUD()
        self.bench = numpy.zeros([1, 8])
        self.board = numpy.zeros([4, 8])
        self.profilePics = loadProfiles()
        self.bought = None
        self.shopChoices = None
        self.storeMap = [350, 450, 575, 700, 800]
        self.purchaseHistory = []

        shopImages, classes, value, inspect, statesList = self.shop.labelShop()

        self.shopLabels = []
        self.shopImages = []
        self.benchLabels = []
        self.benchHeroes = [None, None, None, None, None, None, None, None]

        self.hudLabel = None
        self.toBuy = None
        shopFrame = Frame(
            master=rootWindow,
            relief=tkinter.RAISED,
            borderwidth=1
        )
        tempImage = ImageTk.PhotoImage(shopImages[0])
        for i in range(5):
            # print(f"Confidence {statesList[i] * 100}")
            label = Label(master=shopFrame, foreground='white', background='black', image=tempImage,
                          text=f"{classes[statesList[i]]} {value[i] * 100:.1f}%", compound='top')
            label.grid(row=0, column=i, padx=5, pady=5)
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
            button.grid(row=1, column=i)

        for x in range(8):
            newLabel = Label(master=shopFrame, foreground='white', background='black',
                             text=f"None", compound='top')
            newLabel.grid(row=4, column=x, padx=5, pady=5)
            self.benchLabels.append(newLabel)

            shopFrame.grid(row=1, column=0, pady=0, columnspan=5)
            self.hudLabel = Label(master=shopFrame, foreground='white', background='black',
                                  text="Hi", compound='top')

        self.hudLabel.grid(row=2, column=0, padx=5, pady=5, columnspan=5)
        shopFrame.pack()

    def run(self):
        while not self.stopped.wait(1):
            #  print("Updating store")
            if self.shopChoices is not None and self.bought is not None:
                shopImages, classes, value, inspect, statesList = self.shopChoices
                itemCounts, itemImage = self.HUD.getHUD()

                for i in range(5):
                    tempImage = ImageTk.PhotoImage(shopImages[i])
                    self.shopImages.append(tempImage)
                    self.shopLabels[i].config(image=tempImage,
                                              text=f"{classes[statesList[i]]} {value[i] * 100:2.1f}%")

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
                            break

    def toggleStore(self, coords):

        mouse1.position = coords
        mouse1.click(Button.left, 1)
        time.sleep(1)
        self.shopChoices = self.shop.labelShop()

    def buy(self, xPos=350, idx=0):

        if idx in self.purchaseHistory:
            print("Invalid attempt to buy a unit!")
            return -1

        hwnd = win32gui.FindWindow(None, 'Dota Underlords')
        win32gui.SetForegroundWindow(hwnd)

        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y

        self.toggleStore((x + 900, y + 65))

        mouse1.position = (x + xPos, y + 130)
        mouse1.click(Button.left, 1)

        if self.benchLevelUp(idx):
            self.bought = None
            return 1

        self.bought = idx

        # Expand this to take precedence for tiering up once it is relevant

    def boardLevelUp(self):

        levThresh = 2
        # Adding +1 to represent the shop unit coming in
        return {"tierTwo": 0, "tierOne": 0 + 1, "tierTwoHeroes": [], "tierOneHeroes": [], "tieredUp": False}

    def benchLevelUp(self, idx):

        levThresh = 2
        tieredUp = False
        shopImages, classes, value, inspect, statesList = self.shopChoices
        boardScan = self.boardLevelUp()

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

        if bench["tierOne"] == levThresh:  # If there is enough tier ones to make a tier 2,
            # first instance hero levels up, the rest should be removed from reference and update labels?

            bench["tierOneHeroes"][0].tier += 1

            if bench["tierOneHeroes"][0].coords[1] == -1:
                self.benchLabels[bench["tierOneHeroes"][0].coords[0]].config(bg="blue")

            bench["tierTwoHeroes"].append(bench["tierOneHeroes"][0])
            bench["tierTwo"] += 1
            tieredUp = True

            for x in range(1, len(bench["tierOneHeroes"])):

                specificHero = bench["tierOneHeroes"][x]

                if specificHero.coords[1] == -1:  # Only if this hero is located on the bench!
                    self.benchHeroes[specificHero.coords[0]] = None
                    self.benchLabels[specificHero.coords[0]].config(text="Tiered Up")
                # else
                # To do - note - NOTE add board logic wiping later

        if bench["tierTwo"] == levThresh:

            bench["tierTwoHeroes"][0].tier += 1

            if bench["tierTwoHeroes"][0].coords[1] == -1:
                self.benchLabels[bench["tierTwoHeroes"][0].coords[0]].config(bg="yellow")

            tieredUp = True

            for x in range(1, len(bench["tierTwoHeroes"])):

                specificHero = bench["tierTwoHeroes"][x]

                if specificHero.coords[1] == -1:  # Only if this hero is located on the bench!
                    self.benchHeroes[specificHero.coords[0]] = None
                    self.benchLabels[specificHero.coords[0]].config(text="Tiered Up", bg='black')
                # else
                # To do - note - NOTE add board logic wiping later

        #   print(bench)

        return tieredUp

    def updateBenchLabels(self):
        # To do
        return 1


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


def useless():
    print()
    # button = Button(
    #     text="Click me!",
    #     width=25,
    #     height=5,
    #     bg="blue",
    #     fg="yellow",
    # )
    # button.pack()
    # label = Label(
    #     master= shopFrame,
    #     text="This is the Shop!",
    #     fg="white",
    #     bg="black",
    #     width=10,
    #     height=10
    # )
    # label.pack()


openVision()
