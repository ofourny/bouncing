import pygame
import sys
import math
import pygame.gfxdraw
import mido
import random
import pygame.midi

pygame.midi.init()

# Get the default MIDI output ID
output_id = pygame.midi.get_default_output_id()

# Open the default MIDI output
midi_output = pygame.midi.Output(1)

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width, screen_height = 1920, 1080
screen = pygame.display.set_mode((screen_width, screen_height))

# Path to your MIDI file
midi_path = 'ball4_2.mid'

# Load the MIDI file
midi_file = mido.MidiFile(midi_path, clip=True)

# Cap the ball's speed to prevent it from becoming too fast
max_speed = 500  # Adjust as needed
gravity = 7.6  # Adjust the gravity effect here
bounce_factor = 10  # Bounce factor; values >1 will make the ball bounce higher
max_bounce_factor = 30
bounce_count = 0
decrement_speed = 20
general_opacity = 4

# Constants
initial_damping = 1.6  # Initial growth factor, starting high
damping_decrease = 0.9  # Factor by which the damping decreases each time
minimum_damping = 1.02  # Minimum damping factor to prevent growth from stopping entirely
damping_decay_rate = 0.1

# Initialize the damping variable at the start of the game
damping_factor = initial_damping


# Circle's center and radius for boundary collision
circle_center_x, circle_center_y = screen_width / 2, screen_height / 2
circle_center = [circle_center_x, circle_center_y]

pygame.font.init()  # Don't forget to initialize the font module
pygame.mixer.init()
debug_font = pygame.font.SysFont('Comic Sans Ms', 18)

# Keep track of the current note index
current_note_index = 0


# Create an RGBA color by adding the alpha value to the existing RGB color
def ensure_color_values(color):
    return tuple(min(255, max(0, int(c))) for c in color)

def update_damping():
    global damping_factor
    if damping_factor > minimum_damping:
        damping_factor *= (1 - damping_decay_rate)
        damping_factor = max(damping_factor, minimum_damping)

#92

freq = 192000    # audio CD quality
bitsize = -16   # unsigned 16 bit
channels = 2    # 1 is mono, 2 is stereo
buffer = 1024    # number of samples
pygame.mixer.init(freq, bitsize, channels, buffer)

# optional volume 0 to 1.0
pygame.mixer.music.set_volume(0.6)

trail_max_position = 1000

def spawn_second_ball():
    global second_ball, second_ball_spawned
    second_ball_pos = [ball_pos[0] + ball_size, ball_pos[1]]
    second_ball_speed = [random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)]
    second_ball = [second_ball_pos, second_ball_speed, second_ball_size]
    second_ball_spawned = True

def update_ball(ball, dt):
    # Update position based on speed
    ball[0][0] += ball[1][0] * dt
    ball[0][1] += ball[1][1] * dt
    # Gravity effect
    ball[1][1] += gravity * dt
    # Limit speed
    ball[1][0] = max(-max_speed, min(max_speed, ball[1][0]))
    ball[1][1] = max(-max_speed, min(max_speed, ball[1][1]))

def check_collision(ball1, ball2):
    dx, dy = ball1[0][0] - ball2[0][0], ball1[0][1] - ball2[0][1]
    distance = math.sqrt(dx**2 + dy**2)
    if distance < ball1[2] + ball2[2]:
        return True, dx, dy, distance
    return False, dx, dy, distance

def handle_collisions():
    global bounce_count
    # Check collisions between primary ball and screen boundary
    if ball_pos[0] - ball_size <= 0 or ball_pos[0] + ball_size >= screen_width:
        ball_speed[0] *= -bounce_factor
    if ball_pos[1] - ball_size <= 0 or ball_pos[1] + ball_size >= screen_height:
        ball_speed[1] *= -bounce_factor
        bounce_count += 1
        if bounce_count == 50:
            spawn_second_ball()

    # Check collisions between primary and secondary ball
    if second_ball_spawned:
        collided, dx, dy, dist = check_collision([ball_pos, ball_speed, ball_size], second_ball)
        if collided:
            # Elastic collision response (simplified)
            ball_speed[0], second_ball[1][0] = second_ball[1][0], ball_speed[0]
            ball_speed[1], second_ball[1][1] = second_ball[1][1], ball_speed[1]

            # Draw line on collision
            lines.append((ball_pos.copy(), second_ball[0].copy()))

# Function to play MIDI notes at a specific second
def play_notes_at_second(second):
    ticks_per_second = midi_file.ticks_per_beat * 0.0005  # Assuming 120 BPM

    # Calculate start and end ticks for the desired second
    start_tick = ticks_per_second * second
    end_tick = ticks_per_second * (second + 1)
    current_tick = 0

    for msg in midi_file:
        current_tick += msg.time
        if start_tick <= current_tick < end_tick:
            if msg.type == 'note_on':
                midi_output.note_on(msg.note, msg.velocity)
            elif msg.type == 'note_off':
                midi_output.note_off(msg.note, msg.velocity)
        elif current_tick >= end_tick:
            break

def lighten_color(color, amount=0.5):
    """Lightens the given color by multiplying (1-luminosity) by the given amount."""
    return tuple(min(255, int(c + (255 - c) * amount)) for c in color)

def darken_color(color, amount=0.5):
    """Darkens the given color by multiplying (1-luminosity) by the given amount."""
    return tuple(max(0, int(c * (1 - amount))) for c in color)

def interpolate_color(color_start, color_end, factor):
    red = round(color_start[0] + (color_end[0] - color_start[0]) * factor)
    green = round(color_start[1] + (color_end[1] - color_start[1]) * factor)
    blue = round(color_start[2] + (color_end[2] - color_start[2]) * factor)
    return (int(min(255, max(0, red))), int(min(255, max(0, green))), int(min(255, max(0, blue))))

# Define the draw_text function
def draw_text(surface, text, position, font, color=(255, 255, 255)):
    """Render text onto the screen."""
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

# Colors
black = (0, 0, 0)
rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
segment_angle = 360 / len(rainbow_colors)
current_color_index = 0
circle_color = rainbow_colors[current_color_index]

circle_radius = 250
circle_thickness = 10
outer_circle_radius_increment = 0

# Primary ball settings
ball_size = 5
ball_pos = [circle_center[0], circle_center[1] - 50]
ball_speed = [-0.01, 0]
ball_color = (0, 0, 0)  # black

# Secondary ball settings
second_ball = None
second_ball_size = 3
second_ball_spawned = False

# Trailing effect storage
trail_positions = []

# Lines storage for dynamic drawing between inner circle and ball center
lines = []

# Clock to control the frame rate
clock = pygame.time.Clock()

color_change_duration = 1.0  # Duration in seconds to complete a color transition
color_change_timer = 0.0  # Timer to track the color transition progress
current_color_index = 0  # Start with the first color
next_color_index = (current_color_index + 1) % len(rainbow_colors)
interpolation_factor = 0.0  # Factor to interpolate between current and next color

# Initialize the cooldown timer
collision_cooldown = 0
acceleration_factor = 1.2
max_acceleration_factor = 3

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
FullScreen = True

# 5 38 27
inst = 5
midi_output.set_instrument(38)

dtcount = 0

# Game loop
while True:
    dt = clock.tick(60) / 1000  # Delta time in seconds

    dtcount += dt

#    if(dtcount > 3) :
#        inst += 1
#        dtcount = 0
#        midi_output.set_instrument(inst)
#        print("switch")
#        print(inst)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            midi_output.close()
            pygame.midi.quit()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                if FullScreen:
                    Ekran = pygame.display.set_mode((ScreenSizeMinx, ScreenSizeMiny))
                    FullScreen = False
                else:
                    Ekran = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    FullScreen = True
        if event.type == pygame.QUIT:
            run = False

    # Inside the game loop, after processing events and before rendering
    ball_pos[0] += ball_speed[0] * dt
    ball_pos[1] += ball_speed[1] * dt

    ball_radius = ball_size / 2

    # Inside the game loop, when updating trail_positions
    trail_positions.insert(0, (ball_pos[0], ball_pos[1], circle_color, ball_size/2))
    if len(trail_positions) > trail_max_position:
        trail_positions.pop()

    # Inside the game loop, before handling collisions
    if collision_cooldown > 0:
        collision_cooldown -= dt  # Decrease cooldown timer by the elapsed time



    # Calculate the vector from the circle's center to the ball's center
    dx, dy = ball_pos[0] - circle_center[0], ball_pos[1] - circle_center[1]
    distance = math.sqrt(dx**2 + dy**2)

    # Calculate normal vector from the circle center to the ball center
    if distance != 0:
        nx, ny = dx / distance, dy / distance
    else:
        nx, ny = 0, 0

    adjusted_collision_radius = circle_radius - circle_thickness - ball_radius

    # Check collision with the circle's boundary considering the thickness
    if distance >= adjusted_collision_radius :
        # Reflect ball's velocity
        dot = ball_speed[0] * nx + ball_speed[1] * ny
        ball_speed[0] -= 2 * dot * nx
        ball_speed[1] -= 2 * dot * ny

        # Apply bounce factor and subtract gravity to simulate energy loss
        ball_speed[0] *= bounce_factor
        ball_speed[1] *= bounce_factor - gravity

        # Ensure ball is placed just outside the circle considering its radius
        overlap = (distance + ball_radius) - (circle_radius - circle_thickness)
        ball_pos[0] -= overlap * nx
        ball_pos[1] -= overlap * ny

        # Calculate the corrected collision point at the inner boundary
        collision_angle = math.atan2(dy, dx)
        adjusted_radius = circle_radius - circle_thickness

        # Calculate the collision point based on the adjusted radius and collision angle
        collision_point = (
            circle_center_x + adjusted_radius * math.cos(collision_angle),
            circle_center_y + adjusted_radius * math.sin(collision_angle)
        )

        color_collision_angle = math.atan2(dy, dx) * 180 / math.pi % 360
        color_index = int(color_collision_angle // segment_angle)
        collision_color = rainbow_colors[color_index]
        # Append the collision point and circle color to 'lines'
        lines.append((collision_point, collision_color))

        if( collision_cooldown <= 0) :
            # Increase the ball size with a limit
            if ball_size * damping_factor < 2 * circle_radius:
                ball_size *= damping_factor
            else:
                ball_size = 2 * circle_radius  # or any other maximum size logic

                # Reduce the damping factor, but ensure it does not fall below the minimum
            update_damping()
            collision_cooldown = 0.1

            play_notes_at_second(current_note_index)
            current_note_index = current_note_index + 1
            #trail_max_position = trail_max_position + 2
            acceleration_factor = acceleration_factor + 0.08

            if(bounce_factor < max_bounce_factor):
                bounce_factor = bounce_factor + 0.5

            bounce_count = bounce_count + 1

            # Update the color change timer and interpolation factor
            color_change_timer += dt * 10
            if color_change_timer >= color_change_duration:
                color_change_timer -= color_change_duration
                current_color_index = next_color_index
                next_color_index = (current_color_index + 1) % len(rainbow_colors)
            interpolation_factor = color_change_timer / color_change_duration



            # Calculate the current color
            current_color = rainbow_colors[current_color_index]
            next_color = rainbow_colors[next_color_index]
            circle_color = interpolate_color(current_color, next_color, interpolation_factor)

            outer_circle_radius_increment = outer_circle_radius_increment + 20

            if(general_opacity < 254):
                general_opacity = general_opacity + 1

    ball_speed[1] += gravity

    ball_speed[0] = max(-max_speed, min(max_speed, ball_speed[0]))
    ball_speed[1] = max(-max_speed, min(max_speed, ball_speed[1]))


    if outer_circle_radius_increment > 0:
        outer_circle_radius_increment -= 1 * dt * decrement_speed
        decrement_speed = decrement_speed * 1.001

    # Create a transparent surface
    transparent_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

    screen.fill(black)


    # Apply the function to convert color values before usage
    circle_color_with_transparency = ensure_color_values(circle_color + (general_opacity,))

    transparent_surface.fill(circle_color_with_transparency)

    # Blit the transparent surface onto the screen
    screen.blit(transparent_surface, (0, 0))

    # Outer circle for expansion effect
    expanded_radius = int(circle_radius + outer_circle_radius_increment)
    outer_circle_color = darken_color(circle_color, 0.2)
    pygame.gfxdraw.filled_circle(screen, int(circle_center[0]), int(circle_center[1]), expanded_radius + circle_thickness, outer_circle_color)

    # Circle with lighter outside area
    lighter_circle_color = lighten_color(circle_color, 0.3)
    pygame.gfxdraw.filled_circle(screen, int(circle_center[0]), int(circle_center[1]), circle_radius, lighter_circle_color)
    pygame.gfxdraw.filled_circle(screen, int(circle_center[0]), int(circle_center[1]), circle_radius - circle_thickness, black)

    draw_text(screen, '@musique.ball', (circle_center_x-60, circle_center_y),
              debug_font, (45,45,45))

    border_thickness = 2

    ## When drawing the trailing effect
    for i, (pos_x, pos_y, trail_color, ball_size_s) in enumerate(reversed(trail_positions)):
        #opacity = max(0, 255 - (i * 1))
        #trail_color = trail_color + (opacity,)
        pygame.gfxdraw.filled_circle(screen, int(pos_x), int(pos_y), int(ball_size_s + 1),
                                     (255,255,255))
        pygame.gfxdraw.filled_circle(screen, int(pos_x), int(pos_y), int(ball_size_s), trail_color)

    # When drawing lines from the list 'lines'
    #for collision_point, line_color in lines:
    #    pygame.draw.line(screen, line_color, collision_point,
    #                     (int(ball_pos[0] ), int(ball_pos[1] )), 1)

    # Ball with border
    border_color = (255,255,255)

    pygame.gfxdraw.filled_circle(screen, int(ball_pos[0] ), int(ball_pos[1] ), int(ball_size / 2 + border_thickness), border_color)
    pygame.gfxdraw.filled_circle(screen, int(ball_pos[0] ), int(ball_pos[1] ), int(ball_size / 2), black)

    draw_text(screen, f'Rebonds: {bounce_count}', (circle_center_x-42, circle_center_y+240),
              debug_font, (200,200,200))


    #draw_text(screen, f'Speed: ({ball_speed[0]:.2f}, {ball_speed[1]:.2f})', (circle_center_x, circle_center_y), debug_font)
    #draw_text(screen, f'Ball Pos: ({ball_pos[0]:.2f}, {ball_pos[1]:.2f})', (20, 60), debug_font)
    #Ensure collision_point is defined before trying to display it to avoid errors
    #if 'collision_point' in locals():
    #    draw_text(screen, f'Collision Point: ({collision_point[0]:.2f}, {collision_point[1]:.2f})', (20, 80), debug_font)


    pygame.display.flip()
