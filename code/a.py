import argparse

from ray.rllib.agents.ppo import ppo, DDPPOTrainer
from ray.rllib.env import PolicyServerInput
from ray.rllib.examples.custom_metrics_and_callbacks import MyCallbacks
from ray.tune.logger import pretty_print
from ray.util.client import ray

parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('-ip', type=str, help='IP of this device')

parser.add_argument('-checkpoint', type=str, help='location of checkpoint to restore from')


args = parser.parse_args()

DEFAULT_CONFIG = ppo.PPOTrainer.merge_trainer_configs(
    ppo.DEFAULT_CONFIG,
    {
        # During the sampling phase, each rollout worker will collect a batch
        # `rollout_fragment_length * num_envs_per_worker` steps in size.
        "rollout_fragment_length": 100,
        # Vectorize the env (should enable by default since each worker has
        # a GPU).
        "num_envs_per_worker": 1,
        # During the SGD phase, workers iterate over minibatches of this size.
        # The effective minibatch size will be:
        # `sgd_minibatch_size * num_workers`.
        "sgd_minibatch_size": 50,
        # Number of SGD epochs per optimization round.
        "num_sgd_iter": 25,
        # Download weights between each training step. This adds a bit of
        # overhead but allows the user to access the weights from the trainer.
        # "keep_local_weights_in_sync": True,

        # *** WARNING: configs below are DDPPO overrides over PPO; you
        #     shouldn't need to adjust them. ***
        # DDPPO requires PyTorch distributed.
        "framework": "torch",
        # The communication backend for PyTorch distributed.
        "torch_distributed_backend": "gloo",
        # Learning is no longer done on the driver process, so
        # giving GPUs to the driver does not make sense!
        "num_gpus": 0,
        # Each rollout worker gets a GPU.
        "num_gpus_per_worker": 0,
        # Require evenly sized batches. Otherwise,
        # collective allreduce could fail.
        "truncate_episodes": True,
        # This is auto set based on sample batch size.
        "train_batch_size": -1,
        # Use the connector server to generate experiences.
        "input": (
            lambda ioctx: PolicyServerInput(ioctx, args.ip, 55555)
        ),
        # Use a single worker process to run the server.
        "num_workers": 1,
        # Disable OPE, since the rollouts are coming from online clients.
        "input_evaluation": [],
        "callbacks": MyCallbacks,
        "env_config": {"sleep": True},
        'env': "CartPole-v0"
    },
    _allow_unknown_configs=True,
)

ray.init()

print(f"running on: {args.ip}:55555")

trainer = DDPPOTrainer(config=DEFAULT_CONFIG)
i = 0
while True:
    print(pretty_print(trainer.train()))
    print(f"Finished train run #{i + 1}")
    i += 1
    # checkpoint = trainer.save(checkpoint_path)
    # print("Last checkpoint", checkpoint)