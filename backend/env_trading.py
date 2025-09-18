import numpy as np
import gymnasium as gym
from gymnasium import spaces

class TradingEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, prices, features, initial_cash=10000.0):
        super().__init__()
        self.prices = prices  # np.array of close prices
        self.features = features  # np.array shape [T, F]
        self.initial_cash = initial_cash
        self.action_space = spaces.Discrete(3)  # 0 sell, 1 hold, 2 buy
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(features.shape[1]+1,), dtype=np.float32)
        self.reset()

    def _portfolio_value(self):
        return self.cash + self.shares * self.prices[self.t]

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.t = 0
        self.cash = self.initial_cash
        self.shares = 0.0
        obs = np.concatenate([[self.prices[self.t]], self.features[self.t]])
        return obs, {}

    def step(self, action):
        price = self.prices[self.t]
        if action == 2:  # buy all
            qty = self.cash // price
            self.cash -= qty * price
            self.shares += qty
        elif action == 0:  # sell all
            self.cash += self.shares * price
            self.shares = 0.0

        prev_val = self._portfolio_value()
        self.t += 1
        terminated = self.t >= len(self.prices)-1
        reward = self._portfolio_value() - prev_val
        if not terminated:
            obs = np.concatenate([[self.prices[self.t]], self.features[self.t]])
        else:
            obs = np.zeros_like(np.concatenate([[0.0], self.features[0]]))
        return obs, reward, terminated, False, {}
