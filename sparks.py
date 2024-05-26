import math
import random
import pygame

def initiate_sparks_on_collision(spark_trails, collision_point, color):
    number_of_sparks = 10  # Number of sparks to generate
    spark_duration = 1.0  # Lifetime of each spark in seconds
    sparks = []

    for _ in range(number_of_sparks):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 100)  # Speed of the spark
        velocity = (
            speed * math.cos(angle),
            speed * math.sin(angle)
        )

        spark = {
            'position': collision_point,
            'velocity': velocity,
            'life': spark_duration,
            'color': color
        }
        sparks.append(spark)

    spark_trails.append(sparks)

def update_sparks(spark_trails, dt):
    for trail in spark_trails:
        for spark in trail:
            # Update the spark position based on its velocity and direction
            spark['position'] = (spark['position'][0] + spark['velocity'][0] * dt,
                                 spark['position'][1] + spark['velocity'][1] * dt)
            # Optionally fade out or shrink sparks here
            spark['life'] -= dt
        # Remove sparks that have "expired"
        trail[:] = [spark for spark in trail if spark['life'] > 0]

def draw_sparks(screen, spark_trails):
    # Iterate over each list of sparks in the spark trails
    for sparks in spark_trails:
        for spark in sparks:
            # Extract the position from the spark dictionary
            position = spark['position']
            # Draw each spark as a small circle at its position
            pygame.draw.circle(screen, spark['color'], (int(position[0]), int(position[1])), 2)

def initiate_sparks(start_position, end_position, number_of_sparks=10):
    sparks = []
    for _ in range(number_of_sparks):
        angle = random.uniform(0, 2 * math.pi)  # You might adjust this if you need directional sparks
        distance = random.uniform(0.1, 0.3)  # Distance factor from start towards end
        position = (start_position[0] + distance * (end_position[0] - start_position[0]),
                    start_position[1] + distance * (end_position[1] - start_position[1]))
        velocity = (angle, distance)
        sparks.append((position, velocity))
    return sparks
