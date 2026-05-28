"""
Vampire Survivors-like game.

Simple top-down survival game:
- Player auto-attacks the nearest enemy periodically.
- Enemies spawn from screen edges and chase the player.
- Killing enemies drops XP gems; collecting them levels up the player.
- Each level increases attack damage and radius.
- Goal: survive as long as possible.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import pygame
import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

PLAYER_SPEED = 3.0
PLAYER_RADIUS = 12
PLAYER_HP = 100

ENEMY_SPEED_BASE = 1.2
ENEMY_HP_BASE = 40
ENEMY_RADIUS = 10
ENEMY_DAMAGE = 8  # damage per hit frame

ATTACK_COOLDOWN = 60  # frames between auto-attacks
ATTACK_RADIUS_BASE = 70
ATTACK_RADIUS_MAX = 120  # hard cap on attack radius
ATTACK_DAMAGE_BASE = 15

XP_RADIUS = 6
XP_VALUE = 25
XP_TO_LEVEL = 100  # XP needed per level

SPAWN_INTERVAL_START = 80   # frames between spawns at start
SPAWN_INTERVAL_MIN = 10     # fastest spawn rate
SPAWN_RAMP_RATE = 0.8       # frames of reduction per second of game time

# Colors
COL_BG = (15, 15, 25)
COL_PLAYER = (80, 200, 255)
COL_ENEMY = (220, 60, 60)
COL_XP = (100, 255, 100)
COL_ATTACK = (255, 255, 100, 120)
COL_HP_BAR = (220, 50, 50)
COL_HP_BG = (60, 20, 20)
COL_TEXT = (230, 230, 230)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class Entity:
    x: float
    y: float
    hp: float = 0
    radius: float = 10


@dataclass
class Player(Entity):
    level: int = 1
    xp: int = 0
    attack_timer: int = 0


@dataclass
class Enemy(Entity):
    speed: float = ENEMY_SPEED_BASE


@dataclass
class XPGem(Entity):
    value: int = XP_VALUE


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class Game:
    """Self-contained game state that can be stepped frame-by-frame."""

    def __init__(self, render: bool = True):
        pygame.init()
        self.render_enabled = render
        if render:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Vampire Survivors AI")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont("monospace", 16, bold=True)
        else:
            self.screen = None
            self.clock = None
            self.font = None
        self.reset()

    # ------------------------------------------------------------------
    # Reset / init
    # ------------------------------------------------------------------
    def reset(self):
        """Reset the game to initial state. Returns observation."""
        self.player = Player(
            x=WIDTH / 2, y=HEIGHT / 2,
            hp=PLAYER_HP, radius=PLAYER_RADIUS
        )
        self.enemies: list[Enemy] = []
        self.gems: list[XPGem] = []
        self.frame = 0
        self.score = 0
        self.kills = 0
        self.spawn_timer = 0
        self.attack_flash = 0  # visual flash timer
        self.done = False
        return self.get_observation()

    # ------------------------------------------------------------------
    # Observation for AI
    # ------------------------------------------------------------------
    def get_observation(self) -> dict:
        """Return a simple dict describing the current game state."""
        p = self.player

        # Find the closest enemies (up to 8)
        enemies_sorted = sorted(
            self.enemies,
            key=lambda e: (e.x - p.x) ** 2 + (e.y - p.y) ** 2
        )[:8]

        enemy_data = []
        for e in enemies_sorted:
            dx = e.x - p.x
            dy = e.y - p.y
            dist = math.hypot(dx, dy)
            enemy_data.append((dx / WIDTH, dy / HEIGHT, dist / math.hypot(WIDTH, HEIGHT), e.hp / ENEMY_HP_BASE))

        # Pad to 8
        while len(enemy_data) < 8:
            enemy_data.append((0.0, 0.0, 1.0, 0.0))

        # Find closest gems (up to 4)
        gems_sorted = sorted(
            self.gems,
            key=lambda g: (g.x - p.x) ** 2 + (g.y - p.y) ** 2
        )[:4]

        gem_data = []
        for g in gems_sorted:
            dx = g.x - p.x
            dy = g.y - p.y
            dist = math.hypot(dx, dy)
            gem_data.append((dx / WIDTH, dy / HEIGHT, dist / math.hypot(WIDTH, HEIGHT)))

        while len(gem_data) < 4:
            gem_data.append((0.0, 0.0, 1.0))

        return {
            "player_x": p.x / WIDTH,
            "player_y": p.y / HEIGHT,
            "player_hp": p.hp / PLAYER_HP,
            "player_level": p.level,
            "xp_progress": p.xp / XP_TO_LEVEL,
            "enemies": enemy_data,
            "gems": gem_data,
            "num_enemies": len(self.enemies),
            "frame": self.frame,
        }

    # ------------------------------------------------------------------
    # Step
    # ------------------------------------------------------------------
    def step(self, action: tuple[float, float]) -> tuple[dict, float, bool]:
        """
        Advance one frame.
        action: (dx, dy) movement direction, each in [-1, 1].
        Returns: (observation, reward, done)
        """
        if self.done:
            return self.get_observation(), 0.0, True

        reward = 0.1  # small reward for surviving each frame
        p = self.player

        # --- Move player ---
        dx, dy = action
        length = math.hypot(dx, dy)
        if length > 0:
            dx, dy = dx / length, dy / length
        p.x = max(p.radius, min(WIDTH - p.radius, p.x + dx * PLAYER_SPEED))
        p.y = max(p.radius, min(HEIGHT - p.radius, p.y + dy * PLAYER_SPEED))

        # --- Spawn enemies ---
        elapsed_sec = self.frame / FPS
        spawn_interval = max(
            SPAWN_INTERVAL_MIN,
            SPAWN_INTERVAL_START - elapsed_sec * SPAWN_RAMP_RATE
        )
        self.spawn_timer += 1
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0
            self._spawn_enemy()

        # --- Move enemies ---
        for e in self.enemies:
            ex, ey = e.x - p.x, e.y - p.y
            dist = math.hypot(ex, ey)
            if dist > 0:
                e.x -= (ex / dist) * e.speed
                e.y -= (ey / dist) * e.speed

        # --- Enemy collision with player ---
        for e in self.enemies:
            dist = math.hypot(e.x - p.x, e.y - p.y)
            if dist < p.radius + e.radius:
                p.hp -= ENEMY_DAMAGE / FPS  # damage per frame
                reward -= 0.5

        # --- Player auto-attack ---
        p.attack_timer += 1
        atk_radius = min(ATTACK_RADIUS_BASE + p.level * 5, ATTACK_RADIUS_MAX)
        atk_damage = ATTACK_DAMAGE_BASE + p.level * 3
        if p.attack_timer >= ATTACK_COOLDOWN:
            p.attack_timer = 0
            self.attack_flash = 8
            killed = []
            for e in self.enemies:
                dist = math.hypot(e.x - p.x, e.y - p.y)
                if dist < atk_radius:
                    e.hp -= atk_damage
                    if e.hp <= 0:
                        killed.append(e)
            for e in killed:
                self.enemies.remove(e)
                self.gems.append(XPGem(x=e.x, y=e.y, radius=XP_RADIUS, value=XP_VALUE))
                self.kills += 1
                self.score += 10
                reward += 5.0

        # --- Collect XP gems ---
        collected = []
        for g in self.gems:
            dist = math.hypot(g.x - p.x, g.y - p.y)
            if dist < p.radius + g.radius + 20:  # generous pickup radius
                collected.append(g)
                p.xp += g.value
                reward += 2.0
        for g in collected:
            self.gems.remove(g)

        # --- Level up ---
        while p.xp >= XP_TO_LEVEL:
            p.xp -= XP_TO_LEVEL
            p.level += 1
            p.hp = min(p.hp + 20, PLAYER_HP)  # heal on level up
            reward += 10.0

        # --- Check death ---
        if p.hp <= 0:
            self.done = True
            reward -= 50.0

        self.frame += 1
        if self.attack_flash > 0:
            self.attack_flash -= 1

        return self.get_observation(), reward, self.done

    # ------------------------------------------------------------------
    # Spawn
    # ------------------------------------------------------------------
    def _spawn_enemy(self):
        side = random.randint(0, 3)
        if side == 0:  # top
            x, y = random.uniform(0, WIDTH), -ENEMY_RADIUS
        elif side == 1:  # bottom
            x, y = random.uniform(0, WIDTH), HEIGHT + ENEMY_RADIUS
        elif side == 2:  # left
            x, y = -ENEMY_RADIUS, random.uniform(0, HEIGHT)
        else:  # right
            x, y = WIDTH + ENEMY_RADIUS, random.uniform(0, HEIGHT)

        # Scale HP and speed with time — enemies get much tougher
        t = self.frame / FPS
        hp = ENEMY_HP_BASE + t * 1.5
        speed = ENEMY_SPEED_BASE + t * 0.03
        radius = ENEMY_RADIUS + min(t * 0.05, 4)  # grow slightly over time

        # After 30s, spawn in groups of 2-3
        count = 1
        if t > 30:
            count = random.randint(2, 3)
        elif t > 60:
            count = random.randint(2, 4)

        for _ in range(count):
            # Slight position jitter for groups
            jx = x + random.uniform(-20, 20)
            jy = y + random.uniform(-20, 20)
            self.enemies.append(Enemy(x=jx, y=jy, hp=hp, radius=int(radius), speed=speed))

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------
    def draw(self):
        if not self.render_enabled:
            return
        screen = self.screen
        screen.fill(COL_BG)
        p = self.player
        atk_radius = min(ATTACK_RADIUS_BASE + p.level * 5, ATTACK_RADIUS_MAX)

        # Attack flash
        if self.attack_flash > 0:
            surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 255, 100, 30 + self.attack_flash * 10),
                               (int(p.x), int(p.y)), atk_radius)
            screen.blit(surf, (0, 0))

        # XP gems
        for g in self.gems:
            pygame.draw.circle(screen, COL_XP, (int(g.x), int(g.y)), g.radius)

        # Enemies
        for e in self.enemies:
            pygame.draw.circle(screen, COL_ENEMY, (int(e.x), int(e.y)), int(e.radius))

        # Player
        pygame.draw.circle(screen, COL_PLAYER, (int(p.x), int(p.y)), p.radius)

        # HP bar
        bar_w, bar_h = 200, 14
        bx, by = 10, 10
        hp_frac = max(0, p.hp / PLAYER_HP)
        pygame.draw.rect(screen, COL_HP_BG, (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, COL_HP_BAR, (bx, by, int(bar_w * hp_frac), bar_h))

        # HUD text
        hud = f"Lv {p.level}  Score {self.score}  Kills {self.kills}  Time {self.frame // FPS}s"
        txt = self.font.render(hud, True, COL_TEXT)
        screen.blit(txt, (10, 30))

        pygame.display.flip()

    # ------------------------------------------------------------------
    # Handle pygame events (returns quit flag)
    # ------------------------------------------------------------------
    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
        return False

    def tick(self):
        if self.clock:
            self.clock.tick(FPS)
