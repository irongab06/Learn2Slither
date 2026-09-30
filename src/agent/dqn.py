import torch.nn as nn

class DQN(nn.Module):
	def __init__(self):
		super().__init__()
		self.layer1 = nn.Linear(500, 128)
		self.layer2 = nn.Linear(128, 128)
		self.output = nn.Linear(128, 4)

	def forward(self, vision):
		x = self.layer1(vision)
		x = nn.functional.relu(x)

		x = self.layer2(x)
		x = nn.functional.relu(x)

		return(self.output(x))

if __name__ == "__main__":
    import torch
    from src.environment.environment import Environment
    from src.state.vision import encode_vision

    env = Environment()
    vision = encode_vision(env.get_state())

    vision_tensor = torch.tensor(vision, dtype=torch.float32)

    network = DQN()
    with torch.no_grad():
        q_values = network(vision_tensor)

    print(q_values)
    print(q_values.shape)