import os
import MTM
import cv2
import numpy

from main import imageGrab
import json

class Underlords:
    def __init__(self):
        super().__init__()
        self.underlordTemplates = self.loadUnderlords()

        self.underlordData = None

        with open('../underlords.json') as f:
            self.underlordData = json.load(f)

        self.underlordData = self.underlordData['set_balance']

        self.prices = {'abbadon': 3,
                       'alchemist': 3,
                       'anti mage': 1,
                       'axe': 5,
                       'bat rider': 1,
                       'beastmaster': 3,
                       'bounty hunter': 1,
                       'bristle back': 2,
                       'chaos knight': 2,
                       'crystal maiden': 1,
                       'dazzle': 1,
                       'death prophet': 4,
                       'doom': 4,
                       'dragon knight': 5,
                       'drow ranger': 1,
                       'earth spirit': 2,
                       'ember spirit': 3,
                       'enchantress': 1,
                       'faceless void': 5,
                       'juggernaut': 2,
                       'keeper of the light': 5,
                       'kunka': 2,
                       'legion commander': 2,
                       'lich': 1,
                       'life stealer': 3,
                       'lina': 4,
                       'lone druid': 4,
                       'luna': 2,
                       'lycan': 3,
                       'magnus': 1,
                       'medusa': 5,
                       'meepo': 2,
                       'mirana': 4,
                       'nature prophet': 2,
                       'omniknight': 3,
                       'pangolier': 4,
                       'phantom assassin': 1,
                       'puck': 3,
                       'pudge': 2,
                       'queen of pain': 2,
                       'rubick': 4,
                       'shadow demon': 1,
                       'shadow shaman': 3,
                       'slardar': 1,
                       'slark': 3,
                       'snap fire': 1,
                       'spectre': 3,
                       'spirit breaker': 2,
                       'storm spirit': 2,
                       'sven': 4,
                       'templar assassin': 4,
                       'terror blade': 3,
                       'tidehunter': 4,
                       'treant protector': 3,
                       'troll warrior': 5,
                       'tusk': 1,
                       'vengeful spirit': 1,
                       'venomancer': 1,
                       'viper': 4,
                       'void spirit': 4,
                       'wind ranger': 2,
                       'wraith king': 5
                       }

    def checkUnderlords(self):
        gameScreen = imageGrab()
        underlords = self.cropUnderlords(gameScreen)
        underlordsList = []
        for underlord in underlords:
            underlordName = self.detectUnderlord(underlord)
            underlordsList.append(underlordName)
            # print("Item: %s" % underlordName)

        #print(underlordsList)

        return underlordsList

    def loadUnderlords(self):
        root = os.path.join(os.path.dirname(os.getcwd()), "underlords")
        templateList = []
       # print(root)
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

