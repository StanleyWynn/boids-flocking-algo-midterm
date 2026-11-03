# boids-flocking-algo-midterm
Decentralized Multi-Agent Flocking: An Extended Reynolds Boids Model with Tangential Obstacle Steer and Quorum Dynamics

A 2D flocking simulation built in Python using Pygame, modeling collective motion based on Craig Reynolds' classic Boids algorithm.

Developed as a group midterm project for Introduction to Artificial Intelligence.

## Features

- **300 Autonomous Agents**: Real-time decentralized flocking behavior.
- **Dynamic Coloring**: Boids change colors dynamically based on nearby flock density.
- **Predator Mode**: Toggle an active predator that scatters the flock.
- **Interactive Obstacles**: Place and clear barriers on screen with the mouse.
- **Speed Controls**: Adjust simulation speed on the fly.

---

## How It Works

Each boid follows three simple local rules:

1. **Separation**: Steer to avoid crowding nearby flockmates.
2. **Alignment**: Steer toward the average heading of nearby flockmates.
3. **Cohesion**: Steer toward the center of mass of nearby flockmates.

---

## Controls

| Key / Mouse | Action |
| :--- | :--- |
| **Left Click** | Place an obstacle |
| **Right Click** | Remove nearest obstacle |
| **`P`** | Toggle predator on / off |
| **`UP` / `DOWN`** | Increase / decrease boid speed |
| **`SPACE`** | Pause / resume |
| **`C`** | Clear all obstacles |
| **`R`** | Reset simulation |
| **`ESC`** | Quit |

---

## Getting Started

### Requirements
- Python 3.8+
- Pygame

### Notes / Future improvements
- - **Algorithmic Complexity ($O(N^2)$)**: In the current implementation, every boid checks distance against every other boid each frame. With 300 agents, this takes $\approx 90,000$ distance checks per frame, which runs smoothly on modern CPUs but bounds further scaling.
- **Tuning Sensitivity**: The balance between cohesion and separation is delicate; high separation weights cause jitter, while high cohesion causes unnatural collapse into tight points.

### Future Improvements
- **Spatial Partitioning (Quadtree / Spatial Grid)**: Implementing a 2D spatial hash grid will reduce neighbor queries from $O(N^2)$ to $O(N)$, allowing the simulation to scale to 1,000+ boids.
- **In-Game Parameter Sliders**: Add an interactive HUD to tweak separation, alignment, and cohesion weights in real time without restarting the script.
- **Food / Target Attractors**: Introduce dynamic attractors (e.g., clicking to drop food) to observe competition between foraging and predator evasion.
