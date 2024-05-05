import pygame


def safe_draw_circle(screen, color, pos_x, pos_y, radius):
    # Ensure the x and y positions are within the screen boundaries
    pos_x = int(max(0, min(screen.get_width(), pos_x)))
    pos_y = int(max(0, min(screen.get_height(), pos_y)))

    # Ensure the radius is non-negative and within a reasonable size
    radius = int(max(1, min(screen.get_height() // 2, radius)))  # Avoid overly large or negative radii

    # Use pygame's gfxdraw to draw the circle with the adjusted parameters
    pygame.gfxdraw.filled_circle(screen, pos_x, pos_y, radius, color)
