import os
import time
from datetime import datetime

import ctypes
import torch
import torch.nn as nn
import win32con
import win32gui
from PIL import ImageGrab, Image, ImageDraw
from pynput.keyboard import Listener
from torchvision import transforms

import Model


# look at us now
def on_release(key):
    print(key)
    if str(key) == '\'+\'':
        cropShop(imageGrab())
        # Stop listener
        # return False
    if str(key) == '\'r\'':
        time.sleep(0.5)
        labelShop()


def imageGrab():
    ctypes.windll.user32.SetProcessDPIAware()

    # get window handle and dimensions
    hwnd = win32gui.FindWindow(None, 'Dota Underlords')
    dimensions = win32gui.GetWindowRect(hwnd)

    # this gets the window size, comparing it to `dimensions` will show a difference
    winsize = win32gui.GetClientRect(hwnd)

    # this sets window to front if it is not already
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                          win32con.SWP_SHOWWINDOW | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    # grab screen region set in `dimensions`
    image = ImageGrab.grab(dimensions)
    return image
    # image.show()
    # image.save("test.jpg")


def cropShop(shop, save=True):
    # shop = Image.open("test.jpg")
    draw = ImageDraw.Draw(shop)
    offset = 120
    imageList = []
    for i in range(5):
        # draw.rectangle((300, 90) + (400, 195))
        crop = shop.crop((294 + i * offset, 70) + (388 + i * offset, 195))
        # draw.rectangle((294 + i*offset, 70) + (388 + i*offset, 195))
        # print(str(datetime.now()))

        crop.show()
        print(str(datetime.now()))
        imageList.append(crop)
        if save:
            crop.save("./WIP/" + str(datetime.now()).replace(":", "") + ".jpg")
    return imageList


def labelShop():
    imageList = cropShop(imageGrab(), save=False)
    value, inspect = predict(imageList)
    classes = getClasses()

    for i, img in enumerate(inspect):
        state = img.item()
        print("Position %d:" % i, "Label: %s" % classes[state], "Confidence: %f" % value[i])


def getClasses():
    def listdirs(path):
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    class_path = "../Pics"
    classes = listdirs(class_path)
    return classes


def loadOne():
    image_root = "/WIP"
    image_list = []

    for file in os.listdir(image_root):
        image_list.append(Image.open(image_root + "/" + file))

    save_path = "./save/"
    cnt = 0
    value, inspect = predict(image_list)
    classes = getClasses()

    for i, img in enumerate(inspect):
        state = img.item()
        folder_name = classes[state]
        image_list[cnt].save(save_path + folder_name + "/" + str(datetime.now()).replace(":", "") + ".jpg")
        cnt += 1
    return True


# Given a list of images, run a forward pass with CNN and return predictions
def predict(imageList):
    data_transform = transforms.Compose([transforms.ToTensor(),
                                         transforms.Normalize((0.5,), (0.5,), (0.5,)),
                                         ])
    data = []

    for img in imageList:
        data.append(data_transform(img))

    net = Model.Net(n_chans1=7, stride1=1, stride2=1, finalChannel=47)
    net.load_state_dict(torch.load("model.pth", map_location=torch.device('cpu')))

    # conve rt image to tensor
    out = torch.stack(data, dim=0)  # output all images as one tensor
    m = nn.Softmax(dim=1)
    # Perform forward pass with ANN

    if (torch.cuda.is_available()):
        DEVICE = 'cuda'
        # print("cuda")
        net.cuda()
        net.load_state_dict(torch.load("model.pth"))
        out = out.cuda()
    else:
        DEVICE = 'cpu'
        net.load_state_dict(torch.load("model_CPU.pth"))

    out = net(out)  # use model to evaluate
    out = m(out)  # apply softmax
    value, inspect = torch.max(out, 1)

    return value, inspect


def main():
    with Listener(
            on_release=on_release) as listener:
        listener.join()


# cropShop(imageGrab())
# loadOne()
main()
