import os
import MTM
import cv2
import numpy

from main import imageGrab


class Underlords:
    def __init__(self):
        super().__init__()
        self.underlordTemplates = self.loadUnderlords()

    def checkUnderlords(self):
        gameScreen = imageGrab()
        underlords = self.cropUnderlords(gameScreen)
        underlordsList = []
        for underlord in underlords:
            underlordName = self.detectUnderlord(underlord)
            underlordsList.append(underlordName)
            # print("Item: %s" % underlordName)

        print(underlordsList)

        return underlordsList

    def loadUnderlords(self):
        root = os.path.join(os.path.dirname(os.getcwd()), "underlords")
        templateList = []
        print(root)
        for file in os.listdir(root):
            img = cv2.imread(os.path.join(root, file))
            templatename = file[0:len(file)-4]
            templateList.append((templatename, img))

        return templateList

    def cropUnderlords(self, gameScreen):
        underlordsList = []
        for i in range(4):
            underlord = gameScreen.crop((45 + 274 * i, 535) + (135 + 274 * i, 735))
            underlordsList.append(underlord)
        return underlordsList

    def detectUnderlord(self, img):
        img_cv = cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)

        # Look for matches with over 90% confidence
        # Note MTM converts BGR images to grayscale by taking an avg across 3 channels
        hits = MTM.matchTemplates(self.underlordTemplates,
                                  img_cv,
                                  method=cv2.TM_CCOEFF_NORMED,
                                  N_object=float("inf"),
                                  score_threshold=0.85,
                                  maxOverlap=0,
                                  searchBox=None)

        # print(hits)

        if len(hits['TemplateName']) > 0:
            underlordName = hits['TemplateName'].iloc[0]
            return underlordName

        return None

