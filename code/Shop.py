from datetime import datetime
import os
import torch
import torch.nn as nn
from PIL import Image
from torchvision.transforms import transforms

import Model
from main import imageGrab


class Shop:
    def __init__(self):
        super().__init__()
        self.classes = self.getClasses()
        self.model = self.createModel()

    def createModel(self):
        net = Model.Net(n_chans1=7, stride1=1, stride2=1, finalChannel=47)
        if torch.cuda.is_available():
            net = net.cuda()
            net.load_state_dict(torch.load("model.pth"))
        else:
            net.load_state_dict(torch.load("model.pth", map_location=torch.device('cpu')))
        return net

    def getClasses(self):
        def listdirs(path):
            return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

        class_path = "../Pics"
        if torch.cuda.is_available():
            class_path = "../Pics"

        classes = listdirs(class_path)
        return classes

    def labelShop(self):
        imageList = self.cropShop(imageGrab(), save=False)
        value, inspect = self.predict(imageList)
        classes = self.getClasses()
        statesList = []

        for i, img in enumerate(inspect):
            state = img.item()
            statesList.append(state)
            # print("Position %d:" % i, "Label: %s" % classes[state], "Confidence: %f" % value[i])

        return imageList, classes, value, inspect, statesList

    def cropShop(self, gameScreen, save=True):
        # shop = Image.open("test.jpg")
        # draw = ImageDraw.Draw(gameScreen)
        offset = 120
        imageList = []
        for i in range(5):
            # draw.rectangle((300, 90) + (400, 195))
            crop = gameScreen.crop((294 + i * offset, 70) + (388 + i * offset, 195))
            # draw.rectangle((294 + i*offset, 70) + (388 + i*offset, 195))

            imageList.append(crop)
            if save:
                crop.save("../WIP/" + str(datetime.now()).replace(":", "") + ".jpg")
        return imageList

    # Given a list of images, run a forward pass with CNN and return predictions
    def predict(self, imageList):
        data_transform = transforms.Compose([transforms.ToTensor(),
                                             transforms.Normalize((0.5,), (0.5,), (0.5,)),
                                             ])
        data = []

        for img in imageList:
            data.append(data_transform(img))

        out = torch.stack(data, dim=0)  # output all images as one tensor
        m = nn.Softmax(dim=1)
        # Perform forward pass with ANN

        if torch.cuda.is_available():
            out = out.cuda()

        out = self.model(out)  # use model to evaluate
        out = m(out)  # apply softmax
        value, inspect = torch.max(out, 1)
        return value, inspect

    def loadOne(self):
        image_root = "../WIP"
        image_list = []

        for file in os.listdir(image_root):
            image_list.append(Image.open(image_root + "/" + file))

        save_path = "../save/"
        cnt = 0
        value, inspect = self.predict(image_list)
        classes = self.getClasses()

        for i, img in enumerate(inspect):
            state = img.item()
            folder_name = classes[state]
            image_list[cnt].save(save_path + folder_name + "/" + str(datetime.now()).replace(":", "") + ".jpg")
            cnt += 1
        return True

