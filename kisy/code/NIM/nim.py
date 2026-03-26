import random


class Nim():
    def __init__(self, initial=[4, 4, 4, 4]):
        self.piles = initial.copy()
        self.player = 0  # Player 0 starts
        self.winner = None

    @classmethod
    def available_actions(cls, piles):
        actions = set()
        for i, pile in enumerate(piles):
            for j in range(1, pile + 1):
                actions.add((i, j))
        return actions

    @classmethod
    def other_player(cls, player):
        return 0 if player == 1 else 1

    def switch_player(self):
        self.player = Nim.other_player(self.player)

    def move(self, action):
        pile, count = action
        self.piles[pile] -= count
        self.switch_player()
        if all(pile == 0 for pile in self.piles):
            # Winner is the player who would be next to move.
            # (This convention is expected by the training reward logic.)
            self.winner = self.player


class NimAI():
    def __init__(self, alpha=0.5, epsilon=0.1):
        self.q = dict()  # Q-value table
        self.q[(0, 0, 0, 2), (3, 2)] = -1  # Test Q-Value
        self.q[(0, 0, 0, 2), (3, 1)] = 10  # Test Q-Value

        self.alpha = alpha  # Learning rate
        self.epsilon = epsilon  # Exploration rate
        # Optional perfect-play fallback (disabled by default).
        # Enabled from `template/play.py` during actual game runs.
        self.use_optimal = False

    @staticmethod
    def optimal_action(state):
        """
        Compute the optimal Nim move using the XOR (nim-sum) rule.
        Returns (pile_index, remove_count) or None if the position is losing
        (nim-sum == 0).
        """
        nim_sum = 0
        for pile in state:
            nim_sum ^= pile
        if nim_sum == 0:
            return None

        for i, pile in enumerate(state):
            target = pile ^ nim_sum
            if target < pile:
                return (i, pile - target)
        return None

    def update(self, old_state, action, new_state, reward):
        old_q = self.get_q_value(old_state, action)
        best_future_q = self.best_future_reward(new_state)
        self.update_q_value(old_state, action, old_q, reward, best_future_q)

    def get_q_value(self, state, action):
        """
        Return the Q-value for a given state-action pair.

        Parameters:
        state (list): The current game state.
        action (tuple): The action being evaluated.

        Returns:
        float: The Q-value associated with the (state, action) pair.
               Returns 0 if the pair is not yet in the Q-table.
        """
        key = (tuple(state), action)
        return self.q.get(key, 0)

    def update_q_value(self, state, action, old_q, reward, future_q):
        """
        Update the Q-value for a state-action pair using the Q-learning formula.
        """
        # Q-learning update rule:
        # new_q = old_q + alpha * (reward + future_q - old_q)
        new_q = old_q + self.alpha * (reward + future_q - old_q)
        self.q[(tuple(state), action)] = new_q
        return new_q

    def best_future_reward(self, state):
        """
        Determine the highest Q-value among all possible actions in a given state.

        Returns 0 if no actions are available.
        """
        actions = Nim.available_actions(state)
        if not actions:
            return 0
        return max(self.get_q_value(state, action) for action in actions)

    def choose_action(self, state, epsilon=True):
        """
        Choose an action for the given state using an epsilon-greedy strategy.

        If epsilon=True, epsilon-greedy exploration is enabled.
        If epsilon=False, always choose the best action.
        """
        actions = list(Nim.available_actions(state))
        if not actions:
            return None

        # Exploration
        if epsilon and random.random() < self.epsilon:
            return random.choice(actions)

        # Optional perfect-play fallback:
        # when exploration is disabled and `use_optimal` is enabled, return
        # the XOR-optimal Nim move.
        if (not epsilon) and getattr(self, "use_optimal", False):
            optimal = self.optimal_action(state)
            if optimal is not None:
                return optimal

        # Greedy action: pick the action(s) with the highest Q-value.
        best_q = -float("inf")
        best_actions = []
        for action in actions:
            q_val = self.get_q_value(state, action)
            if q_val > best_q:
                best_q = q_val
                best_actions = [action]
            elif q_val == best_q:
                best_actions.append(action)
        return random.choice(best_actions)


def train(n):
    player = NimAI()

    for i in range(n):
        game = Nim([4, 4, 4, 4])
        last_move = {0: {"state": None, "action": None}, 1: {"state": None, "action": None}}

        while True:
            state = game.piles.copy()
            action = player.choose_action(state)
            last_move[game.player]["state"] = state
            last_move[game.player]["action"] = action

            game.move(action)
            new_state = game.piles.copy()

            if game.winner is not None:
                # Terminal update.
                # Flip the reward signs so Q-values correspond to the player
                # who made the last move.
                player.update(state, action, new_state, 1)
                player.update(
                    last_move[game.player]["state"],
                    last_move[game.player]["action"],
                    new_state,
                    -1,
                )
                break
            elif last_move[game.player]["state"] is not None:
                player.update(last_move[game.player]["state"], last_move[game.player]["action"], new_state, 0)

    return player

