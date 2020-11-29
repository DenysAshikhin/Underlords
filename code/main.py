import os
import time

import torch
import torch.nn as nn
import win32gui, win32con, ctypes
from PIL import ImageGrab, Image, ImageDraw
from datetime import datetime
from pynput.keyboard import Listener
from torchvision import transforms
import Model


# look at us now
def on_release(key):
    if str(key) == '\'+\'':
        cropShop(imageGrab())
        # Stop listener
        # return False


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


def cropShop(shop):
    # shop = Image.open("test.jpg")
    draw = ImageDraw.Draw(shop)
    offset = 120
    for i in range(5):
        # draw.rectangle((300, 90) + (400, 195))
        crop = shop.crop((294 + i * offset, 70) + (388 + i * offset, 195))
        # draw.rectangle((294 + i*offset, 70) + (388 + i*offset, 195))
        print(str(datetime.now()))
        crop.save("./WIP/" + str(datetime.now()).replace(":", "") + ".jpg")
    # shop.show()


def loadOne():
    data_transform = transforms.Compose([transforms.ToTensor(),
                                         transforms.Normalize((0.5,), (0.5,), (0.5,)),
                                         ])
    data = []

    net = Model.Net()
    net.load_state_dict(torch.load("model.pth"))

    def listdirs(path):
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    class_path = "./Pics"
    classes = listdirs(class_path)
    print(len(classes))

    image_root = "./WIP"
    image_list = []
    for file in os.listdir(image_root):
        data.append(data_transform(Image.open(image_root + "/" + file)))
        image_list.append(Image.open(image_root + "/" + file))

    # conve rt image to tensor
    out = torch.stack(data, dim=0)  # output all images as one tensor
    print(out)
    m = nn.Softmax(dim=1)
    # Perform forward pass with ANN

    out = net(out)  # use model to evaluate
    out = m(out)  # apply softmax

    save_path = "./save/"

    value, inspect = torch.max(out, 1)
    cnt = 0
    for i, img in enumerate(inspect):
        state = img.item()
        folder_name = classes[state]
        text = str(classes[state])
        # print(text)
        # draw = ImageDraw.Draw(image_list[cnt])
        # draw.text(( 10, 20), text)
        # draw.text((10, 5), str(value[cnt]))
        # image_list[cnt].show()
        # time.sleep(1)
        # image_list[cnt].save(save_path+folder_name+"/"+str(datetime.now()).replace(":","")+".jpg")
        cnt += 1


def main():
    with Listener(
            on_release=on_release) as listener:
        listener.join()

# cropShop(imageGrab())
# loadOne()
# main()
# Model.train()
