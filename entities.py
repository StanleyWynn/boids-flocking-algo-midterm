import math
import random
import pygame
from config import ALERT_DIST, HEIGHT, RED, TRAIL_RED, WIDTH


class Obstacle:
    def __init__(self, x, y, r=38.0):
        self.x = float(x)
        self.y = float(y)
        self.r = float(r)

    def draw(self, screen):
        pos = (round(self.x), round(self.y))
        pygame.draw.circle(screen, (42, 50, 65), pos, round(self.r))
        pygame.draw.circle(screen, (100, 118, 145), pos, round(self.r), 2)
        pygame.draw.circle(screen, (60, 72, 90), pos, round(self.r - 6), 1)


class Predator:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, 2 * math.pi)
        self.speed = 3.8
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.max_turn = 0.16
        self.timer = 0
        self.target_idx = None
        self.trail = []

    def update(self, boid_data, obstacles, speed_mult=1.0):
        self.timer += 1
        if self.target_idx is None or self.timer > 100 or self.target_idx >= len(boid_data):
            self.pick_target(boid_data)
            self.timer = 0

        if self.target_idx is not None and self.target_idx < len(boid_data):
            tx, ty, _, _, _ = boid_data[self.target_idx]
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)

            if dist > 1e-5:
                target_vx = (dx / dist) * self.speed
                target_vy = (dy / dist) * self.speed
                steer_x = target_vx - self.vx
                steer_y = target_vy - self.vy
                steer_mag = math.hypot(steer_x, steer_y)
                if steer_mag > self.max_turn:
                    steer_x = (steer_x / steer_mag) * self.max_turn
                    steer_y = (steer_y / steer_mag) * self.max_turn
                self.vx += steer_x
                self.vy += steer_y

        for obs in obstacles:
            ox = self.x - obs.x
            oy = self.y - obs.y
            dist = math.hypot(ox, oy)
            safe = obs.r + 35.0
            if 1e-4 < dist < safe:
                push = (safe - dist) / dist
                self.vx += (ox / dist) * push * 0.45
                self.vy += (oy / dist) * push * 0.45

        cur_speed = math.hypot(self.vx, self.vy)
        if cur_speed > self.speed:
            self.vx = (self.vx / cur_speed) * self.speed
            self.vy = (self.vy / cur_speed) * self.speed
        elif cur_speed < 1.4:
            scale = 1.4 / max(cur_speed, 1e-5)
            self.vx *= scale
            self.vy *= scale

        if self.x < 30:
            self.vx += 0.4
        elif self.x > WIDTH - 30:
            self.vx -= 0.4
        if self.y < 30:
            self.vy += 0.4
        elif self.y > HEIGHT - 30:
            self.vy -= 0.4

        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult

        self.trail.append((self.x, self.y))
        if len(self.trail) > 14:
            self.trail.pop(0)

    def pick_target(self, boid_data):
        if not boid_data:
            self.target_idx = None
            return

        sample = random.sample(range(len(boid_data)), min(40, len(boid_data)))
        best_idx = None
        best_score = float("inf")

        for i in sample:
            bx, by, _, _, _ = boid_data[i]
            dist = math.hypot(bx - self.x, by - self.y)

            density = 0
            for j in sample:
                if i == j:
                    continue
                ox, oy, _, _, _ = boid_data[j]
                if (ox - bx) ** 2 + (oy - by) ** 2 < 3600.0:
                    density += 1

            score = dist / (1.0 + 0.45 * density)
            if score < best_score:
                best_score = score
                best_idx = i

        self.target_idx = best_idx

    def draw(self, screen, show_trails, show_debug):
        if show_trails and len(self.trail) > 1:
            pygame.draw.lines(screen, TRAIL_RED, False, self.trail, 2)

        if show_debug:
            pygame.draw.circle(
                screen,
                (140, 50, 50),
                (round(self.x), round(self.y)),
                round(ALERT_DIST),
                1,
            )

        angle = math.atan2(self.vy, self.vx)
        size = 14
        tip = (self.x + size * math.cos(angle), self.y + size * math.sin(angle))
        left = (
            self.x + size * 0.9 * math.cos(angle + 2.2),
            self.y + size * 0.9 * math.sin(angle + 2.2),
        )
        notch = (self.x - size * 0.3 * math.cos(angle), self.y - size * 0.3 * math.sin(angle))
        right = (
            self.x + size * 0.9 * math.cos(angle - 2.2),
            self.y + size * 0.9 * math.sin(angle - 2.2),
        )
        points = [(round(px), round(py)) for px, py in (tip, left, notch, right)]
        pygame.draw.polygon(screen, RED, points)
        pygame.draw.polygon(screen, (255, 140, 140), points, 1)