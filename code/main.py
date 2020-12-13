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


def imageGrab():
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

        # grab screen region set in `dimensions`
        image = ImageGrab.grab(dimensions)
        return image
    except pywintypes.error:
        print("Dota Underlords not OPEN!!!!")
        sys.exit()



def main():
    with Listener(
            on_release=on_release) as listener:
        listener.join()

# cropGold(imageGrab())
# cropShop(imageGrab())
# loadOne()
# main()
