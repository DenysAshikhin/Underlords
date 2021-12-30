import os
import ray
from ray.rllib.agents import with_common_config
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.env import PolicyServerInput
from ray.tune.logger import pretty_print

from ray.rllib.examples.env.random_env import RandomEnv
from gym import spaces
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('-ip', type=str, help='IP of this device')

parser.add_argument('-checkpoint', type=str, help='location of checkpoint to restore from')

args = parser.parse_args()

DEFAULT_CONFIG = with_common_config({
    "gamma": 0.999,
    # Should use a critic as a baseline (otherwise don't use value baseline;
    # required for using GAE).
    "use_critic": True,
    # If true, use the Generalized Advantage Estimator (GAE)
    # with a value function, see https://arxiv.org/pdf/1506.02438.pdf.
    "use_gae": True,
    # The GAE (lambda) parameter.
    "lambda": 0.98,
    # Initial coefficient for KL divergence.
    "kl_coeff": 0.2,    
    # Target value for KL divergence.
    "kl_target": 0.02,
    # Size of batches collected from each worker.
    "rollout_fragment_length": 64,
    # Number of timesteps collected for each SGD round. This defines the size
    # of each SGD epoch.
    "train_batch_size": 32768,
    # Total SGD batch size across all devices for SGD. This defines the
    # minibatch size within each epoch.
    "sgd_minibatch_size": 512,
    # Number of SGD iterations in each outer loop (i.e., number of epochs to
    # execute per train batch).
    "num_sgd_iter": 1,
    # Whether to shuffle sequences in the batch when training (recommended).
    "shuffle_sequences": False,
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

        "fcnet_hiddens": [1280, 1280],
        "fcnet_activation": "relu",
        "use_lstm": True,
        "max_seq_len": 32,
        "lstm_cell_size": 512,
        "lstm_use_prev_action": False
    },
    # Coefficient of the entropy regularizer.
    "entropy_coeff": 0.00005,
    # Decay schedule for the entropy regularizer.
    "entropy_coeff_schedule": None,
    # PPO clip parameter.
    "clip_param": 0.2,
    # Clip param for the value function. Note that this is sensitive to the
    # scale of the rewards. If your expected V is large, increase this.
    "vf_clip_param": 30.0,
    # If specified, clip the global norm of gradients by this amount.
    "grad_clip": None,
    # Whether to rollout "complete_episodes" or "truncate_episodes".
    "batch_mode": "complete_episodes",
    # Which observation filter to apply to the observation.
    "observation_filter": "NoFilter",
    # Uses the sync samples optimizer instead of the multi-gpu one. This is
    # usually slower, but you might want to try it if you run into issues with
    # # the default optimizer.
    "simple_optimizer": True,
    #"reuse_actors": True,
    "num_gpus": 1,
    # Use the connector server to generate experiences.
    "input": (
        lambda ioctx: PolicyServerInput(ioctx, args.ip, 55556)
    ),
    # Use a single worker process to run the server.
    "num_workers": 0,
    # Disable OPE, since the rollouts are coming from online clients.
    "input_evaluation": [],
    # "callbacks": MyCallbacks,
    "env": RandomEnv,
    "env_config": {
    "sleep": True
    },
    "framework": "tf",
    # "eager_tracing": True,
    "explore": True,
    # "exploration_config": {
    #     "type": "Curiosity",  # <- Use the Curiosity module for exploring.
    #     "eta": 0.6,  # Weight for intrinsic rewards before being added to extrinsic ones.
    #     "lr": 0.001,  # Learning rate of the curiosity (ICM) module.
    #     "feature_dim": 1152, # Dimensionality of the generated feature vectors.
    #     # Setup of the feature net (used to encode observations into feature (latent) vectors).
    #     "inverse_net_hiddens": [64, 128], # Hidden layers of the "inverse" model.
    #     "inverse_net_activation": "relu",  # Activation of the "inverse" model.
    #     "forward_net_hiddens": [64, 128],  # Hidden layers of the "forward" model.
    #     "forward_net_activation": "relu",  # Activation of the "forward" model.
    #     "beta": 0.2,  # Weight for the "forward" loss (beta) over the "inverse" loss (1.0 - beta).
    #     # Specify, which exploration sub-type to use (usually, the algo's "default"
    #     # exploration, e.g. EpsilonGreedy for DQN, StochasticSampling for PG/SAC).
    #     "sub_exploration": {
    #         "type": "StochasticSampling",
    #     }
    # },
    "create_env_on_driver": False,
    "log_sys_usage": False,
    # "normalize_actions": False,
    "compress_observations": True
    # Whether to fake GPUs (using CPUs).
    # Set this to True for debugging on non-GPU machines (set `num_gpus` > 0).
    #"_fake_gpus": True,
})

allianceId = 27
heroId = 72
localHeroId = 100
itemId = 70
localItemId = 13
x = 8
y = 5
tier = 6
DEFAULT_CONFIG["env_config"]["observation_space"] = spaces.Tuple(
            (spaces.Discrete(9),  # final position * (if not 0 means game is over!)

             # spaces.Discrete(101),  # health *
             # spaces.Discrete(100),  # gold
             # spaces.Discrete(11),  # level *

             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),

             # spaces.Discrete(99),  # remaining EXP to level up
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),

             # spaces.Discrete(50),  # round
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),

             spaces.Discrete(2),  # locked in
             spaces.Discrete(2),  # punish for locking in this round
             spaces.Discrete(6),  # gamePhase *
             spaces.MultiDiscrete([x, y]),  # heroToMove: x, y coord
             spaces.Discrete(localItemId),  # itemToMove: localID*,
             spaces.Discrete(3),  # reRoll cost
             spaces.Discrete(2),  # rerolled (item)

             # spaces.Discrete(35),  # current round timer
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),

             # below are the store heros
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, tier, allianceId, allianceId, allianceId, tier,
                                   allianceId, allianceId, allianceId, tier, allianceId, allianceId, allianceId, tier,
                                   allianceId, allianceId, allianceId, tier]),
             # below are the bench heroes
             # first the levels of all the heroes
             spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
                        high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]),
                        dtype=np.float32),
             # now the cost of all the heroes
             spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
                        high=np.array([5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]),
                        dtype=np.float32),

             # Alliance composition of units
             spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0, 0, 0]),
                        high=np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                       1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                       1, 1, 1, 1, 1, 1, 1]),
                        dtype=np.float32),


             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             # below are the board heros (11 because 1 is underlord)
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId, localItemId, x, y, 5, 3]),
             # below are underlords to pick (whenever valid) -> underlord ID - specialty
             spaces.MultiDiscrete([5, 3, 5, 3, 5, 3, 5, 3]),
             # below are the items
             spaces.MultiDiscrete([itemId, localItemId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, 4, 5]),
             spaces.MultiDiscrete([itemId, localItemId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, 4, 5]),
             spaces.MultiDiscrete([itemId, localItemId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, 4, 5]),
             spaces.MultiDiscrete([itemId, localItemId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, 4, 5]),
             spaces.MultiDiscrete([itemId, localItemId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, 4, 5]),
             # spaces.MultiDiscrete([itemId, localItemId, 4, 5]), spaces.MultiDiscrete([itemId, localItemId, 4, 5]),
             # below are the items to pick from
             spaces.MultiDiscrete([itemId, itemId, itemId]),
             # below are dicts of other players: slot, health, gold, level, boardUnits (ID, Tier)

             spaces.Discrete(9),
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             spaces.MultiDiscrete([allianceId, allianceId, allianceId,
                                   allianceId, allianceId, allianceId,
                                   allianceId, allianceId, allianceId,
                                   allianceId, allianceId, allianceId,
                                   allianceId, allianceId, allianceId,
                                   allianceId, allianceId, allianceId,
                                   allianceId, allianceId, allianceId,
                                   allianceId, allianceId, allianceId,
                                   allianceId, allianceId, allianceId,
                                   allianceId, allianceId, allianceId]),

             # spaces.Discrete(9),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             # spaces.MultiDiscrete([allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId]),
             #
             # spaces.Discrete(9),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             # spaces.MultiDiscrete([allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId]),
             #
             # spaces.Discrete(9),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             # spaces.MultiDiscrete([allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId]),
             #
             # spaces.Discrete(9),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             # spaces.MultiDiscrete([allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId]),
             #
             # spaces.Discrete(9),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             # spaces.MultiDiscrete([allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId]),
             #
             # spaces.Discrete(9),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
             # spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]), dtype=np.float32),
             # spaces.MultiDiscrete([allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId, allianceId])
             ))
DEFAULT_CONFIG["env_config"]["action_space"] = spaces.MultiDiscrete([7, 8, 5])

ray.init(log_to_driver=False)

#print(f"running on: {args.ip}:44444")

# trainer = DDPPOTrainer(config=DEFAULT_CONFIG)

# trainer = PPOTrainer(config=DEFAULT_CONFIG, env=RandomEnv)
trainer = PPOTrainer

# trainer = PPOTrainer(config=DEFAULT_CONFIG, env=UnderlordEnv)
# trainer = APPOTrainer(config=DEFAULT_CONFIG, env=UnderlordEnv)

# checkpoint_path = CHECKPOINT_FILE.format(args.run)


#checkpoint_path = "checkpointsA/"

#print(args.checkpoint)

#if args.checkpoint:
#    # Attempt to restore from checkpoint, if possible.
#    if os.path.exists(args.checkpoint):
#        print('path FOUND!')
#        print("Restoring from checkpoint path", args.checkpoint)
#        trainer.restore(args.checkpoint)
#    else:
#        print("That path does not exist!")

## Serving and training loop.
#i = 0
#while True:

#   print(pretty_print(trainer.train()))
#   print(f"Finished train run #{i + 1}")
#    i += 1
#    if i % 1 == 0:
#        checkpoint = trainer.save(checkpoint_path)
#        print("Last checkpoint", checkpoint)

from ray import tune
name = "" + args.checkpoint
print(f"Starting: {name}")
tune.run(trainer, 
#resume = True, 
config=DEFAULT_CONFIG, name=name, keep_checkpoints_num = None, checkpoint_score_attr = "episode_reward_mean", max_failures = 1,
#restore="C:\\Users\\ashyk\\ray_results\\GAE_98-Gamma_999\\PPO_RandomEnv_2f211_00000_0_2021-11-28_20-25-06\\checkpoint_000069\\checkpoint-69",
checkpoint_freq = 1, checkpoint_at_end = True)