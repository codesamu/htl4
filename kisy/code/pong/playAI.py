import pygame
import numpy as np
from pong_rl_environment import pong_environment
from deepQ_agent import my_agent

def mirror_state(state):
    """
    Transforms the state so that the left agent thinks it is the right agent.
    State indices:
    0: ball_x, 1: ball_y, 2: ball_vx, 3: ball_vy
    4: paddle_left_x, 5: paddle_left_y
    6: paddle_right_x, 7: paddle_right_y
    """
    mirrored = np.copy(state)
    mirrored[0] = 1.0 - state[0]          # ball_x
    mirrored[2] = -state[2]               # ball_vx
    mirrored[4] = 1.0 - state[6]          # new_paddle_left_x (was right)
    mirrored[5] = state[7]                # new_paddle_left_y (was right)
    mirrored[6] = 1.0 - state[4]          # new_paddle_right_x (was left)
    mirrored[7] = state[5]                # new_paddle_right_y (was left)
    return mirrored

# Initialize environment
env = pong_environment(render=True)

# Load the trained agent
agent = my_agent(
    inp_shape=8,
    output_shape=3,
    loadmodel=True,
    trainme=False,
    filename="pong.keras"
)

print("Starting AI vs AI match...")

while True:
    # 1. Get current state (initially from an empty step or handled in loop)
    # We use a dummy action to get the first state if needed, but the loop handles it.
    
    # For the very first step, we might need a state
    # Let's use a standard pattern
    state, _, _, _ = env.one_step(2, human=False, actionleftpaddle=2)

    done = False
    while not done:
        # --- Right Agent Action ---
        action_right = agent.get_action(state)

        # --- Left Agent Action (using mirroring) ---
        m_state = mirror_state(state)
        action_left = agent.get_action(m_state)

        # --- Step Environment ---
        next_state, reward_r, reward_l, done = env.one_step(
            actionrightpaddle=action_right,
            human=False,
            actionleftpaddle=action_left
        )

        state = next_state

        # --- Pygame Quit Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    print("Match finished, restarting...")
