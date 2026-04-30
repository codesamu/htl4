import pygame
import random
from pong_rl_environment import pong_environment

# create environment
env = pong_environment(render=True)

running = True

while running:
    # pick random action (0=up, 1=down, 2=do nothing)
    action = random.randint(0, 2)

    # step the environment every frame
    positiondata, reward, rewardleft, done = env.one_step(action)

    # handle quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # optional: restart if episode ends
    if done:
        print("Episode finished")
        # you could reset logic here if needed

pygame.quit()
