import os
import time
from datetime import datetime

import random

from PIL import Image
from pynput.keyboard import Listener

from Shop import Shop
from main import imageGrab


def on_release(key):
    print(key)

    if str(key) == '\'r\'':
        time.sleep(random.random() * 2 + 0.2)
        cropShop(imageGrab(), True)


def cropShop(gameScreen, save=True):
    # shop = Image.open("test.jpg")
    # draw = ImageDraw.Draw(gameScreen)
    offset = 120
    imageList = []
    for i in range(5):
        # draw.rectangle((300, 90) + (400, 195))
        crop = gameScreen.crop((294 + i * offset, 70) + (388 + i * offset, 195))
        # draw.rectangle((294 + i*offset, 70) + (388 + i*offset, 195))

        imageList.append(crop)
        if save:
            crop.save("../WIP/" + str(datetime.now()).replace(":", "") + ".jpg")
    return imageList


def mains():
    with Listener(
            on_release=on_release) as listener:
        listener.join()


mains()
