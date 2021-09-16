import os
import ray
from ray.rllib.agents import with_common_config
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.env import PolicyServerInput

from ray.rllib.examples.env.random_env import RandomEnv
from gym import spaces

DEFAULT_CONFIG = with_common_config({
    # Should use a critic as a baseline (otherwise don't use value baseline;
    # required for using GAE).
    "use_critic": True,
    # If true, use the Generalized Advantage Estimator (GAE)
    # with a value function, see https://arxiv.org/pdf/1506.02438.pdf.
    "use_gae": True,
    # The GAE (lambda) parameter.
    "lambda": 1.0,
    # Initial coefficient for KL divergence.
    "kl_coeff": 0.2,
    # Size of batches collected from each worker.
    "rollout_fragment_length": 20,
    # Number of timesteps collected for each SGD round. This defines the size
    # of each SGD epoch.
    "train_batch_size": 5000,
    # Total SGD batch size across all devices for SGD. This defines the
    # minibatch size within each epoch.
    "sgd_minibatch_size": 200,
    # Number of SGD iterations in each outer loop (i.e., number of epochs to
    # execute per train batch).
    "num_sgd_iter": 25,
    # Whether to shuffle sequences in the batch when training (recommended).
    "shuffle_sequences": True,
    # Stepsize of SGD.
    "lr": 3e-5,
    # Learning rate schedule.
    "lr_schedule": None,
    # Coefficient of the value function loss. IMPORTANT: you must tune this if
    # you set vf_share_layers=True inside your model's config.
    "vf_loss_coeff": 1.0,
    "model": {
        # Share layers for value function. If you set this to True, it's
        # important to tune vf_loss_coeff.
        "vf_share_layers": False,
        "fcnet_hiddens": [56, 56],
        "use_lstm": False
        # "max_seq_len": 3,
    },
    # Coefficient of the entropy regularizer.
    "entropy_coeff": 0.0,
    # Decay schedule for the entropy regularizer.
    "entropy_coeff_schedule": None,
    # PPO clip parameter.
    "clip_param": 0.3,
    # Clip param for the value function. Note that this is sensitive to the
    # scale of the rewards. If your expected V is large, increase this.
    "vf_clip_param": 50000.0,
    # If specified, clip the global norm of gradients by this amount.
    "grad_clip": None,
    # Target value for KL divergence.
    "kl_target": 0.01,
    # Whether to rollout "complete_episodes" or "truncate_episodes".
    "batch_mode": "complete_episodes",
    # Which observation filter to apply to the observation.
    "observation_filter": "NoFilter",
    # Uses the sync samples optimizer instead of the multi-gpu one. This is
    # usually slower, but you might want to try it if you run into issues with
    # # the default optimizer.
    # "simple_optimizer": False,
    # Whether to fake GPUs (using CPUs).
    # Set this to True for debugging on non-GPU machines (set `num_gpus` > 0).
    # "_fake_gpus": True,
    "num_gpus": 1,
    # Use the connector server to generate experiences.
    "input": (
        lambda ioctx: PolicyServerInput(ioctx, '127.0.0.1', 55558)
    ),
    # Use a single worker process to run the server.
    "num_workers": 0,
    # Disable OPE, since the rollouts are coming from online clients.
    "input_evaluation": [],
    # "callbacks": MyCallbacks,
    "env_config": {"sleep": True,},
    "framework": "tf",
    # "eager_tracing": True,
    "explore": True,
    "exploration_config": {
        "type": "Curiosity",  # <- Use the Curiosity module for exploring.
        "eta": 1.0,  # Weight for intrinsic rewards before being added to extrinsic ones.
        "lr": 0.001,  # Learning rate of the curiosity (ICM) module.
        "feature_dim": 512,  # Dimensionality of the generated feature vectors.
        # Setup of the feature net (used to encode observations into feature (latent) vectors).
        "inverse_net_hiddens": [64],  # Hidden layers of the "inverse" model.
        "inverse_net_activation": "relu",  # Activation of the "inverse" model.
        "forward_net_hiddens": [64],  # Hidden layers of the "forward" model.
        "forward_net_activation": "relu",  # Activation of the "forward" model.
        "beta": 0.2,  # Weight for the "forward" loss (beta) over the "inverse" loss (1.0 - beta).
        # Specify, which exploration sub-type to use (usually, the algo's "default"
        # exploration, e.g. EpsilonGreedy for DQN, StochasticSampling for PG/SAC).
        "sub_exploration": {
            "type": "StochasticSampling",
        }
    },
    "create_env_on_driver": False,
    "log_sys_usage": False,
    "normalize_actions": False
    # "compress_observations": True

})

heroId = 72
DEFAULT_CONFIG["env_config"]["observation_space"] = spaces.Tuple(
            (spaces.Discrete(9),  # final position * (if not 0 means game is over!)
             spaces.Discrete(101),  # health *
             spaces.Discrete(100),  # gold
             spaces.Discrete(11),  # level *
             spaces.Discrete(99),  # remaining EXP to level up
             spaces.Discrete(50),  # round
             spaces.Discrete(2),  # locked in
             spaces.Discrete(2),  # punish for locking in this round
             spaces.Discrete(6),  # gamePhase *
             spaces.MultiDiscrete([250, 3]),  # heroToMove: heroLocalID, isUnderlord
             spaces.Discrete(250),  # itemToMove: localID*,
             spaces.Discrete(3),  # reRoll cost
             spaces.Discrete(2),  # rerolled (item)
             spaces.Discrete(35),  # current round timer
             # below are the store heros
             spaces.MultiDiscrete([heroId, heroId, heroId, heroId, heroId]),
             # below are the bench heroes
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             # below are the board heros
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
             spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]), spaces.MultiDiscrete([heroId, 250, 4, 6, 14, 9, 9, 3]),
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
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4]),
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4]),
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4]),
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4]),
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4]),
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4]),
             spaces.MultiDiscrete(
                 [9, 101, 100, 11, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4, heroId, 4])
             ))
DEFAULT_CONFIG["env_config"]["action_space"] = spaces.MultiDiscrete([7, 9, 9])

ray.init()
trainer = PPOTrainer(config=DEFAULT_CONFIG, env=RandomEnv)
trainer2 = PPOTrainer(config=DEFAULT_CONFIG, env=RandomEnv)

checkpoint_path = "checkpoints/"
checkpoint1 = "checkpoint_000001/checkpoint-1"
fullpath1 = checkpoint_path + checkpoint1

checkpoint2 = "checkpoint_000005/checkpoint-5"
fullpath2 = checkpoint_path + checkpoint2

sum1a = 0
sum1b = 0
sum2a = 0
sum2b = 0


if os.path.exists(fullpath1):
    print('path FOUND!')
    print("Restoring from checkpoint path", fullpath1)
    trainer.restore(fullpath1)
    temp = trainer.get_policy().model._curiosity_feature_net
    sum1a = sum(v.sum() for k, v in trainer.get_policy().get_weights().items())
    sum1b = sum(
        v.eval(trainer.get_policy()._sess).sum() for v in trainer.get_policy().model._curiosity_feature_net.variables())
else:
    print("That path does not exist!")


if os.path.exists(fullpath2):
    print('path FOUND!')
    print("Restoring from checkpoint path", fullpath2)
    trainer2.restore(fullpath2)
    sum2a = sum(v.sum() for k, v in trainer2.get_policy().get_weights().items())
    sum2b = sum(
        v.eval(trainer2.get_policy()._sess).sum() for v in trainer2.get_policy().model._curiosity_feature_net.variables())
else:
    print("That path does not exist!")

print("TF")
print(sum1a, " , ", sum2a)
print(sum1b, " , ", sum2b)
import numpy as np

print("All weights isclose?: ", np.isclose(sum1a, sum2a))
print("Curiosity_feature_net weights isclose?: ", np.isclose(sum1b, sum2b))
