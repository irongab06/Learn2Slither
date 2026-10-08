from src.environment.environment import Environment


def run_sessions(sessions, agent, learn=True, grid_size=10):
    env = Environment(
        grid_size,
        max_steps_without_apple=grid_size * grid_size,
    )
    final_lengths = []
    best_length = 0
    best_session = 0
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
            if learn:
                agent.remember(state, action, reward, next_state, done)
                agent.train_step()
                agent.decay_epsilon()
            state = next_state
        print(
            f"Game over, final length = {len(env.snake.body)}, "
            f"max length = {max_length}, max duration = {steps}"
        )
        final_length = len(env.snake.body)
        final_lengths.append(final_length)
        if final_length > best_length:
            best_length = final_length
            best_session = session + 1
        print(
            f"Partie {session + 1}/{sessions} "
            f"- mouvements : {steps} "
            f"- longueur max : {max_length} "
            f"- mises a jour : {agent.training_steps} "
            f"- epsilon : {agent.epsilon:.3f}"
        )
    total = 0
    nb_35 = 0
    for length in final_lengths:
        total += length
        if length >= 35:
            nb_35 += 1
    print(
        f"Meilleure partie : n° {best_session} "
        f"avec une longueur finale de {best_length}"
    )
    print(f"Longueur finale moyenne : {total / len(final_lengths):.1f}")
    print(f"Parties >= 35 : {nb_35} sur {len(final_lengths)}")
