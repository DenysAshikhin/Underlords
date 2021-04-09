import os
from datetime import datetime
import MTM
import cv2
import numpy
from main import imageGrab


class Items:
    def __init__(self):
        super().__init__()
        self.itemTemplates = self.loadItems()
        #print(self.itemTemplates)

    def checkItems(self):
        gameScreen = imageGrab()
        items = self.cropItems(gameScreen)
        itemList = []
        for item in items:
            itemName = self.detectItem(item)
            itemList.append(itemName)
           # print("Item: %s" % itemName)

        return itemList

    def loadItems(self):
        root = os.path.join(os.path.dirname(os.getcwd()), "items")
        templateList = []
      #  print(root)
        for file in os.listdir(root):
            img = cv2.imread(os.path.join(root, file))
            print(file)
            templatename = file[0:len(file) - 4]
            templateList.append((templatename, img))

        return templateList

    def cropItems(self, gameScreen):
        item1 = (gameScreen.crop((315, 340) + (390, 480)))
        #item1.show()
        item2 = gameScreen.crop((540, 340) + (615, 480))
        item3 = gameScreen.crop((765, 340) + (840, 480))
        return [item1, item2, item3]

    def detectItem(self, img):
        # Convert from PIL image type to cv2
        # PIL image store in rgb format, non array
        img_cv = cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)

        # Look for matches with over 90% confidence
        # Note MTM converts BGR images to grayscale by taking an avg across 3 channels
        hits = MTM.matchTemplates(self.itemTemplates,
                                  img_cv,
                                  method=cv2.TM_CCOEFF_NORMED,
                                  N_object=float("inf"),
                                  score_threshold=0.1,
                                  maxOverlap=0,
                                  searchBox=None)

        print(hits)

        if len(hits['TemplateName']) > 0:
            itemName = hits['TemplateName'].iloc[0]
            return itemName

        return None
