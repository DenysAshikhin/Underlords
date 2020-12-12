import time
import tkinter
from threading import Event, Thread
from tkinter import Frame, Tk, Label

import win32gui
from PIL import ImageTk
from HUD import HUD
from Shop import Shop

from pynput import keyboard
from pynput.keyboard import Key, Controller, Listener

# from tkinter.ttk import Frame
# import tkinter as tk


keyboard1 = Controller()


def buy1():
    print('wow')
    hwnd = win32gui.FindWindow(None, 'Dota Underlords')
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(1)
    keyboard1.press('1')
    keyboard1.release('1')


def buy2():
    keyboard1.press('2')
    keyboard1.release('2')


def buy3():
    keyboard1.press('3')
    keyboard1.release('3')


def buy4():
    keyboard1.press('4')
    keyboard1.release('4')


def buy5():
    keyboard1.press('5')
    keyboard1.release('5')


storeMap = {
    0: None,
    1: buy1,
    2: buy2,
    3: buy3,
    4: buy4,
    5: buy5
}


def on_press(key):
    print(f"pressed ${key}")

def on_release(key):
    print(key)
    # if str(key) == '\'+\'' or str(key) == '\'=\'':
    #     Shop.cropShop(imageGrab())
    #     # Stop listener
    #     # return False
    #
    # # if str(key) == '\'-\'':
    # #     Gold.cropGold(imageGrab())
    #
    # if str(key) == '\'r\'':
    #     time.sleep(0.5)
    #     Shop.labelShop()


class ShopThread(Thread):
    def __init__(self, event, rootWindow):
        Thread.__init__(self)
        self.stopped = event
        self.rootWindow = rootWindow
        self.shop = Shop()
        self.HUD = HUD()

        shopImages, classes, value, inspect, statesList = self.shop.labelShop()

        self.shopLabels = []
        self.shopImages = []
        self.itemLabel = None
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
                command=storeMap[i + 1]
            )
            button.grid(row=1, column=i)

        shopFrame.grid(row=1, column=0, pady=0, columnspan=5)
        # self.itemLabel = Label(master=shopFrame, foreground='white', background='black', image=tempImage,
        #                        text="Hi", compound='top')
        #
        # self.itemLabel.grid(row=1, column=0, padx=5, pady=5, columnspan=5)
        shopFrame.pack()

    def run(self):
        while not self.stopped.wait(1):
           #  print("Updating store")
             if not self.toBuy == None:
                 print("Trying to buy")
        #     shopImages, classes, value, inspect, statesList = self.shop.labelShop()
        #     itemCounts, itemImage = self.HUD.getHUD()
        #
        #     for i in range(5):
        #         tempImage = ImageTk.PhotoImage(shopImages[i])
        #         self.shopImages.append(tempImage)
        #         self.shopLabels[i].config(image=tempImage,
        #                                   text=f"{classes[statesList[i]]} {value[i] * 100:2.1f}%")
        #     #  print(f"{classes[statesList[i]]} {value[i] * 100:2.1f}%")
        #
        #     itemImage = ImageTk.PhotoImage(itemImage)
        #     tempString = "Gold Count: %d" % itemCounts[0] + "\nHealth Count: %d" % itemCounts[1] + "\nUnit Count %d" % \
        #                  itemCounts[2]
        # # self.itemLabel.config(image=itemImage, text=tempString)


def openVision():
    root = Tk()
    # root.geometry("600x105")
    root.resizable(0, 0)
    stopFlag = Event()
    thread = ShopThread(stopFlag, root)
    storeMap[0] = thread
    thread.start()
    # this will stop the timer
    # stopFlag.set()
    # shopFrame.pack()

    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()


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
