import os
import cv2
import torch
from torchvision.transforms import transforms

from Clock_Model import Net

root1 = "C:/Program Files (x86)/Steam/userdata/87849181/760/remote/1046930/screenshots/"
root2 = "D:/Documents/procesing/"
save = "D:/Documents/underlords save/"

files = os.listdir(root1)
createModel()
for file in files:
    file_name = os.path.join(root1,file)
    # print(files)
    img = cv2.imread(file_name)
    # crop = img[10:10+56, 550:550+50]

    cv2.imwrite(os.path.join(save,file), crop)

def createModel(self, n_chans1=35, stride1=1, stride2=1, finalChannel=38):
    net = Net(n_chans1=n_chans1, stride1 = stride1, stride2 = stride2, finalChannel= finalChannel)
    if torch.cuda.is_available():
        net = net.cuda()
        net.load_state_dict(torch.load("digits_model.pth"))
    else:
        net.load_state_dict(torch.load("digits_model.pth", map_location=torch.device('cpu')))
    return net


def predict(self, imageList, net):
    data_transform = transforms.Compose([transforms.ToTensor(),
                                             transforms.Normalize((0.5,), (0.5,), (0.5,)),
                                             ])
    data = []

    for img in imageList:
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