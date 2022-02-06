from gym.spaces import Box, Dict, Discrete, MultiDiscrete
import numpy as np

from ray.rllib.examples.env.random_env import RandomEnv


class ActionMaskEnv(RandomEnv):
    """A randomly acting environment that publishes an action-mask each step."""

    def __init__(self, config):
        super().__init__(config)
        print("Init triggered")

        # Masking only works for Discrete actions.
        assert isinstance(self.action_space, MultiDiscrete)
        print("Asset Raised")
        # Add action_mask to observations.
        self.observation_space = Dict(
            {
                "action_mask": Box(low=np.array([0]), high=np.array([1]), dtype=np.float32),
                "observations": self.observation_space,
            }
        )
        print(self.observation_space)
        print("Obs dict init")
        self.valid_actions = None

    def reset(self):
        obs = super().reset()
        print ("reset triggered")
        self._fix_action_mask(obs)
        print("Fixed action")
        return obs

    def step(self, action):
        print("Step triggere")
        # Check whether action is valid.
        if not self.valid_actions[action]:
            print("Invalaid action")
            raise ValueError(
                f"Invalid action sent to env! " f"valid_actions={self.valid_actions}"
            )

        print("Valid action")
        obs, rew, done, info = super().step(action)

        print("Obs stepped")
        self._fix_action_mask(obs)
        print("action mask applied")
        return obs, rew, done, info

    def _fix_action_mask(self, obs):
        # Fix action-mask: Everything larger 0.5 is 1.0, everything else 0.0.
        print("dddd")
        self.valid_actions = np.round(obs["action_mask"])
        obs["action_mask"] = self.valid_actions