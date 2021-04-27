import gym
from ray.rllib.env import PolicyClient
from ray.tune.registry import register_env

from environment import UnderlordEnv

import argparse
parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('-ip', type=str,
                    help='IP of this device')

args = parser.parse_args()

print('trying to launch policy client')
client = PolicyClient(address=f"http://{args.ip}:55555")
# env = UnderlordEnv({'sleep': True})
# env.root.update()


print('trying to get initial eid')
episode_id = client.start_episode()
# gameObservation = env.underlord.getObservation()
reward = 0
print('starting main loop')
while True:
    print('getting observation')
    gameObservation = client.env.underlord.getObservation()
    print('updating gui')
    client.env.root.update()

    print('getting action')
    action = client.get_action(episode_id=episode_id, observation=gameObservation)
    print(f"taking action:")
    print(action)
    print('----')
    reward += client.env.underlord.act(action=action[0], x=action[1]-1, y=action[2]-1, selection=action[3]-1)
    print(f"running reward: {reward}")
    client.log_returns(episode_id=episode_id, reward=reward)
    print('finished logging step')

    if client.env.underlord.finished() != -1:
        reward = 0
        #need to call a reset of env here
        client.end_episode(episode_id=episode_id, observation=gameObservation)
        client.env.resetEnv()
        episode_id = client.start_episode(episode_id=None)

    #
    # while True:
    #     obs, reward, done, info = env.step(action)
    #     rewards += reward
    #     client.log_returns(eid, reward, info=info)
    #     if done:
    #         print("Total reward:", rewards)
    #         if rewards >= args.stop_reward:
    #             print("Target reward achieved, exiting")
    #             exit(0)
    #         rewards = 0
    #         client.end_episode(eid, obs)
    #         obs = env.reset()
    #         eid = client.start_episode(training_enabled=not args.no_train)