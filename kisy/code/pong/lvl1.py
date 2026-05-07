import random
import pygame
from pong_rl_environment import pong_environment
from deepQ_agent import my_agent

# Environment
env = pong_environment(render=True)

# State size = 8 (Ball + Paddles), Actions = 3 (up/down/stay)
agent = my_agent(inp_shape=8, output_shape=3, loadmodel=False, trainme=True)

running = True

while running:

    # get random action for human paddle OR fixed logic (here: do nothing)
    human_action = 2

    # AI action
    state, reward, rewardleft, done = env.one_step(2, human=True)
    ai_action = agent.get_action(state)

    # step again with AI controlling right paddle
    next_state, reward, rewardleft, done = env.one_step(ai_action, human=True)

    # store experience
    agent.memory.append((state, ai_action, reward, next_state, done))

    # train agent
    agent.train()

    # quit handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if done:
        print("Episode finished")
