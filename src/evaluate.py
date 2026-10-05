from src.agent.agent import Agent
from src.environment.environment import Environment


def evaluate(path, sessions=100, max_steps=1000,
             max_steps_without_apple=100):
    if sessions <= 0 or max_steps <= 0:
        raise ValueError("sessions et max_steps doivent etre positifs")

    env = Environment(max_steps_without_apple=max_steps_without_apple)
    agent = Agent()
    agent.load(path)
    agent.epsilon = 0.0
    agent.network.eval()
    results = []

    for session in range(sessions):
        env.reset()
        done = False
        steps = 0
        max_length = len(env.snake.body)

        while not done and steps < max_steps:
            state = env.get_state()
            action = agent.choose_action(state)
            reward, done = env.step(action)
            steps += 1
            max_length = max(max_length, len(env.snake.body))

        final_length = len(env.snake.body)
        limited = not done
        results.append((steps, max_length, final_length, limited))
        status = "limite de mouvements" if limited else "partie terminee"
        print(
            f"Partie {session + 1}/{sessions} "
            f"- mouvements : {steps} "
            f"- longueur max : {max_length} "
            f"- longueur finale : {final_length} "
            f"- {status}"
        )

    average_steps = sum(result[0] for result in results) / sessions
    average_length = sum(result[2] for result in results) / sessions
    best_length = max(result[1] for result in results)
    limited_games = sum(result[3] for result in results)
    print(
        f"Bilan - mouvements moyens : {average_steps:.1f} "
        f"- longueur finale moyenne : {average_length:.1f} "
        f"- longueur max : {best_length} "
        f"- parties limitees : {limited_games}/{sessions}"
    )
    return results


if __name__ == "__main__":
    evaluate("models/2000_sessions.pth")
