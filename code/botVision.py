import tkinter
from threading import Event, Thread
from tkinter import Frame, Tk, Label

from PIL import ImageTk
from Gold import Gold
from Shop import Shop
import main


# from tkinter.ttk import Frame
# import tkinter as tk



class controlWindow(Frame):

    def __init__(self):
        super().__init__()
        self.gold = Gold()
        self.shop = Shop()
        self.update()


class ShopThread(Thread):
    def __init__(self, event, rootWindow):
        Thread.__init__(self)
        self.stopped = event
        self.rootWindow = rootWindow
        self.shop = Shop()
        self.gold = Gold()

        shopImages, classes, value, inspect, statesList = self.shop.labelShop()

        self.shopLabels = []
        self.shopImages = []
        for i in range(5):
            shopFrame = Frame(
                master=rootWindow,
                relief=tkinter.RAISED,
                borderwidth=1
            )
            shopFrame.grid(row=0, column=i, padx=5, pady=5)

            tempImage = ImageTk.PhotoImage(shopImages[0])
            print(f"Confidence {statesList[i] * 100}")
            label = label = Label(master=shopFrame, foreground='white', background='black', image=tempImage,
                                  text=f"{classes[statesList[i]]} {value[i] * 100:.1f}%", compound='top')
            self.shopLabels.append(label)
            label.pack()

    def run(self):
        while not self.stopped.wait(1):
            print("Updating store")
            shopImages, classes, value, inspect, statesList = self.shop.labelShop()

            for i in range(5):
                tempImage = ImageTk.PhotoImage(shopImages[i])
                self.shopImages.append(tempImage)
                self.shopLabels[i].config(image=tempImage,
                                          text=f"{classes[statesList[i]]} {value[i] * 100:2.1f}%")


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


def useles():
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
