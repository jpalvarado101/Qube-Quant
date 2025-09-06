import gymnasium as gym
import numpy as np
class SimpleTradingEnv(gym.Env):
    metadata = {"render.modes": ["human"]}
    def __init__(self, features: np.ndarray, prices: np.ndarray, cost: float =0.0005):
        super().__init__()
        self.features = features
        self.prices = prices
        self.n = len(prices)
        self.step_i = 0
        self.pos = 0 # -1,0,1
        self.cash = 1.0
        self.cost = cost
        self.action_space = gym.spaces.Discrete(3)
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf,shape=(features.shape[1]+1,), dtype=np.float32)
        
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.step_i = 0; self.pos = 0; self.cash = 1.0
        return self._obs(), {}
    
    
    def _obs(self):
        return np.concatenate([self.features[self.step_i],[self.pos]]).astype(np.float32)
    def step(self, action: int):
        prev_price = self.prices[self.step_i]
        self.step_i += 1
        done = self.step_i >= self.n-1
        new_price = self.prices[self.step_i]
        reward = 0.0
        # map action: 0 hold, 1 long, 2 short
        target = {0:self.pos,1:1,2:-1}[action]
        if target != self.pos:
        reward -= self.cost
        self.pos = target
        reward += self.pos * ((new_price/prev_price)-1.0)
        return self._obs(), float(reward), done, False, {}