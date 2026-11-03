import math
import random
import pygame
from boid import Boid
from config import (
    BG_COLOR,
    FPS,
    HEIGHT,
    MUTED_TEXT,
    PANEL_BG,
    PANEL_BORDER,
    TEXT_COLOR,
    WIDTH,
    Rules,
)
from entities import Obstacle, Predator
from flock import get_order, setup_flock, update_flock


def draw_hud(screen, font, title_font, boids, predators, obstacles, rules, speed, paused, frame):
    panel = pygame.Surface((380, 238), pygame.SRCALPHA)
    panel.fill((*PANEL_BG, 235))
    screen.blit(panel, (14, 14))
    pygame.draw.rect(screen, PANEL_BORDER, (14, 14, 380, 238), 1, border_radius=5)

    blue = sum(1 for b in boids if b.kind == 1)
    green = sum(1 for b in boids if b.kind == 2)
    orange = sum(1 for b in boids if b.kind == 3)
    order = get_order(boids)

    screen.blit(title_font.render("Boids Simulation", True, TEXT_COLOR), (24, 16))
    screen.blit(font.render(f"Polarization (Phi): {order:.3f} | Speed: {speed:.1f}x", True, TEXT_COLOR), (24, 38))
    screen.blit(font.render(f"Blue: {blue:3d}  |  Green: {green:3d}  |  Orange: {orange:3d}", True, (135, 185, 255)), (24, 60))
    screen.blit(font.render(f"Predators: {len(predators)}  |  Obstacles: {len(obstacles)}", True, (255, 110, 110)), (24, 82))

    screen.blit(font.render(f"Separation [1]: {'ON' if rules.sep else 'OFF'} | Alignment [2]: {'ON' if rules.align else 'OFF'}", True, TEXT_COLOR), (24, 108))
    screen.blit(font.render(f"Cohesion   [3]: {'ON' if rules.coh else 'OFF'} | Joining   [J]: {'ON' if rules.join else 'OFF'}", True, TEXT_COLOR), (24, 128))
    screen.blit(font.render(f"Predator Evasion [E]: {'ON' if rules.evade else 'OFF'}", True, TEXT_COLOR), (24, 148))
    screen.blit(font.render(f"Obstacle Avoid   [O]: {'ON' if rules.avoid_obs else 'OFF'}", True, TEXT_COLOR), (24, 168))

    status = "PAUSED" if paused else "RUNNING"
    screen.blit(font.render(f"{status} | Frame: {frame} | [UP/DOWN] Speed", True, MUTED_TEXT), (24, 202))


def draw_help(screen, font):
    lines = [
        "1,2,3: sep/align/coh | J: join | K: re-divide colors | E: evade | O: avoid obstacles | UP/DOWN: speed",
        "A: add obstacle | Z: remove obstacle | C: clear obstacles | Right-click: add predator | X: clear predators",
        "T: trails | D: debug | P: pause | R: reset | Left-click: spawn boid | ESC/Q: quit",
    ]
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, MUTED_TEXT), (14, HEIGHT - 62 + i * 18))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Boids Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 14)
    title_font = pygame.font.SysFont("Arial", 17, bold=True)

    boids, predators, obstacles = setup_flock()
    rules = Rules()

    speed = 1.0
    show_trails = True
    show_debug = False
    show_help = True
    paused = False
    frame = 0
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_UP:
                    speed = min(3.0, round(speed + 0.2, 1))
                elif event.key == pygame.K_DOWN:
                    speed = max(0.2, round(speed - 0.2, 1))
                elif event.key == pygame.K_k:
                    for b in boids:
                        b.kind = random.choice([1, 2, 3])
                        b.set_type()
                elif event.key == pygame.K_t:
                    show_trails = not show_trails
                elif event.key == pygame.K_d:
                    show_debug = not show_debug
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_h:
                    show_help = not show_help
                elif event.key == pygame.K_j:
                    rules.join = not rules.join
                elif event.key == pygame.K_1:
                    rules.sep = not rules.sep
                elif event.key == pygame.K_2:
                    rules.align = not rules.align
                elif event.key == pygame.K_3:
                    rules.coh = not rules.coh
                elif event.key == pygame.K_e:
                    rules.evade = not rules.evade
                elif event.key == pygame.K_o:
                    rules.avoid_obs = not rules.avoid_obs
                elif event.key == pygame.K_a:
                    for _ in range(60):
                        r = random.uniform(32.0, 52.0)
                        x = random.uniform(150, WIDTH - 150)
                        y = random.uniform(120, HEIGHT - 120)
                        if all(math.hypot(x - o.x, y - o.y) >= r + o.r + 25.0 for o in obstacles):
                            obstacles.append(Obstacle(x, y, r))
                            break
                elif event.key == pygame.K_z:
                    if obstacles:
                        obstacles.pop()
                elif event.key == pygame.K_c:
                    obstacles.clear()
                elif event.key == pygame.K_x:
                    predators.clear()
                elif event.key == pygame.K_r:
                    boids, predators, obstacles = setup_flock()
                    rules = Rules()
                    speed = 1.0
                    frame = 0
                    paused = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if event.button == 1:
                    boids.append(Boid(mx, my, kind=random.choice([1, 2, 3])))
                elif event.button == 3:
                    predators.append(Predator(mx, my))

        if not paused:
            update_flock(boids, predators, obstacles, rules, speed)
            frame += 1

        screen.fill(BG_COLOR)

        for obs in obstacles:
            obs.draw(screen)
        for b in boids:
            b.draw(screen, show_trails, show_debug)
        for p in predators:
            p.draw(screen, show_trails, show_debug)

        draw_hud(screen, font, title_font, boids, predators, obstacles, rules, speed, paused, frame)
        if show_help:
            draw_help(screen, font)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()