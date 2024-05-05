import pymunk
import random
import pygame
from draw import safe_draw_circle


def add_walls(space, screen_width, screen_height):
    """Adds walls to the pymunk Space to create a boundary."""
    center_x = screen_width // 2
    walls = [
        pymunk.Segment(space.static_body, (center_x - 300, 0), (center_x - 300, 1080), 1),  # Left wall
        pymunk.Segment(space.static_body, (center_x - 300, 1080), (center_x + 300, 1080), 1),  # Bottom wall
        pymunk.Segment(space.static_body, (center_x + 300, 1080), (center_x + 300, 0), 1),  # Right wall
        pymunk.Segment(space.static_body, (center_x + 300, 0), (center_x - 300, 0), 1)  # Top wall
    ]
    for wall in walls:
        wall.elasticity = 0.9
        wall.friction = 0.5
    space.add(*walls)

def setup_space():
    space = pymunk.Space()
    space.gravity = (0, 900)  # Adjust gravity to match your game's theme
    return space


def add_ball(space, color, elasticity, circle_center_x):
    """Adds a ball to the pymunk Space with random properties."""
    mass = 1.0
    radius = 30
    inertia = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, inertia)
    x = random.randint(-20, 20)
    body.position = circle_center_x + x, 50
    shape = pymunk.Circle(body, radius)
    shape.color = color
    shape.elasticity = elasticity
    space.add(body, shape)
    return shape


def add_main_ball(space, color, elasticity, screen_width, screen_height):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    # Specify the position
    body.position = (screen_width / 2, screen_height / 2)

    shape = pymunk.Circle(body, 200 + 10)
    shape.color = color
    shape.elasticity = elasticity
    space.add(body, shape)
    return shape

def draw_balls(screen, balls):
    for ball in balls:
        pos = int(ball.body.position.x), int(ball.body.position.y)
        safe_draw_circle(screen, (255, 255, 255), int(ball.body.position.x), int(ball.body.position.y), int(ball.radius + 2))
        pygame.draw.circle(screen, ball.color, pos, int(ball.radius))