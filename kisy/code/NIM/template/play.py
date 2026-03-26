import os

from nim import train
from game import start_game


def print_actions_table(ai, max_states=50):
    """
    Print a compact "actions table" from the trained Q-values:
    for each seen state, show the best action and its Q-value.
    """
    # q-table keys: ((pile0, pile1, pile2, pile3), (pile_index, remove_count))
    best_by_state = {}
    for (state, action), q_val in ai.q.items():
        prev = best_by_state.get(state)
        if prev is None or q_val > prev[1]:
            best_by_state[state] = (action, q_val)

    items = sorted(best_by_state.items(), key=lambda x: x[0])
    print(f"\nLearned states in Q-table: {len(best_by_state)}")
    print(f"Showing up to {max_states} states:\n")

    for i, (state, (action, q_val)) in enumerate(items[:max_states], start=1):
        print(f"{i}. state={state} -> action={action}, Q={q_val:.4f}")

    if len(items) > max_states:
        print(f"\n... {len(items) - max_states} more states omitted. Set NIM_POLICY_MAX_STATES to show more.")

if __name__ == "__main__":
    # Train the AI (default: 1000 games, configurable via env var)
    print("START TRAINING \n")
    train_games = int(os.getenv("NIM_TRAIN_GAMES", "1000"))
    ai = train(train_games)
    # Make the AI unexploitable during the actual game by enabling a
    # perfect-play fallback (Nim XOR strategy) in addition to the learned Q-table.
    ai.use_optimal = True

    max_states = int(os.getenv("NIM_POLICY_MAX_STATES", "50"))
    print_actions_table(ai, max_states=max_states)

    # Start the game and play against the trained AI
    print("STARTING THE GAME \n")
    start_game(ai)
