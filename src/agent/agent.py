import random
from collections import deque
from pathlib import Path

import torch

from src.agent.dqn import DQN
from src.state.vision import encode_vision


class Agent:
	def __init__(self):
		self.network = DQN()
		self.target_network = DQN()
		self.target_network.load_state_dict(self.network.state_dict())
		self.actions = ["up", "down", "left", "right"]
		self.epsilon = 1.0
		self.epsilon_min = 0.01
		self.epsilon_decay_steps = 30000
		self.exploration_steps = 0
		self.memory = deque(maxlen=100000)
		self.batch_size = 64
		self.gamma = 0.99
		self.training_steps = 0
		self.target_update_interval = 100
		self.loss_function = torch.nn.SmoothL1Loss()
		self.optimizer = torch.optim.Adam(
			self.network.parameters(),
			lr=0.0005,
		)

	def choose_action(self, vision):
		if random.random() < self.epsilon:
			return random.choice(self.actions)

		encoded_vision = encode_vision(vision)
		vision_tensor = torch.tensor(encoded_vision, dtype=torch.float32)
		with torch.no_grad():
			q_values = self.network(vision_tensor)
		action_index = torch.argmax(q_values).item()
		return self.actions[action_index]

	def decay_epsilon(self):
		self.exploration_steps += 1
		progression = self.exploration_steps / self.epsilon_decay_steps
		if progression > 1.0:
			progression = 1.0
		self.epsilon = 1.0 - progression * (1.0 - self.epsilon_min)

	def remember(self, state, action, reward, next_state, done):
		experience = (state, action, reward, next_state, done)
		self.memory.append(experience)

	def save(self, path, with_memory=False):
		path = Path(path)
		path.parent.mkdir(parents=True, exist_ok=True)
		checkpoint = {
			"network": self.network.state_dict(),
			"target_network": self.target_network.state_dict(),
			"optimizer": self.optimizer.state_dict(),
			"epsilon": self.epsilon,
			"epsilon_min": self.epsilon_min,
			"epsilon_decay_steps": self.epsilon_decay_steps,
			"exploration_steps": self.exploration_steps,
			"training_steps": self.training_steps,
			"target_update_interval": self.target_update_interval,
			"batch_size": self.batch_size,
			"gamma": self.gamma,
			"actions": self.actions,
			"memory_capacity": self.memory.maxlen,
		}
		if with_memory:
			checkpoint["memory"] = list(self.memory)
		torch.save(checkpoint, path)

	def load(self, path):
		checkpoint = torch.load(path, map_location="cpu", weights_only=True)
		self.network.load_state_dict(checkpoint["network"])
		self.target_network.load_state_dict(checkpoint["target_network"])
		self.optimizer.load_state_dict(checkpoint["optimizer"])
		self.epsilon = checkpoint["epsilon"]
		self.epsilon_min = checkpoint.get("epsilon_min", self.epsilon_min)
		self.epsilon_decay_steps = checkpoint.get(
			"epsilon_decay_steps",
			self.epsilon_decay_steps,
		)
		self.exploration_steps = checkpoint.get("exploration_steps", 0)
		self.training_steps = checkpoint["training_steps"]
		self.target_update_interval = checkpoint["target_update_interval"]
		self.batch_size = checkpoint["batch_size"]
		self.gamma = checkpoint["gamma"]
		self.actions = checkpoint["actions"]
		if "memory" in checkpoint:
			self.memory = deque(
				checkpoint["memory"],
				maxlen=checkpoint.get("memory_capacity", self.memory.maxlen),
			)

	def train_step(self):
		if len(self.memory) < self.batch_size:
			return

		batch = random.sample(list(self.memory), self.batch_size)
		states = []
		actions = []
		next_states = []
		rewards = []
		dones = []
		for state, action, reward, next_state, done in batch:
			states.append(encode_vision(state))
			actions.append(self.actions.index(action))
			rewards.append(reward)
			if done:
				next_states.append([0.0] * 500)
			else:
				next_states.append(encode_vision(next_state))
			dones.append(done)

		vision_tensor = torch.tensor(states, dtype=torch.float32)

		next_vision_tensor = torch.tensor(next_states, dtype=torch.float32)

		actions_tensor = torch.tensor(actions, dtype=torch.long)

		rewards_tensor = torch.tensor(rewards, dtype=torch.float32)

		dones_tensor = torch.tensor(dones, dtype=torch.bool)

		q_values = self.network(vision_tensor)

		rows = torch.arange(len(batch))

		chosen_q_values = q_values[rows, actions_tensor]

		with torch.no_grad():
			# Double DQN : le reseau principal choisit l'action,
			# le reseau cible donne sa valeur.
			next_q_values = self.network(next_vision_tensor)
			best_actions = next_q_values.argmax(dim=1)
			target_q_values = self.target_network(next_vision_tensor)
			best_next_q_values = target_q_values[rows, best_actions]
			best_next_q_values[dones_tensor] = 0.0
			targets = rewards_tensor + self.gamma * best_next_q_values

		loss = self.loss_function(chosen_q_values, targets)
		self.optimizer.zero_grad()
		loss.backward()
		self.optimizer.step()
		self.training_steps += 1

		if self.training_steps % self.target_update_interval == 0:
			self.target_network.load_state_dict(self.network.state_dict())
