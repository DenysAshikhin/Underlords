from gym import spaces
import numpy as np

heroId = 72
allianceId = 27
localHeroId = 100
itemId = 70
localItemId = 13
x = 8
y = 5
underlordsId = 9
tier = 6

spacef = spaces.Tuple(
    (spaces.Discrete(9),  # final position * (if not 0 means game is over!)


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
     spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]),
                dtype=np.float32),
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
     # Coords of the enemy units
     spaces.MultiDiscrete([8, 4,
                           8, 4,
                           8, 4,
                           8, 4,
                           8, 4,
                           8, 4,
                           8, 4,
                           8, 4,
                           8, 4,
                           8, 4]),
     ))



def find_shape(obs):
    n = 0
    k = 0
    for i in obs:
        k += 1
        if isinstance(i, spaces.Box):
            n += i.shape[0]
        elif isinstance(i, spaces.Discrete):
            n += i.n
        elif isinstance(i, spaces.MultiDiscrete):
            n += i.nvec.sum()
        else:
            raise TypeError

    return k,n


import tensorflow as tf
import numpy as np
tf.compat.v1.disable_eager_execution()

t1 = tf.compat.v1.placeholder (tf.float32, [None, 400])
t2 = tf.compat.v1.placeholder (tf.float32, [None, 1176])
t4 = tf.compat.v1.placeholder (tf.float32, [None, 2176])
t = [t1, t2, t4]
print(t)
t3 = tf.concat([t1, t2, t4], axis = -1)


with tf.compat.v1.Session() as sess:
    sess.run(tf.compat.v1.global_variables_initializer())
    t3_val = sess.run(t3, feed_dict = {t1: np.ones((300, 400)), t2: np.ones((300, 1176)), t4: np.ones((300,2176))})

    print(t3_val.shape)
    # (300, 1576)
