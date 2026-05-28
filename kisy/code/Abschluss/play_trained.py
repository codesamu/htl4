"""
Run the game with a saved AI model loaded before play starts.

Usage:
    uv run play_trained.py
    uv run play_trained.py --model-path models/vampire_survivors_agent.json
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pygame

from ai_agent import HeuristicAgent
from game import FPS, Game


def main() -> None:
    parser = argparse.ArgumentParser(description="Play using a saved Vampire Survivors AI model")
    parser.add_argument(
        "--model-path",
        default="models/vampire_survivors_agent.json",
        help="Saved model checkpoint to load before starting",
    )
    args = parser.parse_args()

    model_path = Path(args.model_path)
    if not model_path.exists():
        raise SystemExit(
            f"No trained model found at {model_path}. "
            "Run `uv run main.py` first so it can save one."
        )

    agent = HeuristicAgent.load(model_path)
    print(
        "[debug] trained agent loaded "
        f"path={model_path} "
        "epsilon=N/A alpha=N/A "
        f"danger_weight={agent.danger_weight} "
        f"loot_weight={agent.loot_weight} "
        f"center_weight={agent.center_weight}"
    )
    game = Game(render=True)
    obs = game.reset()

    while True:
        if game.handle_events():
            break

        action = agent.act(obs)
        obs, reward, done = game.step(action)
        game.draw()
        game.tick()

        if done:
            if game.font and game.screen:
                txt = game.font.render(
                    f"GAME OVER  -  Score: {game.score}  Kills: {game.kills}  "
                    f"Time: {game.frame // FPS}s  Level: {game.player.level}",
                    True, (255, 80, 80),
                )
                rect = txt.get_rect(center=(400, 300))
                game.screen.blit(txt, rect)
                pygame.display.flip()
                pygame.time.wait(3000)
            break

    pygame.quit()


if __name__ == "__main__":
    main()
