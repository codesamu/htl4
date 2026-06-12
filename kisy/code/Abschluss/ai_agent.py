"""
AI agent for the Vampire Survivors game.

Uses a simple heuristic approach:
  1. Compute a "danger" vector pointing away from nearby enemies.
  2. Compute a "loot" vector pointing toward the nearest XP gem.
  3. Blend them based on urgency (low HP → more flee, high HP → more loot).
  4. Add a mild center pull so the agent doesn't get stuck in corners.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


MODEL_VERSION = 1


class HeuristicAgent:
    """Rule-based AI that balances dodging enemies and collecting XP."""

    def __init__(self, danger_weight: float = 1.0, loot_weight: float = 0.6,
                 center_weight: float = 0.15):
        self.danger_weight = danger_weight
        self.loot_weight = loot_weight
        self.center_weight = center_weight

    def to_model_data(self, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return a JSON-serializable checkpoint for this agent."""
        return {
            "version": MODEL_VERSION,
            "agent": "HeuristicAgent",
            "params": {
                "danger_weight": self.danger_weight,
                "loot_weight": self.loot_weight,
                "center_weight": self.center_weight,
            },
            "metadata": metadata or {},
        }

    def save(self, path: str | Path, metadata: dict[str, Any] | None = None) -> None:
        """Save this agent's model parameters to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_model_data(metadata), indent=2), encoding="utf-8")

    @classmethod
    def from_model_data(cls, data: dict[str, Any]) -> "HeuristicAgent":
        """Create an agent from checkpoint data."""
        if data.get("agent") != "HeuristicAgent":
            raise ValueError(f"Unsupported agent type: {data.get('agent')}")

        params = data.get("params", {})
        return cls(
            danger_weight=float(params.get("danger_weight", 1.0)),
            loot_weight=float(params.get("loot_weight", 0.6)),
            center_weight=float(params.get("center_weight", 0.15)),
        )

    @classmethod
    def load(cls, path: str | Path) -> "HeuristicAgent":
        """Load an agent checkpoint from disk."""
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_model_data(data)

    def act(self, obs: dict) -> tuple[float, float]:
        """Given an observation dict, return (dx, dy) in [-1, 1]."""
        px, py = obs["player_x"], obs["player_y"]
        hp_frac = obs["player_hp"]
        nearest_enemy_dist_norm = float(obs.get("nearest_enemy_dist_norm", 1.0))
        nearest_gem_dist_norm = float(obs.get("nearest_gem_dist_norm", 1.0))
        enemy_pressure = float(obs.get("enemy_pressure", 0.0))
        close_enemy_count = float(obs.get("close_enemy_count", 0.0))
        attack_ready = float(obs.get("attack_ready", 0.0))
        attack_radius_norm = float(obs.get("attack_radius_norm", 0.0))
        wall_left, wall_right, wall_top, wall_bottom = obs.get(
            "wall_distances",
            (0.5, 0.5, 0.5, 0.5),
        )

        # --- Danger vector: flee from enemies ---
        flee_x, flee_y = 0.0, 0.0
        for (edx, edy, dist_norm, _ehp) in obs["enemies"]:
            if dist_norm < 0.01:
                dist_norm = 0.01
            # Inverse-square weighting: closer enemies push harder
            weight = 1.0 / (dist_norm ** 2)
            flee_x -= edx * weight
            flee_y -= edy * weight

        # Normalize
        flee_len = math.hypot(flee_x, flee_y)
        if flee_len > 0:
            flee_x /= flee_len
            flee_y /= flee_len

        if nearest_enemy_dist_norm < 1.0:
            # Make nearby threats count more strongly than distant ones.
            flee_boost = max(0.0, 1.0 - nearest_enemy_dist_norm)
            flee_x *= 1.0 + flee_boost * 0.8 + enemy_pressure * 25.0
            flee_y *= 1.0 + flee_boost * 0.8 + enemy_pressure * 25.0

        # --- Loot vector: move toward nearest gem ---
        loot_x, loot_y = 0.0, 0.0
        for (gdx, gdy, dist_norm) in obs["gems"]:
            if dist_norm < 1.0:  # real gem exists
                # Only care about the closest one
                loot_x = gdx
                loot_y = gdy
                loot_len = math.hypot(loot_x, loot_y)
                if loot_len > 0:
                    loot_x /= loot_len
                    loot_y /= loot_len
                break

        if nearest_gem_dist_norm < 1.0:
            loot_x *= 1.0 + max(0.0, 1.0 - nearest_gem_dist_norm)
            loot_y *= 1.0 + max(0.0, 1.0 - nearest_gem_dist_norm)

        # --- Center pull: stay near center of screen ---
        center_x = 0.5 - px
        center_y = 0.5 - py
        center_len = math.hypot(center_x, center_y)
        if center_len > 0:
            center_x /= center_len
            center_y /= center_len

        # --- Wall avoidance: explicitly move away from the closest edge ---
        wall_x = wall_right - wall_left
        wall_y = wall_bottom - wall_top
        wall_len = math.hypot(wall_x, wall_y)
        if wall_len > 0:
            wall_x /= wall_len
            wall_y /= wall_len

        # --- Blend based on HP ---
        # Low HP → prioritize fleeing; High HP → prioritize looting
        urgency = 1.0 - hp_frac  # 0 = full HP, 1 = nearly dead
        threat = min(1.0, nearest_enemy_dist_norm * 0.5 + enemy_pressure * 15.0 + close_enemy_count * 0.1)
        dw = self.danger_weight * (0.45 + urgency * 0.9 + threat)
        lw = self.loot_weight * max(0.15, 1.0 - urgency * 0.8) * (1.15 - min(nearest_gem_dist_norm, 1.0) * 0.5)
        cw = self.center_weight
        ww = 0.35 + (1.0 - min(wall_left, wall_right, wall_top, wall_bottom))

        if attack_ready > 0.5 and nearest_enemy_dist_norm < attack_radius_norm * 1.2:
            # If the attack is about to trigger and an enemy is in range, become less timid.
            dw *= 0.8
            lw *= 1.05

        dx = flee_x * dw + loot_x * lw + center_x * cw + wall_x * ww
        dy = flee_y * dw + loot_y * lw + center_y * cw + wall_y * ww

        # Clamp
        length = math.hypot(dx, dy)
        if length > 1:
            dx /= length
            dy /= length

        return dx, dy
