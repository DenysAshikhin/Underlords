import os
import cv2
import MTM
from main import imageGrab
import numpy


class HUD:
    def __init__(self):
        super().__init__()
        self.gold = 0
        self.health = 0
        self.units = 3
        self.goldTemplates = self.loadDigits("gold")
        self.healthTemplates = self.loadDigits("health")
        self.unitTemplates = self.loadDigits("unit")
        self.expTemplates = self.loadDigits("exp")
        self.expSlash = [("Slash", cv2.imread("../digits/exp_slash.jpg"))]
        self.currExp = 0
        self.poolExp = 0
        self.hero = False

    def getHUD(self):
        # Capture screen once, and crop it as needed
        gameScreen = imageGrab()
        self.gold = self.countHUD(self.cropGold(gameScreen), self.goldTemplates)
        self.health = self.countHUD(self.cropHealth(gameScreen), self.healthTemplates)
        self.units = self.countHUD(self.cropUnit(gameScreen), self.unitTemplates)
        self.currExp, self.poolExp = self.countEXP(self.cropEXP(gameScreen))
        allImage = self.cropHUD(gameScreen)

        return [self.gold, self.health, self.units, self.currExp, self.poolExp], allImage

    def cropHealth(self, gameScreen):
        crop = gameScreen.crop((1010, 810) + (1100, 870))
        return crop

    def cropUnit(self, gameScreen):
        crop = gameScreen.crop((925, 810) + (985, 875))
        return crop

    def cropGold(self, gameScreen):
        crop = gameScreen.crop((920, 40) + (943, 75))
        return crop

    def cropHUD(self, gameScreen):
        crop = gameScreen.crop((920, 815) + (1100, 975))
        return crop

    def cropEXP(self, gameScreen):
        crop = gameScreen.crop((875, 235) + (935, 275))
        return crop

    def countEXP(self, img):
        # Convert img from PIL to numpy
        img_cv = cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)

        # xp in underlords has the following format ##/##
        # we find the position of / to distinguish curr and pool xp
        slashdf = MTM.matchTemplates(self.expSlash,
                                     img_cv,
                                     method=cv2.TM_CCOEFF_NORMED,
                                     N_object=float("inf"),
                                     score_threshold=0.9,
                                     maxOverlap=0,
                                     searchBox=None)

        # 1 = shop open , xp visible, any other cases are errors
        if len(slashdf) == 1:
            hits = MTM.matchTemplates(self.expTemplates,
                                      img_cv,
                                      method=cv2.TM_CCOEFF_NORMED,
                                      N_object=float("inf"),
                                      score_threshold=0.9,
                                      maxOverlap=0,
                                      searchBox=None)

            slashX, _, _, _ = slashdf['BBox'].iloc[0]

            currExpArr = []
            poolExpArr = []

            # Construct two ordered  lists to keep track of the digits found
            for index, row in hits.iterrows():
                digitX, _, _, _ = row['BBox']
                if digitX < slashX:
                    insertPos = binarySearch(currExpArr, digitX)
                    if insertPos < 0:
                        insertPos = -insertPos - 1
                    currExpArr.insert(insertPos, (digitX, row['TemplateName']))
                else:
                    insertPos = binarySearch(poolExpArr, digitX)
                    if insertPos < 0:
                        insertPos = -insertPos - 1
                    poolExpArr.insert(insertPos, (digitX, row['TemplateName']))

            currExp = 0
            poolExp = 0
            placeFactor = 1

            # binary search is set up currently to sort smallest to highest
            # the digit with the smallest x position is a higher value
            # we reverse the list to account for this and start at ones column
            for digit in reversed(currExpArr):
                currExp = placeFactor * int(digit[1]) + currExp
                placeFactor *= 10

            placeFactor = 1
            for digit in reversed(poolExpArr):
                poolExp = placeFactor * int(digit[1]) + poolExp
                placeFactor *= 10

            return currExp, poolExp
        else:
            return -1, -1

    # Given a cropped image, and a set of templates containing digits
    # count the current number present and return it
    # gold = gold count
    # health = current health, etc
    def countHUD(self, img, templates):
        # Convert from PIL image type to cv2
        # PIL image store in rgb format, non array
        img_cv = cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)

        # Look for matches with over 90% confidence
        # Note MTM converts BGR images to grayscale by taking an avg across 3 channels
        hits = MTM.matchTemplates(templates,
                                  img_cv,
                                  method=cv2.TM_CCOEFF_NORMED,
                                  N_object=float("inf"),
                                  score_threshold=0.9,
                                  maxOverlap=0,
                                  searchBox=None)

        # print(hits)

        if len(hits['TemplateName']) == 1:
            # If only one match is found, single digit is present
            itemCount = int(hits['TemplateName'].iloc[0])
        elif len(hits['TemplateName']) == 0:
            itemCount = -1
        else:
            # For two matches, look at their location in the image
            # to determine the tens and ones digit
            x1, _, _, _ = hits['BBox'].iloc[0]
            x2, _, _, _ = hits['BBox'].iloc[1]

            if x1 <= x2:
                tensDigit = int(hits['TemplateName'].iloc[0])
                onesDigit = int(hits['TemplateName'].iloc[1])
            else:
                tensDigit = int(hits['TemplateName'].iloc[1])
                onesDigit = int(hits['TemplateName'].iloc[0])

            itemCount = tensDigit * 10 + onesDigit
        return itemCount

    # Load a templates of images in the format specified by MTM
    # itemName redirects to the sub folder to search templates for
    def loadDigits(self, itemName):
        root = os.path.join(os.path.dirname(os.getcwd()), "digits", itemName)
        digitsList = []
        print(root)
        for i in range(len(os.listdir(root)) + 1):
            if os.path.isfile(os.path.join(root, str(i) + ".jpg")):
                img = cv2.imread(os.path.join(root, str(i) + ".jpg"))
                digitsList.append((str(i), img))
        return digitsList

def binarySearch(arr, value):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid][0] < value:
            low = mid + 1
        elif arr[mid][0] > value:
            high = mid - 1
        else:
            return mid
    return -(low + 1)
