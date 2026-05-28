"""
Train the AI without rendering and keep saving the best model found.

This project uses a heuristic AI, so training here means tuning the agent's
movement weights with random mutations. Stop with Ctrl+C; the best model stays
saved on disk and can be used by play_trained.py.

Usage:
    uv run train_headless.py
    uv run train_headless.py --model-path models/best_agent.json
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import pygame

from ai_agent import HeuristicAgent
from game import FPS, Game


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def mutate_agent(agent: HeuristicAgent, alpha: float) -> HeuristicAgent:
    """Create a slightly changed copy of an agent."""
    return HeuristicAgent(
        danger_weight=clamp(random.gauss(agent.danger_weight, alpha), 0.05, 5.0),
        loot_weight=clamp(random.gauss(agent.loot_weight, alpha), 0.0, 4.0),
        center_weight=clamp(random.gauss(agent.center_weight, alpha * 0.5), 0.0, 2.0),
    )


def evaluate(agent: HeuristicAgent, episodes: int, max_frames: int) -> dict[str, float]:
    """Run the agent without rendering and return averaged stats."""
    total_fitness = 0.0
    total_reward = 0.0
    total_score = 0.0
    total_kills = 0.0
    total_time = 0.0
    total_level = 0.0

    for _ in range(episodes):
        game = Game(render=False)
        obs = game.reset()
        reward_sum = 0.0

        while not game.done and game.frame < max_frames:
            action = agent.act(obs)
            obs, reward, done = game.step(action)
            reward_sum += reward
            if done:
                break

        time_seconds = game.frame / FPS
        fitness = (
            reward_sum
            + game.score * 1.0
            + game.kills * 20.0
            + time_seconds * 5.0
            + game.player.level * 50.0
        )

        total_fitness += fitness
        total_reward += reward_sum
        total_score += game.score
        total_kills += game.kills
        total_time += time_seconds
        total_level += game.player.level

    pygame.quit()
    return {
        "fitness": total_fitness / episodes,
        "reward": total_reward / episodes,
        "score": total_score / episodes,
        "kills": total_kills / episodes,
        "time_seconds": total_time / episodes,
        "level": total_level / episodes,
    }


def save_best(
    agent: HeuristicAgent,
    model_path: Path,
    generation: int,
    stats: dict[str, float],
    epsilon: float,
    alpha: float,
) -> None:
    agent.save(
        model_path,
        metadata={
            "generation": generation,
            "fitness": stats["fitness"],
            "reward": stats["reward"],
            "score": stats["score"],
            "kills": stats["kills"],
            "time_seconds": stats["time_seconds"],
            "level": stats["level"],
            "epsilon": epsilon,
            "alpha": alpha,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Headless AI trainer")
    parser.add_argument(
        "--model-path",
        default="models/vampire_survivors_agent.json",
        help="Where the best trained model is loaded from and saved to",
    )
    parser.add_argument(
        "--episodes-per-try",
        type=int,
        default=3,
        help="Episodes to average for each candidate agent",
    )
    parser.add_argument(
        "--max-seconds",
        type=float,
        default=180.0,
        help="Maximum length of one training episode",
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=0.25,
        help="Chance to explore from the original/default agent instead of the current best",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.18,
        help="Mutation strength for each new candidate",
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=0,
        help="Stop after N generations; 0 means train forever",
    )
    args = parser.parse_args()

    model_path = Path(args.model_path)
    max_frames = max(1, int(args.max_seconds * FPS))
    episodes_per_try = max(1, args.episodes_per_try)

    base_agent = HeuristicAgent()
    if model_path.exists():
        best_agent = HeuristicAgent.load(model_path)
        print(f"[debug] loaded existing model path={model_path}")
    else:
        best_agent = base_agent
        print("[debug] no existing model found; starting from default agent")

    print(
        "[debug] training started "
        f"epsilon={args.epsilon} alpha={args.alpha} "
        f"episodes_per_try={episodes_per_try} max_seconds={args.max_seconds}"
    )

    best_stats = evaluate(best_agent, episodes_per_try, max_frames)
    save_best(best_agent, model_path, 0, best_stats, args.epsilon, args.alpha)
    print(
        "[debug] initial best "
        f"fitness={best_stats['fitness']:.2f} "
        f"score={best_stats['score']:.1f} "
        f"kills={best_stats['kills']:.1f} "
        f"time={best_stats['time_seconds']:.1f}s "
        f"level={best_stats['level']:.1f}"
    )

    generation = 0
    try:
        while True:
            generation += 1
            if args.generations > 0 and generation > args.generations:
                break

            parent = base_agent if random.random() < args.epsilon else best_agent
            candidate = mutate_agent(parent, args.alpha)
            stats = evaluate(candidate, episodes_per_try, max_frames)

            if stats["fitness"] > best_stats["fitness"]:
                best_agent = candidate
                best_stats = stats
                save_best(best_agent, model_path, generation, best_stats, args.epsilon, args.alpha)
                print(
                    "[debug] new best "
                    f"generation={generation} "
                    f"epsilon={args.epsilon} alpha={args.alpha} "
                    f"fitness={stats['fitness']:.2f} "
                    f"score={stats['score']:.1f} "
                    f"kills={stats['kills']:.1f} "
                    f"time={stats['time_seconds']:.1f}s "
                    f"level={stats['level']:.1f} "
                    f"danger_weight={best_agent.danger_weight:.3f} "
                    f"loot_weight={best_agent.loot_weight:.3f} "
                    f"center_weight={best_agent.center_weight:.3f} "
                    f"saved={model_path}"
                )
            elif generation % 10 == 0:
                print(
                    "[debug] training "
                    f"generation={generation} "
                    f"epsilon={args.epsilon} alpha={args.alpha} "
                    f"candidate_fitness={stats['fitness']:.2f} "
                    f"best_fitness={best_stats['fitness']:.2f}"
                )
    except KeyboardInterrupt:
        save_best(best_agent, model_path, generation, best_stats, args.epsilon, args.alpha)
        print(f"\n[debug] stopped; best model saved path={model_path}")
    else:
        save_best(best_agent, model_path, generation - 1, best_stats, args.epsilon, args.alpha)
        print(f"[debug] finished; best model saved path={model_path}")


if __name__ == "__main__":
    main()
