import math
import random
import pygame
from config import (
    ALERT_DIST,
    BLUE,
    EDGE_MARGIN,
    EDGE_TURN,
    GREEN,
    HEIGHT,
    JOIN_DIST,
    ORANGE,
    PROTECTED_DIST,
    TRAIL_BLUE,
    TRAIL_GREEN,
    TRAIL_ORANGE,
    VISUAL_DIST,
    WANDER,
    WEIGHT_ALIGN,
    WEIGHT_COH,
    WEIGHT_EVADE,
    WEIGHT_OBS,
    WEIGHT_SEP,
    WIDTH,
)


class Boid:
    def __init__(self, x, y, kind=1):
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        self.set_type()

        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(self.min_speed, self.max_speed)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.trail = []

    def set_type(self):
        if self.kind == 1:
            self.max_speed = 4.2
            self.min_speed = 2.0
            self.color = BLUE
            self.trail_color = TRAIL_BLUE
            self.size = 8
        elif self.kind == 2:
            self.max_speed = 3.6
            self.min_speed = 1.6
            self.color = GREEN
            self.trail_color = TRAIL_GREEN
            self.size = 10
        else:
            self.max_speed = 3.9
            self.min_speed = 1.8
            self.color = ORANGE
            self.trail_color = TRAIL_ORANGE
            self.size = 9

    def get_steer(self, boid_data, predators, obstacles, rules):
        sep_x = sep_y = 0.0
        align_x = align_y = 0.0
        center_x = center_y = 0.0
        same_count = 0
        close_count = 0

        nearest_kind = None
        min_dist_sq = float("inf")
        counts = {1: 0, 2: 0, 3: 0}

        for ox, oy, ovx, ovy, okind in boid_data:
            dx = ox - self.x
            dy = oy - self.y
            dist_sq = dx * dx + dy * dy

            if dist_sq <= 1e-5 or dist_sq > VISUAL_DIST * VISUAL_DIST:
                continue

            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest_kind = okind

            dist = math.sqrt(dist_sq)

            if rules.sep and dist < PROTECTED_DIST:
                close_count += 1
                push = (PROTECTED_DIST - dist) / dist
                sep_x -= (dx / dist) * push
                sep_y -= (dy / dist) * push

            counts[okind] += 1
            if okind == self.kind:
                same_count += 1
                align_x += ovx
                align_y += ovy
                center_x += ox
                center_y += oy

        next_kind = self.kind
        if rules.join and nearest_kind is not None and min_dist_sq < JOIN_DIST * JOIN_DIST:
            if nearest_kind != self.kind and counts[nearest_kind] >= counts[self.kind] + 3 and counts[nearest_kind] >= 4:
                next_kind = nearest_kind

        next_vx = self.vx
        next_vy = self.vy

        if rules.sep and close_count > 0:
            next_vx += sep_x * WEIGHT_SEP
            next_vy += sep_y * WEIGHT_SEP

        obs_hazard = 0.0
        if rules.avoid_obs and obstacles:
            for obs in obstacles:
                ox = obs.x - self.x
                oy = obs.y - self.y
                dist = math.hypot(ox, oy)
                margin = obs.r + 60.0

                if 1e-4 < dist < margin:
                    cur_speed = max(math.hypot(self.vx, self.vy), 1e-4)
                    heading_dot = (self.vx * ox + self.vy * oy) / (dist * cur_speed)

                    if heading_dot > -0.3:
                        urgency = ((margin - dist) / margin) ** 1.5
                        away_x = -ox / dist
                        away_y = -oy / dist

                        side_x = -away_y
                        side_y = away_x
                        if (self.vx * side_x + self.vy * side_y) < 0:
                            side_x = -side_x
                            side_y = -side_y

                        steer_x = away_x * 0.70 + side_x * 0.80
                        steer_y = away_y * 0.70 + side_y * 0.80
                        steer_len = math.hypot(steer_x, steer_y)
                        if steer_len > 1e-5:
                            next_vx += (steer_x / steer_len) * urgency * WEIGHT_OBS * self.max_speed
                            next_vy += (steer_y / steer_len) * urgency * WEIGHT_OBS * self.max_speed
                            obs_hazard = max(obs_hazard, urgency)

        if same_count > 0:
            if rules.align:
                align_factor = max(0.15, 1.0 - obs_hazard * 0.8)
                next_vx += ((align_x / same_count) - self.vx) * (WEIGHT_ALIGN * align_factor)
                next_vy += ((align_y / same_count) - self.vy) * (WEIGHT_ALIGN * align_factor)

            if rules.coh:
                coh_factor = max(0.0, 1.0 - (close_count * 0.45) - (obs_hazard * 0.9))
                next_vx += ((center_x / same_count) - self.x) * (WEIGHT_COH * coh_factor)
                next_vy += ((center_y / same_count) - self.y) * (WEIGHT_COH * coh_factor)

        if rules.evade and predators:
            for pred in predators:
                px = pred.x - self.x
                py = pred.y - self.y
                p_dist_sq = px * px + py * py
                if 1e-4 < p_dist_sq < ALERT_DIST * ALERT_DIST:
                    p_dist = math.sqrt(p_dist_sq)
                    push = (ALERT_DIST - p_dist) / p_dist
                    next_vx -= (px / p_dist) * push * WEIGHT_EVADE * self.max_speed
                    next_vy -= (py / p_dist) * push * WEIGHT_EVADE * self.max_speed

        next_vx += random.uniform(-WANDER, WANDER)
        next_vy += random.uniform(-WANDER, WANDER)

        if self.x < EDGE_MARGIN:
            ratio = (EDGE_MARGIN - self.x) / EDGE_MARGIN
            next_vx += EDGE_TURN * (ratio ** 1.6)
        elif self.x > WIDTH - EDGE_MARGIN:
            ratio = (self.x - (WIDTH - EDGE_MARGIN)) / EDGE_MARGIN
            next_vx -= EDGE_TURN * (ratio ** 1.6)

        if self.y < EDGE_MARGIN:
            ratio = (EDGE_MARGIN - self.y) / EDGE_MARGIN
            next_vy += EDGE_TURN * (ratio ** 1.6)
        elif self.y > HEIGHT - EDGE_MARGIN:
            ratio = (self.y - (HEIGHT - EDGE_MARGIN)) / EDGE_MARGIN
            next_vy -= EDGE_TURN * (ratio ** 1.6)

        speed = math.hypot(next_vx, next_vy)
        if speed <= 1e-9:
            angle = random.uniform(0, 2 * math.pi)
            next_vx = math.cos(angle) * self.min_speed
            next_vy = math.sin(angle) * self.min_speed
        elif speed > self.max_speed:
            next_vx = (next_vx / speed) * self.max_speed
            next_vy = (next_vy / speed) * self.max_speed
        elif speed < self.min_speed:
            next_vx = (next_vx / speed) * self.min_speed
            next_vy = (next_vy / speed) * self.min_speed

        return next_vx, next_vy, next_kind

    def move(self, vx, vy, next_kind, speed_mult=1.0):
        if next_kind != self.kind:
            self.kind = next_kind
            self.set_type()

        self.vx = vx
        self.vy = vy
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult

        pad = 8.0
        if self.x < pad:
            self.x = pad
            self.vx = max(self.vx, 0.8)
        elif self.x > WIDTH - pad:
            self.x = WIDTH - pad
            self.vx = min(self.vx, -0.8)

        if self.y < pad:
            self.y = pad
            self.vy = max(self.vy, 0.8)
        elif self.y > HEIGHT - pad:
            self.y = HEIGHT - pad
            self.vy = min(self.vy, -0.8)

        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

    def draw(self, screen, show_trails, show_debug):
        if show_trails and len(self.trail) > 1:
            pygame.draw.lines(screen, self.trail_color, False, self.trail, 1)

        if show_debug:
            pos = (round(self.x), round(self.y))
            pygame.draw.circle(screen, (55, 70, 95), pos, round(VISUAL_DIST), 1)
            pygame.draw.circle(screen, (135, 65, 65), pos, round(PROTECTED_DIST), 1)

        angle = math.atan2(self.vy, self.vx)
        tip = (self.x + self.size * math.cos(angle), self.y + self.size * math.sin(angle))
        left = (
            self.x + self.size * 0.55 * math.cos(angle + 2.4),
            self.y + self.size * 0.55 * math.sin(angle + 2.4),
        )
        notch = (self.x - self.size * 0.2 * math.cos(angle), self.y - self.size * 0.2 * math.sin(angle))
        right = (
            self.x + self.size * 0.55 * math.cos(angle - 2.4),
            self.y + self.size * 0.55 * math.sin(angle - 2.4),
        )
        points = [(round(px), round(py)) for px, py in (tip, left, notch, right)]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, (220, 235, 255), points, 1)