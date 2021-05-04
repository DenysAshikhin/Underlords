# Adds the following updates to the `PPOTrainer` config in
# rllib/agents/ppo/ppo.py.
import os

import ray
from ray.rllib.agents import with_common_config
from ray.rllib.agents.ppo import ppo, DDPPOTrainer
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.env import PolicyServerInput
from ray.rllib.examples.custom_metrics_and_callbacks import MyCallbacks
from ray.tune.logger import pretty_print

from environment import UnderlordEnv

import argparse

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
        'env': UnderlordEnv
    },
    _allow_unknown_configs=True,
)

# DEFAULT_CONFIG = with_common_config({
#     # Should use a critic as a baseline (otherwise don't use value baseline;
#     # required for using GAE).
#     "use_critic": True,
#     # If true, use the Generalized Advantage Estimator (GAE)
#     # with a value function, see https://arxiv.org/pdf/1506.02438.pdf.
#     "use_gae": True,
#     # The GAE (lambda) parameter.
#     "lambda": 1.0,
#     # Initial coefficient for KL divergence.
#     "kl_coeff": 0.2,
#     # Size of batches collected from each worker.
#     "rollout_fragment_length": 1000,
#     # Number of timesteps collected for each SGD round. This defines the size
#     # of each SGD epoch.
#     "train_batch_size": 1000,
#     # Total SGD batch size across all devices for SGD. This defines the
#     # minibatch size within each epoch.
#     "sgd_minibatch_size": 50,
#     # Number of SGD iterations in each outer loop (i.e., number of epochs to
#     # execute per train batch).
#     "num_sgd_iter": 15,
#     # Whether to shuffle sequences in the batch when training (recommended).
#     "shuffle_sequences": True,
#     # Stepsize of SGD.
#     "lr": 5e-5,
#     # Learning rate schedule.
#     "lr_schedule": None,
#     # Coefficient of the value function loss. IMPORTANT: you must tune this if
#     # you set vf_share_layers=True inside your model's config.
#     "vf_loss_coeff": 1.0,
#     "model": {
#         # Share layers for value function. If you set this to True, it's
#         # important to tune vf_loss_coeff.
#         "vf_share_layers": False,
#         "use_lstm": True
#     },
#     # Coefficient of the entropy regularizer.
#     "entropy_coeff": 0.0,
#     # Decay schedule for the entropy regularizer.
#     "entropy_coeff_schedule": None,
#     # PPO clip parameter.
#     "clip_param": 0.3,
#     # Clip param for the value function. Note that this is sensitive to the
#     # scale of the rewards. If your expected V is large, increase this.
#     "vf_clip_param": 10000.0,
#     # If specified, clip the global norm of gradients by this amount.
#     "grad_clip": None,
#     # Target value for KL divergence.
#     "kl_target": 0.01,
#     # Whether to rollout "complete_episodes" or "truncate_episodes".
#     "batch_mode": "complete_episodes",
#     # Which observation filter to apply to the observation.
#     "observation_filter": "NoFilter",
#     # Uses the sync samples optimizer instead of the multi-gpu one. This is
#     # usually slower, but you might want to try it if you run into issues with
#     # the default optimizer.
#     "simple_optimizer": False,
#     # Whether to fake GPUs (using CPUs).
#     # Set this to True for debugging on non-GPU machines (set `num_gpus` > 0).
#     "_fake_gpus": False,
#     # Use the connector server to generate experiences.
#     "input": (
#         lambda ioctx: PolicyServerInput(ioctx, args.ip, 55555)
#     ),
#     # Use a single worker process to run the server.
#     "num_workers": 0,
#     # Disable OPE, since the rollouts are coming from online clients.
#     "input_evaluation": [],
#     # "callbacks": MyCallbacks,
#     "env_config": {"sleep": True, "framework": 'tf'},
#     "framework": "tf",
#     "explore": True,
#     "exploration_config": {
#         # The Exploration class to use. In the simplest case, this is the name
#         # (str) of any class present in the `rllib.utils.exploration` package.
#         # You can also provide the python class directly or the full location
#         # of your class (e.g. "ray.rllib.utils.exploration.epsilon_greedy.
#         # EpsilonGreedy").
#         "type": "StochasticSampling",
#         # "sub_exploration": "StochasticSampling"
#         # Add constructor kwargs here (if any).
#     },
# })

# DEFAULT_CONFIG["num_workers"] = 1
# DEFAULT_CONFIG['env'] = UnderlordEnv
# DEFAULT_CONFIG['create_env_on_driver'] = True
# DEFAULT_CONFIG["input"] = lambda ioctx: PolicyServerInput(ioctx, 'localhost', 55555)
# print(DEFAULT_CONFIG)

# ray.init()


ray.init()

print(f"running on: {args.ip}:55555")

trainer = DDPPOTrainer(config=DEFAULT_CONFIG)
# trainer = PPOTrainer(config=DEFAULT_CONFIG, env=UnderlordEnv)

# checkpoint_path = CHECKPOINT_FILE.format(args.run)
# checkpoint_path = "checkpoints/"


# if args.checkpoint:
#     # Attempt to restore from checkpoint, if possible.
#     if os.path.exists(args.checkpoint):
#         print('path FOUND!')
#         print("Restoring from checkpoint path", args.checkpoint)
#         trainer.restore(args.checkpoint)
#     else:
#         print("That path does not exist!")

# Serving and training loop.
i = 0
while True:
    print(pretty_print(trainer.train()))
    print(f"Finished train run #{i + 1}")
    i += 1
    # checkpoint = trainer.save(checkpoint_path)
    # print("Last checkpoint", checkpoint)
