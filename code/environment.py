from gym import spaces
import gym

from tkinter import Frame, Tk, Label

from ray.rllib.agents.ppo import DDPPOTrainer, ppo
from ray.tune import register_env

from ray import tune

from ray.rllib.utils.typing import EnvActionType, EnvObsType, EnvInfoDict
import threading
import uuid
from typing import Optional

from botVision import UnderlordInteract
from six.moves import queue
import ray
from ray import serve

import requests
import logging
import threading
import time
from typing import Union, Optional

import ray.cloudpickle as pickle
from ray.rllib.env import ExternalEnv, MultiAgentEnv, ExternalMultiAgentEnv
from ray.rllib.policy.sample_batch import MultiAgentBatch
from ray.rllib.utils.annotations import PublicAPI
from ray.rllib.utils.typing import MultiAgentDict, EnvInfoDict, EnvObsType, EnvActionType


class UnderlordEnv(ExternalEnv):

    def __init__(self, config=None):

        threading.Thread.__init__(self)

        print(config)
        if config is not None:
            if 'sleep' in config:
                self.sleep = config['sleep']
            else:
                self.sleep = False
        else:
            self.sleep = False

        self.daemon = True
        # self.action_space = action_space
        # note to make sure 0's are reserved for n/a -> adding +1 to some values ( marked with a *)
        self.observation_space = spaces.Tuple(
            (spaces.Discrete(9),  # final position * (if not 0 means game is over!)
             spaces.Discrete(101),  # health *
             spaces.Discrete(100),  # gold
             spaces.Discrete(11),  # level *
             spaces.Discrete(99),  # remaining EXP to level up
             spaces.Discrete(50),  # round
             spaces.Discrete(2),  # locked in
             spaces.Discrete(6),  # gamePhase *
             spaces.MultiDiscrete([500, 3]),  # heroToMove: heroLocalID, isUnderlord
             spaces.Discrete(500),  # itemToMove: localID*,
             spaces.Discrete(3),  # reRoll cost
             spaces.Discrete(2),  # rerolled (item)
             # below are the store heros
             spaces.MultiDiscrete([1006, 1006, 1006, 1006, 1006]),
             # below are the bench heroes
             spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]), spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]),
             spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]), spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]),
             spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]), spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]),
             spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]), spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]),
             # below are the board heros
             spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]), spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]),
             spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]), spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]),
             spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]), spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]),
             spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]), spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]),
             spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]), spaces.MultiDiscrete([1006, 500, 4, 6, 500, 9, 9, 3]),
             # below are underlords to pick (whenever valid) -> underlord ID - specialty
             spaces.MultiDiscrete([5, 3, 5, 3, 5, 3, 5, 3, ]),
             # below are the items
             spaces.MultiDiscrete([10220, 500, 500, 4, 5]), spaces.MultiDiscrete([10220, 500, 500, 4, 5]),
             spaces.MultiDiscrete([10220, 500, 500, 4, 5]), spaces.MultiDiscrete([10220, 500, 500, 4, 5]),
             spaces.MultiDiscrete([10220, 500, 500, 4, 5]), spaces.MultiDiscrete([10220, 500, 500, 4, 5]),
             spaces.MultiDiscrete([10220, 500, 500, 4, 5]), spaces.MultiDiscrete([10220, 500, 500, 4, 5]),
             spaces.MultiDiscrete([10220, 500, 500, 4, 5]), spaces.MultiDiscrete([10220, 500, 500, 4, 5]),
             spaces.MultiDiscrete([10220, 500, 500, 4, 5]), spaces.MultiDiscrete([10220, 500, 500, 4, 5]),
             # below are the items to pick from
             spaces.MultiDiscrete([10220, 10220, 10220]))
        )

        self.action_space = spaces.MultiDiscrete(
            [  # 0=reroll, 1 = lock in, 2 = level up, 3 = buy unit from store, 4 = sell unit, 5 = choose item,
                # 6 = choose underlord, 7 = move Unit, 8 = move Item
                9,
                9,  # x-cordinate *
                9,  # y-cordinate *
                4,  # selection -> used only when having to choose an item or underlord
            ]
        )
        self._episodes = {}
        self._finished = set()
        self._results_avail_condition = threading.Condition()
        self._max_concurrent_episodes = 3  # maybe maybe not, no clue lmao

        self.root = Tk()
        self.root.resizable(0, 0)
        self.underlord = UnderlordInteract(self.root)
        # self.root.update()
        # root.mainloop()
        print('got past main loop')

    def run(self):  # if I can't get this to work, try not overriding it in the first place?
        """Override this to implement the run loop.
        Your loop should continuously:
            1. Call self.start_episode(episode_id)
            2. Call self.get_action(episode_id, obs)
                    -or-
                    self.log_action(episode_id, obs, action)
            3. Call self.log_returns(episode_id, reward)
            4. Call self.end_episode(episode_id, obs)
            5. Wait if nothing to do.
        Multiple episodes may be started at the same time.
        """

        if self.sleep:
            time.sleep(999999)

        episode_id = None
        episode_id = self.start_episode(episode_id=episode_id)
        while True:  # not sure if it should be a literal loop..........?
            gameObservation = self.underlord.getObservation()
            self.root.update()

            action = self.get_action(episode_id=episode_id, observation=gameObservation)

            reward = self.underlord.act(action=action[0], x=action[1], y=action[2], selection=action[3])
            self.log_returns(episode_id=episode_id, reward=reward)

            if self.underlord.finished() != -1:
                self.end_episode(episode_id=episode_id, observation=gameObservation)
                episode_id = self.start_episode(episode_id=None)

    def start_episode(self,
                      episode_id: Optional[str] = None,
                      training_enabled: bool = True) -> str:
        """Record the start of an episode.
        Args:
            episode_id (Optional[str]): Unique string id for the episode or
                None for it to be auto-assigned and returned.
            training_enabled (bool): Whether to use experiences for this
                episode to improve the policy.
        Returns:
            episode_id (str): Unique string id for the episode.
        """

        if episode_id is None:
            episode_id = uuid.uuid4().hex
            self.underlord.startNewGame()

        if episode_id in self._finished:
            raise ValueError(
                "Episode {} has already completed.".format(episode_id))

        if episode_id in self._episodes:
            raise ValueError(
                "Episode {} is already started".format(episode_id))

        self._episodes[episode_id] = _ExternalEnvEpisode(
            episode_id, self._results_avail_condition, training_enabled)

        return episode_id

    def get_action(self, episode_id: str,
                   observation: EnvObsType) -> EnvActionType:
        """Record an observation and get the on-policy action.
        Args:
            episode_id (str): Episode id returned from start_episode().
            observation (obj): Current environment observation.
        Returns:
            action (obj): Action from the env action space.
        """

        episode = self._get(episode_id)
        return episode.wait_for_action(observation)

    def log_returns(self,
                    episode_id: str,
                    reward: float,
                    info: EnvInfoDict = None) -> None:
        """Record returns from the environment.
        The reward will be attributed to the previous action taken by the
        episode. Rewards accumulate until the next action. If no reward is
        logged before the next action, a reward of 0.0 is assumed.
        Args:
            episode_id (str): Episode id returned from start_episode().
            reward (float): Reward from the environment.
            info (dict): Optional info dict.
        """

        episode = self._get(episode_id)
        episode.cur_reward += reward

        if info:
            episode.cur_info = info or {}

    def end_episode(self, episode_id: str, observation: EnvObsType) -> None:
        """Record the end of an episode.
        Args:
            episode_id (str): Episode id returned from start_episode().
            observation (obj): Current environment observation.
        """

        self.underlord.returnToMainScreen()
        episode = self._get(episode_id)
        self._finished.add(episode.episode_id)
        episode.done(observation)

    def _get(self, episode_id: str) -> "_ExternalEnvEpisode":
        """Get a started episode or raise an error."""

        if episode_id in self._finished:
            raise ValueError(
                "Episode {} has already completed.".format(episode_id))

        if episode_id not in self._episodes:
            raise ValueError("Episode {} not found.".format(episode_id))

        return self._episodes[episode_id]


class _ExternalEnvEpisode:
    """Tracked state for each active episode."""

    def __init__(self,
                 episode_id: str,
                 results_avail_condition: threading.Condition,
                 training_enabled: bool,
                 multiagent: bool = False):

        self.episode_id = episode_id
        self.results_avail_condition = results_avail_condition
        self.training_enabled = training_enabled
        self.multiagent = multiagent
        self.data_queue = queue.Queue()
        self.action_queue = queue.Queue()
        if multiagent:
            self.new_observation_dict = None
            self.new_action_dict = None
            self.cur_reward_dict = {}
            self.cur_done_dict = {"__all__": False}
            self.cur_info_dict = {}
        else:
            self.new_observation = None
            self.new_action = None
            self.cur_reward = 0.0
            self.cur_done = False
            self.cur_info = {}

    def get_data(self):
        if self.data_queue.empty():
            return None
        return self.data_queue.get_nowait()

    def log_action(self, observation, action):
        if self.multiagent:
            self.new_observation_dict = observation
            self.new_action_dict = action
        else:
            self.new_observation = observation
            self.new_action = action
        self._send()
        self.action_queue.get(True, timeout=60.0)

    def wait_for_action(self, observation):
        if self.multiagent:
            self.new_observation_dict = observation
        else:
            self.new_observation = observation
        self._send()
        return self.action_queue.get(True, timeout=60.0)

    def done(self, observation):
        if self.multiagent:
            self.new_observation_dict = observation
            self.cur_done_dict = {"__all__": True}
        else:
            self.new_observation = observation
            self.cur_done = True
        self._send()

    def _send(self):
        if self.multiagent:
            if not self.training_enabled:
                for agent_id in self.cur_info_dict:
                    self.cur_info_dict[agent_id]["training_enabled"] = False
            item = {
                "obs": self.new_observation_dict,
                "reward": self.cur_reward_dict,
                "done": self.cur_done_dict,
                "info": self.cur_info_dict,
            }
            if self.new_action_dict is not None:
                item["off_policy_action"] = self.new_action_dict
            self.new_observation_dict = None
            self.new_action_dict = None
            self.cur_reward_dict = {}
        else:
            item = {
                "obs": self.new_observation,
                "reward": self.cur_reward,
                "done": self.cur_done,
                "info": self.cur_info,
            }
            if self.new_action is not None:
                item["off_policy_action"] = self.new_action
            self.new_observation = None
            self.new_action = None
            self.cur_reward = 0.0
            if not self.training_enabled:
                item["info"]["training_enabled"] = False

        with self.results_avail_condition:
            self.data_queue.put_nowait(item)
            self.results_avail_condition.notify()
