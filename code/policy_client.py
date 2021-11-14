from queue import Queue
from tkinter import Tk

import gym
from ray.rllib.env import PolicyClient
from ray.tune.registry import register_env

from environment import UnderlordEnv
import logging
import time
import argparse
from six.moves import queue

from logger import logger

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('-ip', type=str,
                    help='IP of this device')

parser.add_argument('-speed', type=float,
                    help='gameFactor, default 1.0')

parser.add_argument('-update', type=float,
                    help='seconds how often to update from main process')

parser.add_argument('-local', type=str,
                    help='Whether to create and update a local copy of the AI (adds delay) or query server for each action.'
                         'possible values: "local" or "remote"')

args = parser.parse_args()

update = 3600.0



local = 'local'

remoteee = False

if args.update:
    update = args.update
    # remoteee = True

if args.local:
    local = args.local
    
if local == 'remote':
    remoteee=True

print(f"Going to update {local}-y  at {update} seconds interval")

print('trying to launch policy client')
client = PolicyClient(address=f"http://{args.ip}:55556", update_interval=60, inference_mode=local)
# env = UnderlordEnv({'sleep': True})
# env.root.update()

# for testing purposes, we will force the env ceated in policy client+server to be a random one and use our game wrapper
# for getting the observation/action/reward

local = 'remote'
forced = True
root = None

# if local == 'remote':
#     root = Tk()
#     root.resizable(0, 0)
#     root.geometry('+0+0')
#     env = UnderlordEnv(root, {'sleep': True})
# else:
#     env = client.env

root = Tk()
root.resizable(0, 0)
root.geometry('+0+0')
env = UnderlordEnv(root, {'sleep': True})

print('trying to get initial eid')
episode_id = client.start_episode()

if local == 'remote':
    env.underlord.startNewGame()

# gameObservation = env.underlord.getObservation()
reward = 0
print('starting main loop')
replayList = []

if args.speed is not None:
    print(f"multiply by {args.speed}")

    env.underlord.mouseSleepTime *= args.speed
    env.underlord.shopSleepTime *= args.speed

update = True

runningReward = 0

closeStore = False

while True:

    # print( not env.underlord.pickTime())
    # print(env.underlord.combatType)
    # print(env.underlord.finalPlacement)
    
    
    if env.underlord.newRoundStarted:
            if env.underlord.prevHP == env.underlord.health:
                env.underlord.extraReward += 10 * 0.025
                print("It didn't loose!")
            else:
                print(f"Lost {env.underlord.prevHP - env.underlord.health} health")

            env.underlord.prevHP = env.underlord.health
            env.underlord.newRoundStarted = False
    
    
    if not env.underlord.pickTime():
        if env.underlord.combatType != 0 and env.underlord.finalPlacement == 0:
            if not closeStore:
                env.underlord.closeStore(True)
                closeStore = True
                # print('wow1')
            # print('wow3')
            time.sleep(0.1)
            continue

        elif closeStore:
            # print('wow2')
            time.sleep(0.3)
            env.underlord.openStore(None, None, True)
            closeStore = False


    # print('getting observation')
    # start_time = time.time()
    # print(f"time: {time}")
    gameObservation = env.underlord.getObservation()

    # print(gameObservation)

    if not env.observation_space.contains(gameObservation):
        print(gameObservation)
        print("Not lined up 1")
        sys.exit()


    # obs_time = time.time() - start_time

    # print(gameObservation)
    # print("--- %s seconds to get observation ---" % (time.time() - start_time))
    # start_time = time.time()

    # print("--- %s seconds to update GUI ---" % (time.time() - start_time))
    # start_time = time.time()

    action = None
    # print('trying to get action')

    # print("got action")
    # print("--- %s seconds to get action ---" % (time.time() - start_time))
    # start_time = time.time()
    # print(action[0], action[1] - 1, action[2] - 1, action[3] - 1)

    # act_time = time.time()
    # print(gameObservation)
    #
    # for i in range(10):
    #
    #     try:

    action = client.get_action(episode_id=episode_id, observation=gameObservation)

    #     break
    # except queue.Empty:
    #     continue

    # if action is None:
    #     raise ValueError("Policy failed to return an action after 10 tries")

    # reward = env.underlord.act(action=action[0], x=action[1] - 1, y=action[2] - 1, selection=action[3] - 1)

    reward = env.underlord.act(action=action[0], x=action[1], y=action[2] - 1)
    root.update()
    runningReward += reward
    # act_time = time.time() - act_time
    # print("--- %s seconds to get do action ---" % (time.time() - start_time))
    # print(f"running reward: {reward}")
    client.log_returns(episode_id=episode_id, reward=reward)
    # print('finished logging step')
    finalPosition = env.underlord.finalPlacement
    # print("--- %s seconds to get finish logging return ---" % (time.time() - start_time))

    # replayList.append((gameObservation, action, reward))

    # print(
    #     f"Round: {gameObservation[5]} - Time Left: {gameObservation[12]} - Obs duration: {obs_time} - Act duration: {act_time} - Overall duration: {time.time() - start_time}")

    if finalPosition != 0:
        print(env.underlord.rewardSummary)
        print(f"GAME OVER! final position: {finalPosition} - final reward: {runningReward} - bought: {env.underlord.localHeroID} heroes!")
        runningReward = 0
        reward = 0
        # need to call a reset of env here
        finalObs = env.underlord.getObservation()

        if not env.observation_space.contains(finalObs):
            print(gameObservation)
            print("Not lined up 3")
            sys.exit()
        # if not env.observation_space.contains(finalObs):
        #     print(gameObservation)
        #     print("Not lined up 4")

        client.end_episode(episode_id=episode_id, observation=finalObs)
        env.underlord.resetEnv()
        # fileWriter = logger(episode_id)
        # fileWriter.createLog()
        # fileWriter.writeLog(replayList)
        # replayList.clear()

        # if forced:
        #     # print("Updating policy weights")
        #     client.update_policy_weights()
        #     print('Updated policy weights')

        if remoteee:
            print("remote sleep")
            time.sleep(45)
            print('remote sleep done')

        episode_id = client.start_episode(episode_id=None)

        if local == 'remote':
            env.underlord.startNewGame()

        env.underlord.openStore()
        # env.underlord.lockIn()
        # env.underlord.lockIn()
        # print('got past restarting of the new episode, for loop should begin anew!')

    # timeLeft = gameObservation[13]
    # print(f"timeLeft: {timeLeft}")
    # # print(env.underlord.itemPicks is None)
    # # print(env.underlord.underlordPicks is None)
    # # print(env.underlord.round > 2)
    # # print(update)
    #
    # if (timeLeft < 5) and (env.underlord.itemPicks is None) and (env.underlord.underlordPicks is None)\
    #         and (env.underlord.round > 2) and (env.underlord.combatType == 3) and update:
    #     print('inside of policy client combat')
    #     client.update_policy_weights()
    #     print('Combat phase updated policy weights')
    #     update = False
    #     # raise Exception("Policy updated!")
    #
    # if timeLeft > 5:
    #     print('reseting the update')
    #     update = True

    # time.sleep(0.5)
    # print('----')
