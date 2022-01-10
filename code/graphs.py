import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd

import writeData as writer


def animate(i):
    # swapper = i % 20

    # if swapper > 10:
    if i % 2 == 0:

        data = writer.readCurrentGame()
        economy = data['economy']
        roundSurvived = data['roundsSurvived']
        finalPosition = data['finalPosition']
        unitLevelUp = data['unitLevelUp']
        mainLevelUp = data['mainLevelUp']
        wins = data['wins']
        lockIn = data['lockIn']
        itemPick = data['itemPick']
        counter = data['counter']
        average = data['average']

        plt.cla()

        plt.plot(counter, economy, label='Economy')
        plt.plot(counter, roundSurvived, label='round Survived')
        plt.plot(counter, finalPosition, label='finalPosition')
        plt.plot(counter, unitLevelUp, label='unit Level Up')
        plt.plot(counter, mainLevelUp, label='main Level Up')
        plt.plot(counter, wins, label='wins')
        plt.plot(counter, lockIn, label='lock In')
        plt.plot(counter, itemPick, label='item Pick')
        # plt.plot(counter, average, label='Average Reward', linestyle=(0, (3, 5, 1, 5, 1, 5)))

        sum = 0

        try:
            sum = average[len(average) - 1]
        except Exception as e:
            print('no sum yet')

        try:
            plt.annotate('Eco: %0.3f' % economy[len(economy) - 1], xy=(1, economy[len(economy) - 1]), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')

            plt.annotate('Rounds: %0.3f' % roundSurvived[len(roundSurvived) - 1],
                         xy=(1, roundSurvived[len(roundSurvived) - 1]), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Pos: %0.3f' % finalPosition[len(finalPosition) - 1],
                         xy=(1, finalPosition[len(finalPosition) - 1]), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Tiering: %0.3f' % unitLevelUp[len(unitLevelUp) - 1],
                         xy=(1, unitLevelUp[len(unitLevelUp) - 1]), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Leveling: %0.3f' % mainLevelUp[len(mainLevelUp) - 1],
                         xy=(1, mainLevelUp[len(mainLevelUp) - 1]), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Wins: %0.3f' % wins[len(wins) - 1], xy=(1, wins[len(wins) - 1]), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Locking: %0.3f' % lockIn[len(lockIn) - 1], xy=(1, lockIn[len(lockIn) - 1]), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Picks: %0.3f' % itemPick[len(itemPick) - 1], xy=(1, itemPick[len(itemPick) - 1]),
                         xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')


        except Exception as e:
            print(e)
            print("Error trying to annotate")

        plt.title(f"Current Game Rewards - Current Reward: {sum}")
        plt.xlabel("Actions")
        plt.ylabel("Reward")
        plt.legend(loc='upper left', title="Reward Sources")
        plt.tight_layout()

    else:
        data = writer.readAllGames()
        economy = data['economy']
        roundSurvived = data['roundsSurvived']
        finalPosition = data['finalPosition']
        unitLevelUp = data['unitLevelUp']
        mainLevelUp = data['mainLevelUp']
        wins = data['wins']
        lockIn = data['lockIn']
        itemPick = data['itemPick']
        counter = data['counter']
        average = data['average']

        avg = 0

        try:
            avg = average.sum()/len(average)
        except Exception as e:
            print('no sum yet')


        plt.cla()

        plt.plot(counter, economy, label='Economy')
        plt.annotate('Eco: %0.3f' % economy[len(economy) - 1], xy=(1, economy[len(economy) - 1]), xytext=(8, 0),
                     xycoords=('axes fraction', 'data'), textcoords='offset points')
        plt.plot(counter, roundSurvived, label='round Survived')
        plt.annotate('Rounds: %0.3f' % roundSurvived[len(roundSurvived) - 1], xy=(1, roundSurvived[len(roundSurvived) - 1]), xytext=(8, 0),
                     xycoords=('axes fraction', 'data'), textcoords='offset points')
        plt.plot(counter, finalPosition, label='finalPosition')
        plt.annotate('Pos: %0.3f' % finalPosition[len(finalPosition) - 1], xy=(1, finalPosition[len(finalPosition) - 1]), xytext=(8, 0),
                     xycoords=('axes fraction', 'data'), textcoords='offset points')
        plt.plot(counter, unitLevelUp, label='unit Level Up')
        plt.annotate('Tiering: %0.3f' % unitLevelUp[len(unitLevelUp) - 1], xy=(1, unitLevelUp[len(unitLevelUp) - 1]), xytext=(8, 0),
                     xycoords=('axes fraction', 'data'), textcoords='offset points')
        plt.plot(counter, mainLevelUp, label='main Level Up')
        plt.annotate('Leveling: %0.3f' % mainLevelUp[len(mainLevelUp) - 1], xy=(1, mainLevelUp[len(mainLevelUp) - 1]), xytext=(8, 0),
                     xycoords=('axes fraction', 'data'), textcoords='offset points')
        plt.plot(counter, wins, label='wins')
        plt.annotate('Wins: %0.3f' % wins[len(wins) - 1], xy=(1, wins[len(wins) - 1]), xytext=(8, 0),
                     xycoords=('axes fraction', 'data'), textcoords='offset points')
        plt.plot(counter, lockIn, label='lock In')
        plt.annotate('Locking: %0.3f' % lockIn[len(lockIn) - 1], xy=(1, lockIn[len(lockIn) - 1]), xytext=(8, 0),
                     xycoords=('axes fraction', 'data'), textcoords='offset points')
        plt.plot(counter, itemPick, label='item Pick')
        plt.annotate('Picks: %0.3f' % itemPick[len(itemPick) - 1], xy=(1, itemPick[len(itemPick) - 1]), xytext=(8, 0),
                     xycoords=('axes fraction', 'data'), textcoords='offset points')
        # plt.plot(counter, average, label='Average Reward', linestyle=(0, (3, 5, 1, 5, 1, 5)))

        #for var in (economy, roundSurvived,finalPosition, unitLevelUp,mainLevelUp, wins,lockIn, itemPick, average):
        # for var in (economy, roundSurvived, finalPosition, unitLevelUp, mainLevelUp, wins, lockIn, itemPick):
        #     plt.annotate('%0.3f' % var[len(var) - 1], xy=(1, var[len(var) - 1]), xytext=(8, 0),
        #                  xycoords=('axes fraction', 'data'), textcoords='offset points')

        plt.title(f"Historical Game Rewards: running average: {avg}")
        plt.legend(loc='upper left', title="Reward Sources")
        plt.xlabel("Games")
        plt.ylabel("Reward")
        plt.tight_layout()


ani = FuncAnimation(plt.gcf(), animate, interval=1000 * 1)

plt.tight_layout()
plt.show()
