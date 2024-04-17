import pygame
import sys
import math
import pygame.gfxdraw
import mido
import random
import pygame.midi
from pydub import AudioSegment
import time
import threading

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
gravity = 5.6  # Adjust the gravity effect here
bounce_factor = 1.1  # Bounce factor; values >1 will make the ball bounce higher
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
debug_font = pygame.font.SysFont('Comic Sans Ms', 24)

# Keep track of the current note index
current_note_index = 0

# Initialize Pygame Mixer
pygame.mixer.init()

channel1 = pygame.mixer.Channel(0)  # Create a Channel on index 0
channel2 = pygame.mixer.Channel(1)  # Create another Channel on index 1
channel3 = pygame.mixer.Channel(2)  # Create another Channel on index 1
channel4 = pygame.mixer.Channel(3)  # Create another Channel on index 1

sound1 = pygame.mixer.Sound('ball6_1.mp3')
sound2 = pygame.mixer.Sound('ball6_1.mp3')
sound3 = pygame.mixer.Sound('ball6_1.mp3')
sound4 = pygame.mixer.Sound('ball6_1.mp3')

def play_audio(index, file_path):
    try:

        if(index == 0):
            channel1.play(sound1)
        if(index == 1):
            channel2.play(sound2)
        if(index == 2):
            channel3.play(sound3)
        if(index == 3):
            channel4.play(sound4)

        # Keep the program running until the music stops
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error occurred: {e}")

def background_audio_player(index, file_path):
    """Function to play audio in the background."""
    thread = threading.Thread(target=play_audio, args=(index,file_path,))
    thread.start()


# Create an RGBA color by adding the alpha value to the existing RGB color
def ensure_color_values(color):
    return tuple(min(255, max(0, int(c))) for c in color)

# Global variable to store rainbow balls
rainbow_balls = []

def spawn_rainbow_balls():
    global rainbow_balls
    colors = [
        (255, 0, 0),  # Bright Red
        (255, 165, 0),  # Orange
        (255, 255, 0),  # Bright Yellow
        (0, 255, 0),  # Neon Green
        (0, 255, 255),  # Aqua
        (0, 127, 255),  # Bright Sky Blue
        (255, 0, 255),  # Magenta
        (255, 105, 180),  # Hot Pink
        (127, 255, 0),  # Chartreuse Green
        (255, 20, 147)  # Deep Pink
    ]

    start_x, start_y = circle_center_x, circle_center_y
    for i, color in enumerate(colors):
        angle = i * (360 / len(colors))
        speed_x = 20 * math.cos(math.radians(angle))
        speed_y = 20 * math.sin(math.radians(angle))
        rainbow_balls.append({'pos': [start_x, start_y], 'speed': [speed_x, speed_y], 'size': 20, 'color': color})

freq = 192000    # audio CD quality
bitsize = -16   # unsigned 16 bit
channels = 2    # 1 is mono, 2 is stereo
buffer = 1024    # number of samples
pygame.mixer.init(freq, bitsize, channels, buffer)

# optional volume 0 to 1.0
pygame.mixer.music.set_volume(0.6)

trail_max_position = 1000

def fade_to_white(color, fade_factor):
    """ Gradually fades the given color towards white by the fade factor. """
    new_color = [min(255, int(c + fade_factor * (255 - c))) for c in color]
    return tuple(new_color)

cpt = 1
def update_ball(index, ball, dt):
    global bounce_count, cpt
    max_speed = 500  # Maximum speed limit for any ball

    """ Update the position and speed of a ball based on gravity and boundary collisions. """
    next_x = ball['pos'][0] + ball['speed'][0] * dt
    next_y = ball['pos'][1] + ball['speed'][1] * dt

    # Calculate distance from the center of the circle
    dx, dy = next_x - circle_center_x, next_y - circle_center_y
    distance = math.sqrt(dx**2 + dy**2)

    # Check collision with the circle's boundary
    if distance + ball['size'] / 2 >= circle_radius:
        # Calculate normal vector from the circle center to the ball center
        nx, ny = dx / distance, dy / distance
        # Reflect the ball's velocity and apply the bounce factor
        dot = ball['speed'][0] * nx + ball['speed'][1] * ny
        ball['speed'][0] = (ball['speed'][0] - 2 * dot * nx) * bounce_factor
        ball['speed'][1] = (ball['speed'][1] - 2 * dot * ny) * bounce_factor

        print(ball['size'])
        if(ball['size'] != 20):
            # Fade color to white upon bounce
            ball['color'] = fade_to_white(ball['color'], 0.1)  # Adjust fade factor as needed
            #file_name = 'output_{:04d}.mp3'.format(cpt)
            file_name = 'ball6_1.mp3'

            background_audio_player(index,file_name)
            cpt = cpt + 1

        # Update bounce count
        if(index == 0):
            bounce_count += 1


    else:
        # Update position if no collision
        ball['pos'][0] = next_x
        ball['pos'][1] = next_y

    # Apply gravity (if it makes sense for your simulation)
    ball['speed'][1] += gravity

    # Enforce the maximum speed limit
    speed_magnitude = math.sqrt(ball['speed'][0]**2 + ball['speed'][1]**2)
    if speed_magnitude > max_speed:
        # Normalize the speed vector and multiply by max_speed
        ball['speed'][0] = (ball['speed'][0] / speed_magnitude) * max_speed
        ball['speed'][1] = (ball['speed'][1] / speed_magnitude) * max_speed


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
ball_size = 50
ball_pos = [circle_center[0], circle_center[1] - 50]
ball_speed = [-0.01, 0]
ball_color = (0, 0, 0)  # black

# Ball settings
balls = [
    {'pos': [circle_center_x+10, circle_center_y], 'speed': [20, 20], 'size': ball_size, 'color': (0, 255, 0)},  # Green ball
    {'pos': [circle_center_x, circle_center_y+30], 'speed': [-20, 20], 'size': ball_size, 'color': (255, 0, 0)},  # Red ball
    {'pos': [circle_center_x-10, circle_center_y], 'speed': [20, 20], 'size': ball_size, 'color': (255, 0, 0)},   # Red ball
    {'pos': [circle_center_x, circle_center_y+50], 'speed': [-20, 20], 'size': ball_size, 'color': (255, 0, 0)}  # Red ball
]

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
done = 0
done2 = 0
ftime = 0
# Game loop
while True:
    dt = clock.tick(60) / 1000  # Delta time in seconds

    ftime = ftime + dt

    dtcount += dt
    # Inside the game loop, check for 100 bounces
    if bounce_count == 20 and done == 0:
        spawn_rainbow_balls()  # Spawn rainbow balls at 100 bounces
        done = 1

    if bounce_count == 50 and done2 == 0:
        spawn_rainbow_balls()  # Spawn rainbow balls at 100 bounces
        done2 = 1

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


    if(ftime < 62):
        # Update each ball
        for index, ball in enumerate(balls):
            update_ball(index, ball, dt)

        for index, ball in enumerate(rainbow_balls):
            update_ball(index, ball, dt)

        if outer_circle_radius_increment > 0:
            outer_circle_radius_increment -= 1 * dt * decrement_speed
            decrement_speed = decrement_speed * 1.001

    if(ftime >= 62):
        for index, ball in enumerate(balls):
            if(index == 0):
                ball['color'] =(0, 255, 0)  # Adjust fade factor as needed
            else:
                ball['color'] = (255, 0, 0)  # Adjust fade factor as needed


    # Create a transparent surface
    transparent_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

    screen.fill(black)


    # Apply the function to convert color values before usage
    circle_color_with_transparency = ensure_color_values(circle_color + (general_opacity,))

    transparent_surface.fill(circle_color_with_transparency)

    # Blit the transparent surface onto the screen
    screen.blit(transparent_surface, (0, 0))

    # Circle with lighter outside area
    lighter_circle_color = lighten_color(circle_color, 0.3)
    pygame.gfxdraw.filled_circle(screen, int(circle_center[0]), int(circle_center[1]), circle_radius, lighter_circle_color)
    pygame.gfxdraw.filled_circle(screen, int(circle_center[0]), int(circle_center[1]), circle_radius - circle_thickness, black)

    draw_text(screen, '@musique.ball', (circle_center_x-60, circle_center_y),
              debug_font, (45,45,45))

    border_thickness = 2

    # Ball with border
    border_color = (255,255,255)

    for ball in balls:
        # Draw the border circle with added border thickness
        pygame.gfxdraw.filled_circle(screen, int(ball['pos'][0]), int(ball['pos'][1]), int(ball['size'] / 2 + border_thickness), border_color)
        pygame.gfxdraw.filled_circle(screen, int(ball['pos'][0]), int(ball['pos'][1]), ball['size'] // 2, ball['color'])

    # Drawing rainbow balls in the game loop
    for ball in rainbow_balls:
        pygame.gfxdraw.filled_circle(screen, int(ball['pos'][0]), int(ball['pos'][1]), ball['size'] // 2, ball['color'])

    draw_text(screen, f'Rebonds: {bounce_count}', (circle_center_x-50, circle_center_y+280),
              debug_font, (200,200,200))

    pygame.display.flip()
