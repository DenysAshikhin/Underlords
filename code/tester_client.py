from ray.rllib.env import PolicyClient
from ray.rllib.examples.env.random_env import RandomEnv
import logging
import time
import argparse
from six.moves import queue
from gym import spaces

#logging.basicConfig(level=logging.INFO)

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
client = PolicyClient(address=f"http://{args.ip}:55555", update_interval=update, inference_mode=local)


#for testing purposes, we will force the env ceated in policy client+server to be a random one and use our game wrapper
#for getting the observation/action/reward

#local = 'remote'
forced = True

env_config = {}
env_config["observation_space"] = spaces.Tuple(
        (spaces.Discrete(9),  # final position * (if not 0 means game is over!)
         spaces.Discrete(101),  # health *
         spaces.Discrete(100),  # gold
         spaces.Discrete(11),  # level *
         spaces.Discrete(99),  # remaining EXP to level up
         spaces.Discrete(50),  # round
         spaces.Discrete(2),  # locked in
         spaces.Discrete(6),  # gamePhase *
         spaces.MultiDiscrete([250, 3]),  # heroToMove: heroLocalID, isUnderlord
         spaces.Discrete(250),  # itemToMove: localID*,
         spaces.Discrete(3),  # reRoll cost
         spaces.Discrete(2),  # rerolled (item)
         spaces.Discrete(35),  # current round timer
         # below are the store heros
         spaces.MultiDiscrete([71, 71, 71, 71, 71]),
         # below are the bench heroes
         spaces.MultiDiscrete([71, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([71, 250, 4, 6, 14, 9, 9, 3]),
         spaces.MultiDiscrete([71, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([71, 250, 4, 6, 14, 9, 9, 3]),
         spaces.MultiDiscrete([71, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([71, 250, 4, 6, 14, 9, 9, 3]),
         spaces.MultiDiscrete([71, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([71, 250, 4, 6, 14, 9, 9, 3]),
         # below are the board heros
         spaces.MultiDiscrete([71, 14, 4, 6, 250, 9, 9, 3]), spaces.MultiDiscrete([71, 14, 4, 6, 250, 9, 9, 3]),
         spaces.MultiDiscrete([71, 14, 4, 6, 250, 9, 9, 3]), spaces.MultiDiscrete([71, 14, 4, 6, 250, 9, 9, 3]),
         spaces.MultiDiscrete([71, 14, 4, 6, 250, 9, 9, 3]), spaces.MultiDiscrete([71, 14, 4, 6, 250, 9, 9, 3]),
         spaces.MultiDiscrete([71, 14, 4, 6, 250, 9, 9, 3]), spaces.MultiDiscrete([71, 14, 4, 6, 250, 9, 9, 3]),
         spaces.MultiDiscrete([71, 14, 4, 6, 250, 9, 9, 3]), spaces.MultiDiscrete([71, 14, 4, 6, 250, 9, 9, 3]),
         # below are underlords to pick (whenever valid) -> underlord ID - specialty
         spaces.MultiDiscrete([5, 3, 5, 3, 5, 3, 5, 3]),
         # below are the items
         spaces.MultiDiscrete([70, 14, 250, 4, 5]), spaces.MultiDiscrete([70, 14, 250, 4, 5]),
         spaces.MultiDiscrete([70, 14, 250, 4, 5]), spaces.MultiDiscrete([70, 14, 250, 4, 5]),
         spaces.MultiDiscrete([70, 14, 250, 4, 5]), spaces.MultiDiscrete([70, 14, 250, 4, 5]),
         spaces.MultiDiscrete([70, 14, 250, 4, 5]), spaces.MultiDiscrete([70, 14, 250, 4, 5]),
         spaces.MultiDiscrete([70, 14, 250, 4, 5]), spaces.MultiDiscrete([70, 14, 250, 4, 5]),
         spaces.MultiDiscrete([70, 14, 250, 4, 5]), spaces.MultiDiscrete([70, 14, 250, 4, 5]),
         # below are the items to pick from
         spaces.MultiDiscrete([70, 70, 70]),
         # below are dicts of other players: slot, health, gold, level, boardUnits (ID, Tier)
         spaces.MultiDiscrete(
             [9, 101, 100, 11, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4]),
         spaces.MultiDiscrete(
             [9, 101, 100, 11, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4]),
         spaces.MultiDiscrete(
             [9, 101, 100, 11, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4]),
         spaces.MultiDiscrete(
             [9, 101, 100, 11, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4]),
         spaces.MultiDiscrete(
             [9, 101, 100, 11, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4]),
         spaces.MultiDiscrete(
             [9, 101, 100, 11, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4]),
         spaces.MultiDiscrete(
             [9, 101, 100, 11, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4, 71, 4])

         ))
env_config["action_space"] = spaces.MultiDiscrete([9, 9, 9, 4])
env_config["p_done"] = 0.05
env = RandomEnv(env_config)


print('trying to get initial eid')
episode_id = client.start_episode()

gameObservation = env.reset()
reward = 0
print('starting main loop')


while True:
    action = None

    for i in range(10):

        try:
            action = client.get_action(episode_id=episode_id, observation=gameObservation)

            break
        except queue.Empty:
            continue

    if action is None:
        raise ValueError("Policy failed to return an action after 10 tries")

    gameObservation, reward, done, info = env.step([action[0], action[1], action[2], action[3]])

    client.log_returns(episode_id=episode_id, reward=reward)

    finalPosition = int(done) #env.underlord.finalPlacement

    if finalPosition != 0:
        print(f"GAME OVER! final position: {finalPosition} - final reward: {reward}")
        reward = 0
        # need to call a reset of env here
        client.end_episode(episode_id=episode_id, observation=gameObservation)

        # if forced:
        #     print("Updating policy weights")
        #     client.update_policy_weights()

        episode_id = client.start_episode(episode_id=None)
        gameObservation = env.reset()
        print('got past restarting of the new episode, for loop should begin anew!')

    print('----')