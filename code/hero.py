class Hero:
    def __init__(self, name, coords, image, underlord=False, ID = None):

        self.name = name
        self.coords = coords
        self.image = image
        self.tier = 1
        self.item = None
        self.underlord = underlord
        self.id = ID

