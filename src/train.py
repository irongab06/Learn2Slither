from src.environment.environment import Environment
from src.agent.agent import Agent

def train(sessions) :
	env = Environment()
	agent = Agent()
	for session in range(sessions):
		env.reset()
		done = False
		state = env.get_state()
		steps = 0
		max_length = len(env.snake.body)
		while not done:
			action = agent.choose_action(state)
			reward, done = env.step(action)
			steps += 1
			max_length = max(max_length, len(env.snake.body))

			if done:
				next_state = None
			else:
				next_state = env.get_state()

			agent.remember(state, action, reward, next_state, done)
			agent.train_step()
			state = next_state
		agent.decay_epsilon()
		print(
			f"Partie {session + 1}/{sessions} "
			f"- mouvements : {steps} "
			f"- longueur max : {max_length} "
			f"- mises a jour : {agent.training_steps} "
			f"- epsilon : {agent.epsilon:.3f}"
		)
	agent.save(f"models/{sessions}_sessions.pth")

if __name__ == "__main__":
    train(100)
