import os
from datetime import datetime
import cv2
import MTM
from main import imageGrab
import numpy


def cropGold(gameScreen):
    # draw = ImageDraw.Draw(gameScreen)
    imageList = []
    tensDigit = gameScreen.crop((920, 52) + (933, 67))
    onesDigit = gameScreen.crop((930, 52) + (943, 67))
    singeDigit = gameScreen.crop((925, 52) + (942, 67))

    imageList.append(singeDigit)
    imageList.append(tensDigit)
    imageList.append(onesDigit)
    return imageList


def loadDigits():
    root = os.path.join(os.path.dirname(os.getcwd()),"digits")
    digitsList = []
    for i in range(10):
        # print(os.path.join(root,str(i) + ".jpg"))
        img = cv2.imread(os.path.join(root,str(i) + ".jpg"))
        cv2.imwrite("tes.jpg",img)
        digitsList.append((str(i), img))
    return digitsList


def countGold(imageList):
    templates = loadDigits()
    # Convert from PIL image type to cv2
    # PIL image store in rgb format, non array
    singleDigit = cv2.cvtColor(numpy.asarray(imageList[0]), cv2.COLOR_RGB2BGR)
    tensDigit = cv2.cvtColor(numpy.asarray(imageList[1]), cv2.COLOR_RGB2BGR)
    onesDigit = cv2.cvtColor(numpy.asarray(imageList[2]), cv2.COLOR_RGB2BGR)

    templates = loadDigits()

    maxScoreTens = 0
    maxScoreOnes = 0
    digitNameTens = -1
    digitNameOnes = -1

    hitsTens = MTM.matchTemplates(templates,
                                  tensDigit,
                                  method=cv2.TM_CCOEFF_NORMED,
                                  N_object=1,
                                  score_threshold=0.5,
                                  maxOverlap=0,
                                  searchBox=None)
    print(hitsTens)


    hitsOnes = MTM.matchTemplates(templates,
                                  onesDigit,
                                  method=cv2.TM_CCOEFF_NORMED,
                                  N_object=1,
                                  score_threshold=0.5,
                                  maxOverlap=0,
                                  searchBox=None)

    print(hitsOnes)

    for index, row in hitsTens.iterrows():
        if row['Score'] > maxScoreTens:
            print("Digit %s" % row['TemplateName'], "Score %f" % row['Score'])
            maxScoreTens = row['Score']
            digitNameTens = int(row['TemplateName'])

    for index, row in hitsOnes.iterrows():
        if row['Score'] > maxScoreOnes:
            print("Digit %s" % row['TemplateName'], "Score %f" % row['Score'])
            maxScoreOnes = row['Score']
            digitNameOnes = int(row['TemplateName'])

    if maxScoreTens >= 0.9 and maxScoreOnes >= 0.9:
        gold = 10 * digitNameTens + digitNameOnes
        return gold

    hits = MTM.matchTemplates(templates,
                              singleDigit,
                              method=cv2.TM_CCOEFF_NORMED,
                              N_object=1,
                              score_threshold=0.80,
                              maxOverlap=0,
                              searchBox=None)

    maxScoreSingle = 0
    digitNameSingle = -1

    print(hits)
    for index, row in hits.iterrows():
        if row['Score'] > maxScoreSingle:
            print("Digit %s" % row['TemplateName'], "Score %f" % row['Score'])
            maxScoreSingle = row['Score']
            digitNameSingle = int(row['TemplateName'])

    gold = digitNameSingle

    return gold


print("Gold %d" % countGold(cropGold(imageGrab())))
