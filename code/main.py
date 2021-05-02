import ctypes
import sys

import pywintypes
import win32con
import win32gui
from PIL import ImageGrab
from pynput.keyboard import Listener


# look at us now


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


def imageGrab(x = 0,y = 0,w = 0, h = 0, yoffset = 0, xoffset = 0):
    ctypes.windll.user32.SetProcessDPIAware()
    # get window handle and dimensions
    hwnd = win32gui.FindWindow(None, 'Dota Underlords')
    try:

        dimensions = win32gui.GetWindowRect(hwnd)
        # this gets the window size, comparing it to `dimensions` will show a difference
        # winsize = win32gui.GetClientRect(hwnd)

        # this sets window to front if it is not already
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                              win32con.SWP_SHOWWINDOW | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        x0, y0, w0, h0 = dimensions
        if x+xoffset+w == 0:
            w = w0

        if y+ yoffset+h == 0:
            h = h0

        crop_dimensions = (x0 + x + xoffset, y0 + y + yoffset, x0 + x + w + xoffset, y0 + y + h + yoffset)
        # grab screen region set in `dimensions`
        image = ImageGrab.grab(crop_dimensions)
        return image
    except pywintypes.error:
        print("Dota Underlords not OPEN!!!!")



# imageGrab(550, 10, 50, 56, 32, 3).save("test.jpg")

# cropGold(imageGrab())
# cropShop(imageGrab())
# loadOne()
# main()
