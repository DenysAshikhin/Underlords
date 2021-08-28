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


if args.update:
    update = args.update

if args.local:
    local = args.local


print(f"Going to update at {update} seconds interval")

print('trying to launch policy client')
client = PolicyClient(address=f"http://{args.ip}:55556", update_interval=None, inference_mode=local)
# env = UnderlordEnv({'sleep': True})
# env.root.update()

#for testing purposes, we will force the env ceated in policy client+server to be a random one and use our game wrapper
#for getting the observation/action/reward

local = 'remote'
forced = True
root = None

if local == 'remote':
    root = Tk()
    root.resizable(0, 0)
    root.geometry('+0+0')
    env = UnderlordEnv(root, {'sleep': True})
else:
    env = client.env


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

while True:
    # print('getting observation')
    start_time = time.time()
    gameObservation = env.underlord.getObservation()
    # print(gameObservation)
    # print(env.observation_space.contains(gameObservation))
    # print('-----------')
    obs_time = time.time() - start_time

    # print(gameObservation)
    # print("--- %s seconds to get observation ---" % (time.time() - start_time))
    # start_time = time.time()
    root.update()
    # print("--- %s seconds to update GUI ---" % (time.time() - start_time))
    # start_time = time.time()

    action = None
    # print('trying to get action')

    # print("got action")
    # print("--- %s seconds to get action ---" % (time.time() - start_time))
    # start_time = time.time()
    # print(action[0], action[1] - 1, action[2] - 1, action[3] - 1)

    act_time = time.time()
    # print(gameObservation)
    #
    # for i in range(10):
    #
    #     try:

    action = client.get_action(episode_id=episode_id, observation=gameObservation)

        #     break
        # except queue.Empty:
        #     continue

    if action is None:
        raise ValueError("Policy failed to return an action after 10 tries")

    reward += env.underlord.act(action=action[0], x=action[1] - 1, y=action[2] - 1, selection=action[3] - 1)

    act_time = time.time() - act_time
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
        # print(f"GAME OVER! final position: {finalPosition} - final reward: {reward}")
        reward = 0
        # need to call a reset of env here
        client.end_episode(episode_id=episode_id, observation=gameObservation)
        env.underlord.resetEnv()
        # fileWriter = logger(episode_id)
        # fileWriter.createLog()
        # fileWriter.writeLog(replayList)
        # replayList.clear()

        if forced:
            # print("Updating policy weights")
            client.update_policy_weights()
            print('Updated policy weights')

        episode_id = client.start_episode(episode_id=None)

        if local == 'remote':
            env.underlord.startNewGame()
        # print('got past restarting of the new episode, for loop should begin anew!')

    # print('----')
