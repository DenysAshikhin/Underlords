import MTM
import cv2
import numpy
import configparser

from PIL import Image

from main import imageGrab


def detectOffset():
    offsetTemplate = cv2.imread("../Header Texts/F.jpg")
    template = [("F", offsetTemplate)]
    img = imageGrab(845,750 ,75,150 ,0 ,0)
    if img is None:
        return (None, None)
    img_cv = cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)

    hits = MTM.matchTemplates(
                              template,
                              img_cv,
                              method= cv2.TM_CCOEFF_NORMED,
                              N_object=float("inf"),
                              score_threshold=0.9,
                              maxOverlap=0,
                              searchBox=None)


    if len(hits['TemplateName']) != 1:
        return -1, -1
    else:
        x, y, _, _ =  hits['BBox'].iloc[0]
        print(hits['BBox'].iloc[0])

        x_offset = x - 16
        y_offset = y - 22
        return x_offset, y_offset

def writeConfig():
    x, y = detectOffset()

    if x is None:
        return None

    config = configparser.ConfigParser()
    config['Offset'] = {}
    config['Offset']['x'] = str(x)
    config['Offset']['y'] = str(y)

    with open("../config.ini", 'w') as configfile:
        config.write(configfile)

    configfile.close()

def getConfig():
    config = configparser.ConfigParser()
    config.read("config.ini")
    x = config['Offset'].getint('x')
    y = config['Offset'].getint('y')

    return x, y


writeConfig()