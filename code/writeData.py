import csv
import pandas as pd

currentGame = 'currentGame.csv'
allGames = 'allGames.csv'
fieldnames = ['economy', 'roundsSurvived', 'finalPosition', 'unitLevelUp',
              'mainLevelUp', 'wins', 'losses', 'lockIn', 'itemPick', 'counter', 'average']


def resetCurrentGame():
    with open(currentGame, 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()


def writeCurrentGameToCSV(counter, rewards):
    with open(currentGame, 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        economy = rewards['economy']
        roundSurvived = rewards['roundsSurvived']
        finalPosition = rewards['finalPosition']
        unitLevelUp = rewards['unitLevelUp']
        mainLevelUp = rewards['mainLevelUp']
        wins = rewards['wins']
        lockIn = rewards['lockIn']
        itemPick = rewards['itemPick']
        losses = rewards['losses']
        rewards['average'] = economy + roundSurvived + finalPosition + unitLevelUp + mainLevelUp + wins + losses + lockIn + itemPick
        rewards['counter'] = counter

        csv_writer.writerow(rewards)

def readCurrentGame():
    data = pd.read_csv(currentGame)
    return data

# resetCurrentGame()
# writeCurrentGameToCSV(0, {'economy': 1, 'roundsSurvived': 2, 'finalPosition': 4, 'unitLevelUp': 0,
#                    'mainLevelUp': 1, 'wins': 3, 'lockIn': 0, 'itemPick': -2, 'counter': 1})
# writeCurrentGameToCSV(1, {'economy': 1, 'roundsSurvived': 2, 'finalPosition': 4, 'unitLevelUp': 0,
#                    'mainLevelUp': 1, 'wins': 3, 'lockIn': 0, 'itemPick': -2, 'counter': 2})
# print('done')

# readCurrentGame()

def resetAllGames():
    with open(allGames, 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()



def readAllGames():
    data = pd.read_csv(allGames)
    return data

def writeCurrentGameToHistoryCSV(rewards):

    data = readAllGames()
    counter = 0
    average = 0
    currentLength = len(data['average'])

    try:
        counter = data['counter'][currentLength-1]
        counter = counter + 1

        economy = rewards['economy']
        roundSurvived = rewards['roundsSurvived']
        finalPosition = rewards['finalPosition']
        unitLevelUp = rewards['unitLevelUp']
        mainLevelUp = rewards['mainLevelUp']
        wins = rewards['wins']
        lockIn = rewards['lockIn']
        itemPick = rewards['itemPick']
        losses = rewards['losses']
        runningSum = economy + roundSurvived + finalPosition + unitLevelUp + mainLevelUp + wins + losses + lockIn + itemPick

        runningSum = (data['average'][currentLength-1] * currentLength) + runningSum

        rewards['average'] = runningSum / (currentLength + 1)

        rewards['counter'] = counter


    except Exception as e:
        print(e)
        print('caught error trying to write to game')
        with open(allGames, 'a') as csv_file:

            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            economy = rewards['economy']
            roundSurvived = rewards['roundsSurvived']
            finalPosition = rewards['finalPosition']
            unitLevelUp = rewards['unitLevelUp']
            mainLevelUp = rewards['mainLevelUp']
            wins = rewards['wins']
            lockIn = rewards['lockIn']
            itemPick = rewards['itemPick']
            losses = rewards['losses']
            runningSum = economy + roundSurvived + finalPosition + unitLevelUp + mainLevelUp + wins + losses + lockIn + itemPick
            rewards['average'] = runningSum
            rewards['counter'] = 0

            csv_writer.writerow(rewards)
        return

    with open(allGames, 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writerow(rewards)

# resetAllGames()
# writeCurrentGameToHistoryCSV({'economy': 3, 'roundsSurvived': 3, 'finalPosition': 3, 'unitLevelUp': 3,
#                     'mainLevelUp': 3, 'wins': 3, 'lockIn': 3, 'itemPick': 3})
# writeCurrentGameToHistoryCSV({'economy': 4, 'roundsSurvived': 4, 'finalPosition': 4, 'unitLevelUp': 4,
#                     'mainLevelUp': 4, 'wins': 4, 'lockIn': 4, 'itemPick': 4})
# writeCurrentGameToHistoryCSV({'economy': 5, 'roundsSurvived': 5, 'finalPosition': 5, 'unitLevelUp': 5,
#                     'mainLevelUp': 5, 'wins': 5, 'lockIn': 5, 'itemPick': 5})