import os
from datetime import datetime
import MTM
import cv2
import numpy
from main import imageGrab


class Items:
    def __init__(self):
        super().__init__()
        # self.heroTemplates = self.load("hero")
        self.itemTemplates = self.loadTemplates("items")

    def checkItems(self):
        gameScreen = imageGrab()
        items = self.cropItems(gameScreen)
        for item in items:
            print("Item: %s" % self.detectItem(item, self.itemTemplates))

    def loadTemplates(self, templateName):
        root = os.path.join(os.path.dirname(os.getcwd()), "items-heroes", templateName)
        templateList = []
        print(root)
        for file in os.listdir(root):
            img = cv2.imread(os.path.join(root,file))
            templateList.append((file, img))

        return templateList

    def cropItems(self, gameScreen):
        item1 = (gameScreen.crop((315, 350) + (390, 480)))
        item2 = gameScreen.crop((540, 350) + (615, 480))
        item3 = gameScreen.crop((765, 350) + (840, 480))
        return [item1, item2, item3]

    def detectItem(self, img, templates):
        # Convert from PIL image type to cv2
        # PIL image store in rgb format, non array
        img_cv = cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)

        # Look for matches with over 90% confidence
        # Note MTM converts BGR images to grayscale by taking an avg across 3 channels
        hits = MTM.matchTemplates(templates,
                                  img_cv,
                                  method=cv2.TM_CCOEFF_NORMED,
                                  N_object=float("inf"),
                                  score_threshold=0.85,
                                  maxOverlap=0,
                                  searchBox=None)

        print(hits)

        if len(hits['TemplateName']) == 1:
            itemName = hits['TemplateName'].iloc[0]
        else:
            return None

        return itemName
