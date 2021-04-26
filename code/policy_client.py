import gym
from ray.rllib.env import PolicyClient
from ray.tune.registry import register_env

from environment import UnderlordEnv

client = PolicyClient(address='http://localhost:55555')
# env = UnderlordEnv({'sleep': True})
# env.root.update()



episode_id = client.start_episode()
# gameObservation = env.underlord.getObservation()
reward = 0

while True:
    gameObservation = client.env.underlord.getObservation()
    break
    env.root.update()

    action = client.get_action(episode_id=episode_id, observation=gameObservation)
    print(f"taking action:")
    print(action)
    print('----')
    reward += env.underlord.act(action=action[0], x=action[1], y=action[2], selection=action[3])
    client.log_returns(episode_id=episode_id, reward=reward)

    if client.underlord.finished() != -1:
        reward = 0
        #need to call a reset of env here
        client.end_episode(episode_id=episode_id, observation=gameObservation)
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