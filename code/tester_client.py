from ray.rllib.env import PolicyClient

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
client = PolicyClient(address=f"http://{args.ip}:55555", update_interval=None, inference_mode=local)

# for testing purposes, we will force the env ceated in policy client+server to be a random one and use our game wrapper
# for getting the observation/action/reward

local = 'remote'
forced = True

if local == 'remote':
    env = UnderlordEnv({'sleep': True})
else:
    env = client.env

print('trying to get initial eid')
episode_id = client.start_episode()

if local == 'remote':
    env.underlord.startNewGame()

reward = 0
print('starting main loop')

while True:

    gameObservation = env.underlord.getObservation()

    env.root.update()  # updating gui (tkinter) to see what the bot sees of the game state

    action = None

    for i in range(10):

        try:
            action = client.get_action(episode_id=episode_id, observation=gameObservation)

            break
        except queue.Empty:
            continue

    if action is None:
        raise ValueError("Policy failed to return an action after 10 tries")

    reward += env.underlord.act(action=action[0], x=action[1] - 1, y=action[2] - 1, selection=action[3] - 1)

    client.log_returns(episode_id=episode_id, reward=reward)

    finalPosition = env.underlord.finalPlacement

    if finalPosition != 0:
        print(f"GAME OVER! final position: {finalPosition} - final reward: {reward}")
        reward = 0
        # need to call a reset of env here
        client.end_episode(episode_id=episode_id, observation=gameObservation)
        env.underlord.resetEnv()

        # if forced:
        #     print("Updating policy weights")
        #     client.update_policy_weights()

        episode_id = client.start_episode(episode_id=None)

        if local == 'remote':
            env.underlord.startNewGame()
        print('got past restarting of the new episode, for loop should begin anew!')

    print('----')