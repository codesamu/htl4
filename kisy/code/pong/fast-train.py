import random
import pygame
from pong_rl_environment import pong_environment
from deepQ_agent import my_agent

# =========================
# SETUP
# =========================

# Rendering is disabled for faster training
env = pong_environment(render=False)

STATE_SIZE = 8
ACTION_SIZE = 3

agent = my_agent(
    inp_shape=STATE_SIZE,
    output_shape=ACTION_SIZE,
    loadmodel=False,
    trainme=True,
    filename="pong.keras"
)

EPISODES = 5000

# =========================
# TRAINING LOOP
# =========================

for episode in range(EPISODES):

    state, _, _, _ = env.one_step(2, human=False)
    total_reward = 0

    done = False

    while not done:

        # AI action
        action_right = agent.get_action(state)

        # random opponent (left paddle)
        action_left = random.randint(0, 2)

        # step environment
        next_state, reward_r, reward_l, done = env.one_step(
            actionrightpaddle=action_right,
            human=False,
            actionleftpaddle=action_left
        )

        # store experience (RIGHT agent learns)
        agent.memory.append(
            (state, action_right, reward_r, next_state, done)
        )

        # train step
        agent.train()

        state = next_state
        total_reward += reward_r

        # pygame quit handling (still useful if a window is visible)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    print(f"Episode {episode} | Reward: {total_reward}")

# =========================
# SAVE FINAL MODEL
# =========================

agent.model.save("pong.keras")
print("Model saved as pong.keras")
