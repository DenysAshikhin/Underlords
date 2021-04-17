import os

import MTM
import cv2
import numpy


class HUD:
    def __init__(self):
        super().__init__()
        # combat Phases > combat, intermission, prepartion
        # selection > item selection, underlord selection
        self.combatPhases, self.selectionPhases = self.loadPhases()

    def loadPhases(self):
        root = "../Game State/"
        templateList = []

        for file in os.listdir(root):
            img = cv2.imread(os.path.join(root, file))
            # print(file)
            templatename = file[0:len(file) - 4]
            templateList.append((templatename, img))

        return templateList

    def detectPhase(self, img):
        # Convert from PIL image type to cv2
        # PIL image store in rgb format, non array
        img_cv = cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)

        # Look for matches with over 90% confidence
        # Note MTM converts BGR images to grayscale by taking an avg across 3 channels
        hits = MTM.matchTemplates(self.loadPhases(),
                                  img_cv,
                                  method=cv2.TM_CCOEFF_NORMED,
                                  N_object=float("inf"),
                                  score_threshold=0.55,
                                  maxOverlap=0,
                                  searchBox=None)

        # print(hits)

        if len(hits['TemplateName']) > 0:
            phase = hits['TemplateName'].iloc[0]
            return phase

        return None