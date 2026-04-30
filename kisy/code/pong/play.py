import pygame
import random
from pong_rl_environment import pong_environment
from deepQ_agent import my_agent

env = pong_environment(render=True)

agent = my_agent(
    inp_shape=8,
    output_shape=3,
    loadmodel=True,
    trainme=False,
    filename="pong.keras"
)

while True:

    state, _, _, _ = env.one_step(2, human=True)

    action_ai = agent.get_action(state)
    action_human = 2  # AI controls right paddle

    _, _, _, done = env.one_step(
        actionrightpaddle=action_ai,
        human=False,
        actionleftpaddle=action_human
    )

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
