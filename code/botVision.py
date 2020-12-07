import tkinter
from threading import Event, Thread
from tkinter import Frame, Tk, Label
from PIL import ImageTk
from HUD import HUD
from Shop import Shop


# from tkinter.ttk import Frame
# import tkinter as tk

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

        shopFrame.grid(row=1, column=0, pady=0, columnspan=5)
        self.itemLabel = Label(master=shopFrame, foreground='white', background='black', image=tempImage,
                               text="Hi", compound='top')

        self.itemLabel.grid(row=1, column=0, padx=5, pady=5, columnspan=5)
        shopFrame.pack()

    def run(self):
        while not self.stopped.wait(1):
            # print("Updating store")
            shopImages, classes, value, inspect, statesList = self.shop.labelShop()
            itemCounts, itemImage = self.HUD.getHUD()

            for i in range(5):
                tempImage = ImageTk.PhotoImage(shopImages[i])
                self.shopImages.append(tempImage)
                self.shopLabels[i].config(image=tempImage,
                                          text=f"{classes[statesList[i]]} {value[i] * 100:2.1f}%")

            itemImage = ImageTk.PhotoImage(itemImage)
            tempString = "Gold Count: %d" % itemCounts[0] + "\nHealth Count: %d" % itemCounts[1] + "\nUnit Count %d" % \
                         itemCounts[2]
            self.itemLabel.config(image=itemImage, text=tempString)


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
