import random
from collections import deque

import torch

from src.agent.dqn import DQN
from src.state.vision import encode_vision


class Agent:
	def __init__(self):
		self.network = DQN()
		self.actions = ["up", "down", "left", "right"]
		self.epsilon = 1.0
		self.memory = deque(maxlen=10000)
		self.batch_size = 64

	def choose_action(self, vision):
		if random.random() < self.epsilon:
			return random.choice(self.actions)

		encoded_vision = encode_vision(vision)
		vision_tensor = torch.tensor(encoded_vision, dtype=torch.float32)
		with torch.no_grad():
			q_values = self.network(vision_tensor)
		action_index = torch.argmax(q_values).item()
		return self.actions[action_index]

	def remember(self, state, action, reward, next_state, done):
		experience = (state, action, reward, next_state, done)
		self.memory.append(experience)

	def train_step(self):
		if len(self.memory) < self.batch_size:
			return

		batch = random.sample(list(self.memory), self.batch_size)
		states = []
		actions = []

		for state, action, reward, next_state, done in batch:
			states.append(encode_vision(state))
			actions.append(self.actions.index(action))
