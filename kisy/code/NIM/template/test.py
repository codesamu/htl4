from nim import NimAI


def test_get_q_value(ai):
    print("\n--- Testing get_q_value ---")
    
    state = (0, 0, 0, 2)
    action = (3, 2)
    
    value = ai.get_q_value(state, action)
    print(f"Q-value for {state}, {action}: {value}")
    # Erwartet: -1 (laut init)


def test_update_q_value(ai):
    print("\n--- Testing update_q_value ---")
    
    state = [2, 1, 1, 0]
    action = (0, 1)
    
    old_q = 0.2
    reward = 1
    future_q = 0.8

    ai.update_q_value(state, action, old_q, reward, future_q)

    new_value = ai.get_q_value(state, action)
    print(f"Updated Q-value: {new_value}")
    # Erwartet: 1.0


def test_best_future_reward(ai):
    print("\n--- Testing best_future_reward ---")
    
    state = [1, 1, 1, 0]

    # Manuelle Q-Werte setzen
    ai.q[(tuple(state), (0, 1))] = 0.4
    ai.q[(tuple(state), (1, 1))] = 0.9
    ai.q[(tuple(state), (2, 1))] = 0.7

    result = ai.best_future_reward(state)
    print(f"Best future reward for {state}: {result}")
    # Erwartet: 0.9


def test_choose_action(ai):
    print("\n--- Testing choose_action ---")
    
    state = [0, 0, 0, 2]

    # Nutzt deine Testwerte aus __init__
    action = ai.choose_action(state, epsilon=False)

    print(f"Chosen action (greedy): {action}")
    # Erwartet: (3,1), weil Q=10 > -1

    # Test mit Exploration
    action_random = ai.choose_action(state, epsilon=True)
    print(f"Chosen action (epsilon): {action_random}")


if __name__ == "__main__":
    ai = NimAI()

    test_get_q_value(ai)
    test_update_q_value(ai)
    test_best_future_reward(ai)
    test_choose_action(ai)

    print("\nAll tests completed.")
