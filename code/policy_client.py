import gym
from ray.rllib.env import PolicyClient
from ray.tune.registry import register_env

from environment import UnderlordEnv

import time
import argparse

from logger import logger

parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('-ip', type=str,
                    help='IP of this device')

parser.add_argument('-speed', type=float,
                    help='gameFactor, default 1.0')

args = parser.parse_args()

print('trying to launch policy client')
client = PolicyClient(address=f"http://{args.ip}:55555", update_interval=600.0)
# env = UnderlordEnv({'sleep': True})
# env.root.update()


print('trying to get initial eid')
episode_id = client.start_episode()
# gameObservation = env.underlord.getObservation()
reward = 0
print('starting main loop')
replayList = []
client.env.underlord.mouseSleepTime = 0.1 * args.speed
client.env.underlord.shopSleepTime = 0.3 * args.speed

while True:
    # print('getting observation')
    # start_time = time.time()
    gameObservation = client.env.underlord.getObservation()
    # print("--- %s seconds to get observation ---" % (time.time() - start_time))
    # start_time = time.time()
    client.env.root.update()
    # print("--- %s seconds to update GUI ---" % (time.time() - start_time))
    # start_time = time.time()

    action = None
    try:
        action = client.get_action(episode_id=episode_id, observation=gameObservation)
    except:
        action = client.get_action(episode_id=episode_id, observation=gameObservation)
    # print("--- %s seconds to get action ---" % (time.time() - start_time))
    # start_time = time.time()
    print(action)
    print('----')
    reward += client.env.underlord.act(action=action[0], x=action[1] - 1, y=action[2] - 1, selection=action[3] - 1)
    # print("--- %s seconds to get do action ---" % (time.time() - start_time))
    # start_time = time.time()
    print(f"running reward: {reward}")
    client.log_returns(episode_id=episode_id, reward=reward)
    print('finished logging step')
    finalPosition = client.env.underlord.finished()
    # print("--- %s seconds to get finish logging return ---" % (time.time() - start_time))

    replayList.append((gameObservation, action, finalPosition))

    if finalPosition != -1:
        print(f"GAME OVER! final position: {finalPosition} ")
        reward = 0
        # need to call a reset of env here
        client.end_episode(episode_id=episode_id, observation=gameObservation)
        client.env.resetEnv()
        fileWriter = logger(episode_id)
        fileWriter.createLog()
        fileWriter.writeLog(replayList)
        replayList.clear()

        episode_id = client.start_episode(episode_id=None)
