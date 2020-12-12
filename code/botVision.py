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

        shopImages, classes, value, inspect, statesList = self.shop.labelShop()

        self.shopLabels = []
        self.shopImages = []
        self.benchLabels = []
        self.benchLabelHero = [None, None, None, None, None, None, None, None]

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

                        if self.benchLabelHero[x] is None:
                            self.benchLabelHero[x] = classes[statesList[self.bought]]
                            self.bought = None
                            self.benchLabels[x].config(text=f"{self.benchLabelHero[x]}",
                                                       image=self.profilePics[self.benchLabelHero[x]])
                            break

    def toggleStore(self, coords):
        mouse1.position = coords
        mouse1.click(Button.left, 1)
        time.sleep(1)
        self.shopChoices = self.shop.labelShop()

    def buy(self, xPos=350, idx=0):

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
        self.bought = idx



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
