class Hero:
    def __init__(self, name, coords, image, underlord=False, ID=None, gold=-1, melee=False, ranged=False,
                 preventMana=False, localID=-1):
        self.name = name
        self.coords = coords
        self.image = image
        self.tier = 1
        self.item = None
        self.underlord = underlord
        self.id = ID
        self.melee = melee
        self.ranged = ranged
        self.preventMana = preventMana
        self.gold = gold
        self.localID = localID
