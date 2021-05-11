import gym
from ray.rllib.env import PolicyClient
from ray.tune.registry import register_env

from environment import UnderlordEnv
import logging
import time
import argparse

from logger import logger

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('-ip', type=str,
                    help='IP of this device')

parser.add_argument('-speed', type=float,
                    help='gameFactor, default 1.0')

parser.add_argument('-update', type=float,
                    help='seconds how often to update from main process')

args = parser.parse_args()

update = 3600.0

if args.update:
    update = args.update

print(f"Going to update at {update} seconds interval")

print('trying to launch policy client')
client = PolicyClient(address=f"http://{args.ip}:55555", update_interval=update)
# env = UnderlordEnv({'sleep': True})
# env.root.update()


print('trying to get initial eid')
episode_id = client.start_episode()
# gameObservation = env.underlord.getObservation()
reward = 0
print('starting main loop')
replayList = []

if args.speed is not None:
    print(f"multiply by {args.speed}")

    client.env.underlord.mouseSleepTime *= args.speed
    client.env.underlord.shopSleepTime *= args.speed

while True:
    # print('getting observation')
    start_time = time.time()
    gameObservation = client.env.underlord.getObservation()
    obs_time = time.time() - start_time
    # print(gameObservation)
    # print("--- %s seconds to get observation ---" % (time.time() - start_time))
    # start_time = time.time()
    client.env.root.update()
    # print("--- %s seconds to update GUI ---" % (time.time() - start_time))
    # start_time = time.time()

    action = None
    # print('trying to get action')

    action = client.get_action(episode_id=episode_id, observation=gameObservation)
    # print("got action")
    # print("--- %s seconds to get action ---" % (time.time() - start_time))
    # start_time = time.time()
    # print(action[0], action[1] - 1, action[2] - 1, action[3] - 1)

    act_time = time.time()
    reward += client.env.underlord.act(action=action[0], x=action[1] - 1, y=action[2] - 1, selection=action[3] - 1)
    act_time = time.time() - act_time
    # print("--- %s seconds to get do action ---" % (time.time() - start_time))
    # start_time = time.time()
    # print(f"running reward: {reward}")
    client.log_returns(episode_id=episode_id, reward=reward)
    # print('finished logging step')
    finalPosition = client.env.underlord.finalPlacement
    # print("--- %s seconds to get finish logging return ---" % (time.time() - start_time))

    replayList.append((gameObservation, action, reward))

    print(
        f"Round: {gameObservation[5]} - Time Left: {gameObservation[12]} - Obs duration: {obs_time} - Act duration: {act_time} - Overall duration: {time.time() - start_time}")

    if finalPosition != 0:
        print(f"GAME OVER! final position: {finalPosition} - final reward: {reward}")
        reward = 0
        # need to call a reset of env here
        client.end_episode(episode_id=episode_id, observation=gameObservation)
        client.env.underlord.resetEnv()
        fileWriter = logger(episode_id)
        fileWriter.createLog()
        fileWriter.writeLog(replayList)
        replayList.clear()

        episode_id = client.start_episode(episode_id=None)
        print('got past restarting of the new episode, for loop should begin anew!')

    print('----')
