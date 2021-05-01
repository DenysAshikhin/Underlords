import math
import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from ray.tune.suggest.bohb import TuneBOHB
from torch.utils.data.sampler import SubsetRandomSampler
from torch.utils.tensorboard import SummaryWriter

import ray

from ray import tune
from ray.tune.schedulers import ASHAScheduler, HyperBandForBOHB


def loadData(batchSize):
    batchSize = int(batchSize)
    dataTransform = transforms.Compose([transforms.ToTensor(),
                                        transforms.Normalize((0.5,), (0.5,), (0.5,)),
                                        ])
    # duplicate data for fails, and add noise/change contrast/add blur/change brightness/scale image/ translation
    randomTransform = transforms.Compose([transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.5),
                                          transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,), (0.5,))])
    transformSet = [dataTransform, randomTransform]

    def listdirs(path):
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    lastSlash = int(os.path.dirname(os.path.realpath(__file__)).rindex('\\'))

    # print(lastSlash)
    root = "D:/Documents/underlords save"

    # print(root)
    classes = listdirs(root)
    print(classes)

    sets = []
    for transform in transformSet:
        set_iter = datasets.ImageFolder(root=root, transform=transform)
        sets.append(set_iter)
    trainSet = torch.utils.data.ConcatDataset(sets)

    relevantIndices = list(range(0, len(trainSet)))
    split1 = int(len(relevantIndices) * 0.7)  # split at 85%
    split2 = int(len(relevantIndices) * 0.3)  # split at 95%

    train_set, val_set = torch.utils.data.random_split(trainSet, [split1+1, split2])

    # split into training and validation indices


    # training, validation = relevantIndices[:split1], relevantIndices[split2:]
    # trainingSampler = SubsetRandomSampler(training)
    trainingLoader = torch.utils.data.DataLoader(train_set, batch_size=batchSize, num_workers=0,  shuffle= True)

    # validationSampler = SubsetRandomSampler(validation)
    validationLoader = torch.utils.data.DataLoader(val_set, batch_size=batchSize, num_workers=0,
                                                   shuffle= True)
    return trainingLoader, validationLoader, classes


class Net(nn.Module):
    def __init__(self, n_chans1=32, stride1=1, stride2=1, finalChannel=32):
        super().__init__()
        print(n_chans1)
        n_chans1 = int(n_chans1)
        stride1 = int(stride1)
        stride2 = int(stride2)
        finalChannel = int(finalChannel)

        def poolAdjust(originalSize, kernel=3, stride=2, dilation=1):
            return (math.ceil((originalSize - (dilation * (kernel - 1)) - 1) / stride)) + 1

        def conv2d_size_out(size, kernel_size=3, stride=1, padding=0):
            return math.ceil((size + (padding * 2) - (kernel_size - 1) - 1) // stride) + 1

        self.n_chans1 = n_chans1
        finalOutput = n_chans1 // 2
        self.conv1 = nn.Conv2d(3, n_chans1, kernel_size=3, stride=stride1, padding=1)
        self.conv1_batchnorm = nn.BatchNorm2d(num_features=n_chans1)
        self.conv2 = nn.Conv2d(n_chans1, finalOutput, kernel_size=3, stride=stride2,
                               padding=1)
        self.conv2_batchnorm = nn.BatchNorm2d(num_features=finalOutput)

        # print(f"We want Width: {31 * 23 * finalOutput}")

        # 94 * 125
        # width = 94
        # height = 125

        # print(f"step1 {conv2d_size_out(94, padding=1, stride=stride1)}") print(f"step2 {poolAdjust(conv2d_size_out(
        # 94, padding=1, stride=stride1))}") print( f"step3 {conv2d_size_out(poolAdjust(conv2d_size_out(94,
        # padding=1, stride=stride1)), padding=1, stride=stride2)}") print( f"step4 {poolAdjust(conv2d_size_out(
        # poolAdjust(conv2d_size_out(94, padding=1, stride=stride1)), padding=1, stride=stride2))}")

        widthFinal = poolAdjust(
            conv2d_size_out(poolAdjust(conv2d_size_out(50, padding=1, stride=stride1)), padding=1, stride=stride2)
        )
        heightFinal = poolAdjust(
            conv2d_size_out(poolAdjust(conv2d_size_out(56, padding=1, stride=stride1)), padding=1, stride=stride2)
        )
        # print(
        #     f"We got Width: {widthFinal}")
        # print(
        #     f"We got Height: {heightFinal}")

        self.finalSize = widthFinal * heightFinal * finalOutput

        # print(f"Final: {self.finalSize}")

        self.fc1 = nn.Linear(self.finalSize, finalChannel)
        self.fc2 = nn.Linear(finalChannel, 29)

    def forward(self, x):
        out = self.conv1_batchnorm(self.conv1(x))
        # print(f"conv1: {out.size()}")
        out = F.max_pool2d(torch.relu(out), 2)
        # print(f"first pool: {out.size()}")
        out = self.conv2_batchnorm(self.conv2(out))
        # print(f"pre pool {out.size()}")
        out = F.max_pool2d(torch.relu(out), 2)
        # print(f"post pool {out.size()}")
        out = out.view(-1, self.finalSize)
        # print(f"post view: {out.size}")
        # print(f"finalSize: {self.finalSize}")
        out = torch.relu(self.fc1(out))
        out = self.fc2(out)
        return out

def training_loop(num_epochs, optimizer, model, criterion, train_loader, valid_loader, writer):
    train_losses = []
    valid_losses = []
    training_accuracy = []
    validation_accuracy = []
    device = torch.device('cpu')
    # print(f"Training on device {device}.")

    # for epoch in range(1, num_epochs + 1):
    train_loss = 0.0
    valid_loss = 0.0

    model.train()  # turning model back to training (needed after .eval() call

    limit = 50
    i = 0
    for imgs, labels in train_loader:
        i += 1

        if limit == i:
            break
        # if i % (limit / 10) == 0:
        # print(f"Mini Step: {i}")
        # move-tensors-to-GPU
        imgs = imgs.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        output = model(imgs)
        # print(f"lables: {labels} || {labels.size()}")
        #
        # print(f"output: {output}")

        loss = criterion(output, labels)
        loss.backward()
        # perform-a-ingle-optimization-step (parameter-update)
        optimizer.step()
        # update-training-loss
        train_loss += loss.item() * imgs.size(0)

        prediction = output.max(1, keepdim=True)[1]
        # print(f"pred: {prediction}")
        # print(f"viewAS: {labels.view_as(prediction)}")
        #
        # print(f"eq: {prediction.eq(labels.view_as(prediction))}")
        # print(f"eq: {prediction.eq(labels.view_as(prediction)).sum().item()}")
        #
        # print('---------------------------')

        correct = prediction.eq(labels.view_as(prediction)).sum().item()

        total = imgs.shape[0]
        training_accuracy.append((correct / total))
        # writer.add_scalar("Loss/train", train_loss, epoch)
        # writer.add_scalar("Accuracy/train", correct / total, epoch)
        writer.add_scalar("Loss/train", train_loss, num_epochs)
        writer.add_scalar("Accuracy/train", correct / total, num_epochs)
        ##########################

        # save the current training information
    # validate-the-model
    model.eval()  # turn off specific layer/parts of the model for validation
    total = 0
    correct = 0

    # print("Training Accuracy: " + str(sum(epoch_test_correct) / len(epoch_test_correct)))

    for imgs, labels in valid_loader:
        imgs = imgs.to(device)
        labels = labels.to(device)
        output = model(imgs)

        loss = criterion(output, labels)

        # update-average-validation-loss
        valid_loss += loss.item() * imgs.size(0)
        prediction = output.max(1, keepdim=True)[1]
        total += imgs.shape[0]
        correct += prediction.eq(labels.view_as(prediction)).sum().item()
        validation_accuracy.append((correct / total))

        # writer.add_scalar("Loss/val", valid_loss, epoch)
        # writer.add_scalar("Accuracy/Val", correct / total, epoch)
        writer.add_scalar("Loss/val", valid_loss, num_epochs)
        writer.add_scalar("Accuracy/Val", correct / total, num_epochs)

    # calculate-average-losses
    train_loss = train_loss / len(train_loader.sampler)
    valid_loss = valid_loss / len(valid_loader.sampler)
    train_losses.append(train_loss)
    valid_losses.append(valid_loss)

    epoch_train_accuracy = sum(training_accuracy) / len(training_accuracy)
    epoch_validation_accuracy = sum(validation_accuracy) / len(validation_accuracy)

    # print-training/validation-statistics
    print(
        'Epoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f}  \tTraining Accuracy: {:.6f}  \tValidation '
        'Accuracy: {:.6f}'.format(
            num_epochs, train_loss, valid_loss, epoch_train_accuracy, epoch_validation_accuracy))

    writer.close()
    return epoch_validation_accuracy, model



def train(config):
    model = Net(n_chans1=config['finalOutput'], stride1=config['stride1'], stride2=config['stride2'],
                finalChannel=config['finalChannel'])

    # model.cuda()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=config['lr'], momentum=0.9)
    writer = SummaryWriter()
    trainingLoader, validationLoader, classes = loadData(config['batchSize'])

    # print(classStats)
    classStats = []

    # print(f"The epoch! {config['epochs']}")
    for i in range(8):
        accuracy, modelB= training_loop(i, optimizer, model, criterion, trainingLoader,
                                                         validationLoader, writer)

        # tune.report(score=accuracy)
        tune.report(mean_loss=accuracy)
    torch.save(model.state_dict(), "digits_model.pth")
    # cpu_model = model.to('cpu')
    # torch.save(model.state_dict(), "model_CPU.pth")


def tunerTrain():
    ray.init(_memory=4000000000, num_cpus=5)
    searchSpace = {
        'lr': tune.loguniform(1e-4, 9e-1),
        'finalOutput': tune.uniform(2, 50),  # minimum of 2, other 1//2 = 0 activation maps
        'stride1': tune.uniform(1,4),
        'stride2': tune.uniform(1,4),
        'batchSize': tune.uniform(2, 32),
        'finalChannel': tune.uniform(1, 50),
    }

    # analysis = tune.run(train, num_samples=1, scheduler=ASHAScheduler(metric='score', mode='max'),
    #                     config=searchSpace)



    algo = TuneBOHB(max_concurrent=4, metric="mean_loss", mode="max")
    bohb = HyperBandForBOHB(
        metric="mean_loss",
        mode="max",
        )
    analysis = tune.run(train, config=searchSpace, scheduler=bohb, search_alg=algo, num_samples= 100)
    # bayesopt = BayesOptSearch( metric="mean_loss", mode="max", random_search_steps = 3)

    # tune.run(train, search_alg=bayesopt, config= searchSpace, scheduler=ASHAScheduler("mean_loss","max"))
    print("Best config: ", analysis.get_best_config(metric="mean_loss", mode="max"))
    # df = analysis.results_df


#train()
#tunerTrain()
#
#
# train({'lr': 0.0133266,
#         'finalOutput': 35,
#          'stride1': 1,
#          'stride2': 1,
#          'batchSize': 28,
#          'finalChannel': 38
#          })
