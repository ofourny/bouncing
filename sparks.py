import math
import random

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