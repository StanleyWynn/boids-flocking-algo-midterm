import math
import random
from boid import Boid
from config import HEIGHT, NUM_BOIDS, WIDTH


def get_order(boids):
    if not boids:
        return 0.0

    sum_x = 0.0
    sum_y = 0.0
    valid = 0
    for b in boids:
        speed = math.hypot(b.vx, b.vy)
        if speed > 1e-9:
            sum_x += b.vx / speed
            sum_y += b.vy / speed
            valid += 1

    if valid == 0:
        return 0.0
    return min(1.0, math.hypot(sum_x, sum_y) / valid)


def setup_flock():
    boids = [
        Boid(
            random.uniform(100, WIDTH - 100),
            random.uniform(100, HEIGHT - 100),
            kind=random.choice([1, 2, 3]),
        )
        for _ in range(NUM_BOIDS)
    ]
    predators = []
    obstacles = []
    return boids, predators, obstacles


def update_flock(boids, predators, obstacles, rules, speed_mult=1.0):
    boid_data = [(b.x, b.y, b.vx, b.vy, b.kind) for b in boids]

    next_moves = [
        b.get_steer(boid_data, predators, obstacles, rules)
        for b in boids
    ]

    for b, (vx, vy, next_kind) in zip(boids, next_moves):
        b.move(vx, vy, next_kind, speed_mult)

    for p in predators:
        p.update(boid_data, obstacles, speed_mult)

    if rules.sep:
        for i in range(len(boids)):
            b1 = boids[i]
            for j in range(i + 1, len(boids)):
                b2 = boids[j]
                dx = b2.x - b1.x
                dy = b2.y - b1.y
                min_dist = b1.size + b2.size + 2.0
                if abs(dx) > min_dist or abs(dy) > min_dist:
                    continue
                dist_sq = dx * dx + dy * dy
                if 0 < dist_sq < min_dist * min_dist:
                    dist = math.sqrt(dist_sq)
                    push = 0.5 * (min_dist - dist)
                    nx = dx / dist
                    ny = dy / dist
                    b1.x -= nx * push
                    b1.y -= ny * push
                    b2.x += nx * push
                    b2.y += ny * push

                    v_dot = (b1.vx - b2.vx) * nx + (b1.vy - b2.vy) * ny
                    if v_dot > 0:
                        b1.vx -= nx * v_dot * 0.6
                        b1.vy -= ny * v_dot * 0.6
                        b2.vx += nx * v_dot * 0.6
                        b2.vy += ny * v_dot * 0.6

    for b in boids:
        for obs in obstacles:
            dx = b.x - obs.x
            dy = b.y - obs.y
            dist = math.hypot(dx, dy)
            min_dist = obs.r + b.size + 1.0
            if 0 < dist < min_dist:
                nx = dx / dist
                ny = dy / dist
                b.x = obs.x + nx * min_dist
                b.y = obs.y + ny * min_dist
                v_dot = b.vx * nx + b.vy * ny
                if v_dot < 0:
                    b.vx -= 1.1 * v_dot * nx
                    b.vy -= 1.1 * v_dot * ny

    for p in predators:
        for obs in obstacles:
            dx = p.x - obs.x
            dy = p.y - obs.y
            dist = math.hypot(dx, dy)
            min_dist = obs.r + 14.0
            if 0 < dist < min_dist:
                nx = dx / dist
                ny = dy / dist
                p.x = obs.x + nx * min_dist
                p.y = obs.y + ny * min_dist
                v_dot = p.vx * nx + p.vy * ny
                if v_dot < 0:
                    p.vx -= 1.1 * v_dot * nx
                    p.vy -= 1.1 * v_dot * ny