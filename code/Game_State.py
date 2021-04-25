import os

import MTM
import cv2
import numpy
from main import imageGrab


class state:
    def __init__(self):
        super().__init__()
        # combat Phases > combat, intermission, prepartion
        # selection > item selection, underlord selection
        self.combatTemplates = self.loadTemplates("../Header Texts/Combat State/")
        self.selectionTemplates = self.loadTemplates("../Header Texts/Selection State/")
        self.placeTemplates = self.loadTemplates("../Header Texts/Place State/")
        self.currentPhase = None

    def getPhase(self):
        gameScreen = imageGrab()

        combatCrop = gameScreen.crop((480, 35) + (600, 60))
        selectionCrop = gameScreen.crop((240, 235) + (580, 340))

        combatPhase = self.detectPhase(combatCrop, self.combatTemplates)
        selectionPhase = self.detectPhase(selectionCrop, self.selectionTemplates)


        if selectionPhase is not None:
            self.currentPhase = selectionPhase
        elif combatPhase is not None:
            self.currentPhase = combatPhase

        return self.currentPhase

    def loadTemplates(self, root):
        templates = []

        for file in os.listdir(root):
            img = cv2.imread(os.path.join(root, file))
            templatename = file[0:len(file) - 4]
            templates.append((templatename, img))

        return templates

    def detectGameEnd (self):
        gameScreen = imageGrab()
        placeCrop = gameScreen.crop((155, 300) + (350, 420))

        placePhase = self.detectPhase(placeCrop, self.placeTemplates)
        if placePhase is not None:
            return placePhase

        return -1



    def detectPhase(self, img, template):
        # Convert from PIL image type to cv2
        # PIL image store in rgb format, non array
        img_cv = cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)

        # Look for matches with over 90% confidence
        # Note MTM converts BGR images to grayscale by taking an avg across 3 channels
        hits = MTM.matchTemplates(template,
                                  img_cv,
                                  method=cv2.TM_CCOEFF_NORMED,
                                  N_object=float("inf"),
                                  score_threshold=0.7,
                                  maxOverlap=0,
                                  searchBox=None)

        # print(hits)

        if len(hits['TemplateName']) > 0:
            phase = hits['TemplateName'].iloc[0]
            # print(phase)
            return phase

        return None
