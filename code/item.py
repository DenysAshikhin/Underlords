class Item:
    def __init__(self, name, coords, image= None, ID = None):

        self.name = name
        self.coords = coords
        self.image = image #maybe at somepoint in the future - not now tho >.>
        self.hero = None
        self.ID = ID