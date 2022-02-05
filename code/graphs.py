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
        losses = data['losses']
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
        plt.plot(counter, losses, label='losses')
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
            plt.annotate('Losses: %0.3f' % losses[len(losses) - 1], xy=(1, losses[len(losses) - 1]), xytext=(8, 0),
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
        plt.xlabel("Actions (every 10)")
        plt.ylabel("Reward")
        plt.legend(loc='upper left', title="Reward Sources")
        plt.tight_layout()

    else:
        data = writer.readAllGames()
        economy = data['economy']
        ecoAvg = 0
        ecoAvgT = 0
        roundSurvived = data['roundsSurvived']
        roundSurvAvg = 0
        roundSurvAvgT = 0
        finalPosition = data['finalPosition']
        finalPosAvg = 0
        finalPosAvgT = 0
        unitLevelUp = data['unitLevelUp']
        unitLevAvg = 0
        unitLevAvgT = 0
        mainLevelUp = data['mainLevelUp']
        mainLevAvg = 0
        mainLevAvgT = 0
        wins = data['wins']
        winsAvg = 0
        winsAvgT = 0
        losses = data['losses']
        lossAvg = 0
        lossAvgT = 0
        lockIn = data['lockIn']
        lockInAvg = 0
        lockInAvgT = 0
        itemPick = data['itemPick']
        itemPickAvg = 0
        itemPickAvgT = 0
        counter = data['counter']
        average = data['average']

        avg = 0

        try:

            length = len(average)

            avgT = average.sum() / length
            ecoAvgT = economy.sum() / length
            roundSurvAvgT = roundSurvived.sum() / length
            finalPosAvgT = finalPosition.sum() / length
            unitLevAvgT = unitLevelUp.sum() / length
            mainLevAvgT = mainLevelUp.sum() / length
            winsAvgT = wins.sum() / length
            lossAvgT = losses.sum() / length
            lockInAvgT = lockIn.sum() / length
            itemPickAvgT = itemPick.sum() / length

            average = average[-100:]
            economy = economy[-100:]
            roundSurvived = roundSurvived[-100:]
            finalPosition = finalPosition[-100:]
            unitLevelUp = unitLevelUp[-100:]
            mainLevelUp = mainLevelUp[-100:]
            wins = wins[-100:]
            losses = losses[-100:]
            lockIn = lockIn[-100:]
            itemPick = itemPick[-100:]
            counter = counter[-100:]


            length = len(average)

            avg = average.sum()/length
            ecoAvg = economy.sum()/length
            roundSurvAvg = roundSurvived.sum() / length
            finalPosAvg = finalPosition.sum() / length
            unitLevAvg= unitLevelUp.sum() / length
            mainLevAvg = mainLevelUp.sum() / length
            winsAvg = wins.sum() / length
            lossAvg = losses.sum() / length
            lockInAvg = lockIn.sum() / length
            itemPickAvg = itemPick.sum() / length
        except Exception as e:
            print('no sum yet')

        plt.cla()

        plt.plot(counter, economy, label=f"Economy, avg: {str(round(ecoAvg, 2))}, all time: {str(round(ecoAvgT, 2))}")
        plt.plot(counter, roundSurvived, label=f"round Survived, avg: {str(round(roundSurvAvg, 2))}, all time: {str(round(roundSurvAvgT, 2))}")
        plt.plot(counter, finalPosition, label=f"finalPosition, avg: {str(round(finalPosAvg, 2))}, all time: {str(round(finalPosAvgT, 2))}")
        plt.plot(counter, unitLevelUp, label=f"unit Level Up, avg: {str(round(unitLevAvg, 2))}, all time: {str(round(unitLevAvgT, 2))}")
        plt.plot(counter, mainLevelUp, label=f"main Level Up, avg: {str(round(mainLevAvg, 2))}, all time: {str(round(mainLevAvgT, 2))}")
        plt.plot(counter, wins, label=f"wins, avg: {str(round(winsAvg, 2))}, all time: {str(round(winsAvgT, 2))}")
        plt.plot(counter, losses, label=f"losses, avg: {str(round(lossAvg, 2))}, all time: {str(round(lossAvgT, 2))}")
        plt.plot(counter, lockIn, label=f"lock In, avg: {str(round(lockInAvg, 2))}, all time: {str(round(lockInAvgT, 2))}")
        plt.plot(counter, itemPick, label=f"item Pick, avg: {str(round(itemPickAvg, 2))}, all time: {str(round(itemPickAvgT, 2))}")

        try:
            plt.annotate('Eco: %0.3f' % economy.tail(1), xy=(1, economy.tail(1)), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')

            plt.annotate('Rounds: %0.3f' % roundSurvived.tail(1),
                         xy=(1, roundSurvived.tail(1)), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Pos: %0.3f' % finalPosition.tail(1),
                         xy=(1, finalPosition.tail(1)), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Tiering: %0.3f' % unitLevelUp.tail(1),
                         xy=(1, unitLevelUp.tail(1)), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Leveling: %0.3f' % mainLevelUp.tail(1),
                         xy=(1, mainLevelUp.tail(1)), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Wins: %0.3f' % wins.tail(1), xy=(1, wins.tail(1)), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Losses: %0.3f' % losses.tail(1), xy=(1, losses.tail(1)), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Locking: %0.3f' % lockIn.tail(1), xy=(1, lockIn.tail(1)), xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')
            plt.annotate('Picks: %0.3f' % itemPick.tail(1), xy=(1, itemPick.tail(1)),
                         xytext=(8, 0),
                         xycoords=('axes fraction', 'data'), textcoords='offset points')


        except Exception as e:
            print(e)
            print("Error trying to annotate")



        plt.title(f"Historical Game Rewards (past 100 games): running average: {avg}")
        plt.legend(loc='upper left', title="Reward Sources")
        plt.xlabel("Games")
        plt.ylabel("Reward")
        plt.tight_layout()


ani = FuncAnimation(plt.gcf(), animate, interval=1000 * 10)

plt.tight_layout()
plt.show()
