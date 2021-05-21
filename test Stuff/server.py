#!/usr/bin/env python
"""Example of running a policy server. Copy this file for your use case.
To try this out, in two separate shells run:
    $ python cartpole_server.py
    $ python cartpole_client.py --inference-mode=local|remote
"""

import argparse
import os

import ray
from ray.rllib.agents.dqn import DQNTrainer
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.env.policy_server_input import PolicyServerInput
from ray.rllib.examples.custom_metrics_and_callbacks import MyCallbacks
from ray.tune.logger import pretty_print

SERVER_ADDRESS = "localhost"
SERVER_PORT = 9900
CHECKPOINT_FILE = "last_checkpoint_{}.out"

parser = argparse.ArgumentParser()
parser.add_argument("--run", type=str, default="DQN")
parser.add_argument(
    "--framework",
    choices=["tf", "torch"],
    default="tf",
    help="The DL framework specifier.")
parser.add_argument(
    "--no-restore",
    action="store_true",
    help="Do not restore from a previously saved checkpoint (location of "
         "which is saved in `last_checkpoint_[algo-name].out`).")

if __name__ == "__main__":
    args = parser.parse_args()
    ray.init()

    env = "CartPole-v0"
    connector_config = {
        # Use the connector server to generate experiences.
        "input": (
            lambda ioctx: PolicyServerInput(ioctx, SERVER_ADDRESS, SERVER_PORT)
        ),
        # Use a single worker process to run the server.
        "num_workers": 0,
        # Disable OPE, since the rollouts are coming from online clients.
        "input_evaluation": [],
        "callbacks": MyCallbacks,
    }

    # if args.run == "DQN":
    #     # Example of using DQN (supports off-policy actions).
    #     trainer = DQNTrainer(
    #         env=env,
    #         config=dict(
    #             connector_config, **{
    #                 "learning_starts": 100,
    #                 "timesteps_per_iteration": 200,
    #                 "framework": args.framework,
    #             }))
    # elif args.run == "PPO":
    #     # Example of using PPO (does NOT support off-policy actions).
    #     trainer = PPOTrainer(
    #         env=env,
    #         config=dict(
    #             connector_config, **{
    #                 "rollout_fragment_length": 1000,
    #                 "train_batch_size": 4000,
    #                 "framework": args.framework,
    #             }))
    # else:
    #     raise ValueError("--run must be DQN or PPO")

    trainer = PPOTrainer(
        env=env,
        config=dict(
            connector_config, **{
                "rollout_fragment_length": 1000,
                "train_batch_size": 4000,
                "framework": args.framework,
            }))

    checkpoint_path = CHECKPOINT_FILE.format(args.run)

    # Serving and training loop.
    while True:
        print(pretty_print(trainer.train()))
