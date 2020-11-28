import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from PIL import Image
from torch.utils.data.sampler import SubsetRandomSampler
from torch.utils.tensorboard import SummaryWriter


def loadData(batchSize):
    dataTransform = transforms.Compose([transforms.ToTensor(),
                                        transforms.Normalize((0.5,), (0.5,), (0.5,)),
                                        ])
    # duplicate data for fails, and add noise/change contrast/add blur/change brightness/scale image/ translation
    randomTransform = transforms.Compose([transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.5),
                                          transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,), (0.5,))])
    transformSet = [dataTransform, randomTransform]

    def listdirs(path):
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    root =  "C:/Users/destr/PycharmProjects/Underlords/Pics"
    classes = listdirs(root)
    print(classes)

    sets = []
    for transform in transformSet:
        set_iter = datasets.ImageFolder(root=root, transform=transform)
        sets.append(set_iter)
    trainSet = torch.utils.data.ConcatDataset(sets)

    # Get the list of indices to sample from
    relevantIndices = list(range(0, len(trainSet)))

    # Split into train and validation
    np.random.seed(1)  # Fixed numpy random seed for reproducible shuffling
    np.random.shuffle(relevantIndices)
    split1 = int(len(relevantIndices) * 0.85)  # split at 85%
    split2 = int(len(relevantIndices) * 0.95)  # split at 95%

    # split into training and validation indices
    training, validation = relevantIndices[:split1], relevantIndices[split1:split2]

    trainingSampler = SubsetRandomSampler(training)

    trainingLoader = torch.utils.data.DataLoader(trainSet, batch_size=batchSize, num_workers=0, sampler=trainingSampler)
    validationSampler = SubsetRandomSampler(validation)

    validationLoader = torch.utils.data.DataLoader(trainSet, batch_size=batchSize, num_workers=0,
                                                   sampler=validationSampler)
    return trainingLoader, validationLoader, classes


class Net(nn.Module):
    def __init__(self, n_chans1=32):
        super().__init__()
        self.n_chans1 = n_chans1
        self.conv1 = nn.Conv2d(3, n_chans1, kernel_size=3, padding=1)
        self.conv1_batchnorm = nn.BatchNorm2d(num_features=n_chans1)
        self.conv2 = nn.Conv2d(n_chans1, n_chans1 // 2, kernel_size=3,
                               padding=1)
        self.conv2_batchnorm = nn.BatchNorm2d(num_features=n_chans1 // 2)
        self.fc1 = nn.Linear(31 * 23 * n_chans1 // 2, 32)
        self.fc2 = nn.Linear(32, 62)

    def forward(self, x):
        out = self.conv1_batchnorm(self.conv1(x))
        out = F.max_pool2d(torch.relu(out), 2)
        out = self.conv2_batchnorm(self.conv2(out))
        out = F.max_pool2d(torch.relu(out), 2)
        out = out.view(-1, 31 * 23 * self.n_chans1  // 2)
        out = torch.relu(self.fc1(out))
        out = self.fc2(out)
        return out

def calculateF1():
    print()

def training_loop(num_epochs, optimizer, model, criterion, train_loader, valid_loader,writer):
    train_losses = []
    valid_losses = []
    training_accuracy = []
    validation_accuracy = []
    device = (torch.device('cuda') if torch.cuda.is_available()
              else torch.device('cpu'))
    print(f"Training on device {device}.")

    for epoch in range(1, num_epochs + 1):
        train_loss = 0.0
        valid_loss = 0.0

        model.train()
        for imgs, labels in train_loader:
            # move-tensors-to-GPU
            imgs = imgs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            output = model(imgs)
            loss = criterion(output, labels)
            loss.backward()
            # perform-a-ingle-optimization-step (parameter-update)
            optimizer.step()
            # update-training-loss
            train_loss += loss.item() * imgs.size(0)
            prediction = output.max(1, keepdim=True)[1]
            correct = prediction.eq(labels.view_as(prediction)).sum().item()
            total = imgs.shape[0]
            training_accuracy.append((correct / total))
            writer.add_scalar("Loss/train", train_loss, epoch)
            writer.add_scalar("Accuracy/train", correct/total, epoch)
            ##########################

            # save the current training information
        # validate-the-model
        model.eval()
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
            validation_accuracy.append((correct/total))

            writer.add_scalar("Loss/val", valid_loss, epoch)
            writer.add_scalar("Accuracy/Val", correct/total, epoch)

        # calculate-average-losses
        train_loss = train_loss / len(train_loader.sampler)
        valid_loss = valid_loss / len(valid_loader.sampler)
        train_losses.append(train_loss)
        valid_losses.append(valid_loss)

        epoch_train_accuracy = sum(training_accuracy) / len(training_accuracy)
        epoch_validation_accuracy = sum(validation_accuracy) / len(validation_accuracy)

        # print-training/validation-statistics
        print('Epoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f}  \tTraining Accuracy: {:.6f}  \tValidation Accuracy: {:.6f}'.format(
            epoch, train_loss, valid_loss,epoch_train_accuracy,epoch_validation_accuracy))
    torch.save(model.state_dict(), "model.pth")
    writer.close()

def train():
    model = Net()
    model = model.cuda()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-2, momentum=0.9)
    writer = SummaryWriter()
    trainingLoader, validationLoader, classes = loadData(16)
    training_loop(10,optimizer,model,criterion,trainingLoader,validationLoader,writer)


#train()


