"""
Entry point – run the Vampire Survivors game.

Usage:
    uv run main.py           # Watch the AI play
    uv run main.py --human   # Play with WASD yourself
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pygame

from game import Game, FPS
from ai_agent import HeuristicAgent


def get_human_action() -> tuple[float, float]:
    """Read WASD / arrow key input and return (dx, dy)."""
    keys = pygame.key.get_pressed()
    dx, dy = 0.0, 0.0
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dy -= 1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy += 1
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        dx -= 1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx += 1
    return dx, dy


def main():
    parser = argparse.ArgumentParser(description="Vampire Survivors AI")
    parser.add_argument("--human", action="store_true", help="Play manually with WASD")
    parser.add_argument(
        "--model-path",
        default="models/vampire_survivors_agent.json",
        help="Where the AI model checkpoint is saved",
    )
    parser.add_argument(
        "--save-every",
        type=float,
        default=30.0,
        help="Save the AI model every N seconds while it plays",
    )
    args = parser.parse_args()

    game = Game(render=True)
    agent = HeuristicAgent()
    obs = game.reset()
    model_path = Path(args.model_path)
    save_interval_frames = max(1, int(args.save_every * FPS))
    next_save_frame = save_interval_frames

    if not args.human:
        print(
            "[debug] agent started "
            "epsilon=N/A alpha=N/A "
            f"danger_weight={agent.danger_weight} "
            f"loot_weight={agent.loot_weight} "
            f"center_weight={agent.center_weight}"
        )

    while True:
        if game.handle_events():
            break

        if args.human:
            action = get_human_action()
        else:
            action = agent.act(obs)

        obs, reward, done = game.step(action)
        game.draw()
        game.tick()

        if not args.human and args.save_every > 0 and game.frame >= next_save_frame:
            agent.save(
                model_path,
                metadata={
                    "score": game.score,
                    "kills": game.kills,
                    "time_seconds": game.frame // FPS,
                    "level": game.player.level,
                },
            )
            print(
                "[debug] model saved "
                f"path={model_path} "
                "epsilon=N/A alpha=N/A "
                f"score={game.score} "
                f"kills={game.kills} "
                f"time={game.frame // FPS}s "
                f"level={game.player.level}"
            )
            next_save_frame += save_interval_frames

        if done:
            if not args.human:
                agent.save(
                    model_path,
                    metadata={
                        "score": game.score,
                        "kills": game.kills,
                        "time_seconds": game.frame // FPS,
                        "level": game.player.level,
                    },
                )
                print(
                    "[debug] final model saved "
                    f"path={model_path} "
                    "epsilon=N/A alpha=N/A "
                    f"score={game.score} "
                    f"kills={game.kills} "
                    f"time={game.frame // FPS}s "
                    f"level={game.player.level}"
                )
            # Show death screen briefly
            if game.font and game.screen:
                txt = game.font.render(
                    f"GAME OVER  —  Score: {game.score}  Kills: {game.kills}  "
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
