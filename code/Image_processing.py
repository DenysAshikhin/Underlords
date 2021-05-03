import os
import time
from datetime import datetime

import cv2
import torch
from torchvision.transforms import transforms
from PIL import Image

from Clock_Model import Net
from HUD import HUD
from main import imageGrab

root1 = "C:/Program Files (x86)/Steam/userdata/87849181/760/remote/1046930/screenshots/"
root2 = "D:/Documents/processing/"
root3 = "D:/Documents/x/"
save = "D:/Documents/underlords save/"



def createModel( n_chans1=35, stride1=1, stride2=1, finalChannel=38):
    net = Net(n_chans1=n_chans1, stride1 = stride1, stride2 = stride2, finalChannel= finalChannel)
    if torch.cuda.is_available():
        net = net.cuda()
        net.load_state_dict(torch.load("digits_model.pth"))
    else:
        net.load_state_dict(torch.load("digits_model.pth", map_location=torch.device('cpu')))
    return net


def predict(img, net):
    data_transform = transforms.Compose([transforms.ToTensor(),
                                             transforms.Normalize((0.5,), (0.5,), (0.5,)),
                                             ])
    data = []


    data.append(data_transform(img))

    out = torch.stack(data, dim=0)  # output all images as one tensor
    m = torch.nn.Softmax(dim=1)
    # Perform forward pass with ANN

    if torch.cuda.is_available():
        out = out.cuda()

    out = net(out)  # use model to evaluate
    out = m(out)  # apply softmax
    value, inspect = torch.max(out, 1)
    return value, inspect

hud = HUD()
start = time.time()

hud.getClockTimeLeft()
end = time.time()

elapsed = end - start
print(elapsed)

net = createModel()
classes = os.listdir(root2)
start = time.time()
imgs = imageGrab()
img = imgs.crop((550,10) + (600, 66))
# img.show()

value, inspect = predict(img=img, net=net)
end = time.time()

# while(True):
#     start = time.time()
#     img = imageGrab()
#     img = img.crop(550, 10, 550 + 50, 10 + 56)
#
#     value, inspect = predict(img=img, net=net)
#     end = time.time()
#     for i, imgs in enumerate(inspect):
#         state = imgs.item()
#
#         img.save(os.path.join(root2, str(classes[state]), str(datetime.now()).replace(":", "")) + ".jpg")
#
#         time.sleep(1)

elapsed = end - start
print(elapsed)


# files = os.listdir(root3)
# print(classes)
# for file in files:
#     file_name = os.path.join(root3,file)
#     if not os.path.isdir(file_name):
#         img = Image.open(file_name)
#         value, inspect = predict(img=img, net=net)
#         for i, imgs in enumerate(inspect):
#             state = imgs.item()
#             print(os.path.join(root2,str(classes[state]),file))
#             img.save(os.path.join(root2,str(classes[state]),file))
    # crop = img[10:10+56, 550:550+50]

    # cv2.imwrite(os.path.join(save,file),)

