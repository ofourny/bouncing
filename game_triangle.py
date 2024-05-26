import pygame
import sys
import math
import pygame.gfxdraw
import mido
from mido import MidiFile, Message, MidiTrack
import random
import pygame.midi
from pydub import AudioSegment
import time
import threading
import colorsys
import multiprocessing
import pymunk

# Initialize Pygame modules
pygame.midi.init()
pygame.init()
pygame.font.init()

# Screen dimensions and settings
screen_width, screen_height = 1920, 1080
screen = pygame.display.set_mode((screen_width, screen_height))

# MIDI settings and file path
midi_path = 'mid/ball12.mid'
midi_file = mido.MidiFile(midi_path, clip=True)
output_id = pygame.midi.get_default_output_id()  # Get the default MIDI output ID

channel = pygame.mixer.Channel(0)

# Dictionary to keep track of the current instrument for each channel
current_instruments = {i: None for i in range(16)}  # MIDI channels 0-15

outport = mido.open_output(mido.get_output_names()[0])  # Open a MIDI output port with mido

# Audio settings
freq = 192000  # Audio CD quality
bitsize = -16  # Unsigned 16 bit
channels = 2  # 1 is mono, 2 is stereo
buffer = 1024  # Number of samples
pygame.mixer.init(freq, bitsize, channels, buffer)
pygame.mixer.music.set_volume(0.9)  # Set volume to 70%

# Create channels for multiple sound effects
channel = pygame.mixer.Channel(0)

# Game physics and gameplay settings
gravity = 15  # Adjust the gravity effect here
bounce_factor = 5  # Bounce factor; values >1 will make the ball bounce higher
bounce_count = 0
current_note_index = 0
decrement_speed = 20
general_opacity = 230
collision_cooldown = 0
acceleration_factor = 1.025
max_acceleration_factor = 2
ball_size_small = 49
ball_size = 10

# Damping settings
initial_damping = 1.6  # Initial growth factor, starting high
damping_decrease = 0.9  # Factor by which the damping decreases each time
minimum_damping = 1.02  # Minimum damping factor to prevent growth from stopping entirely
damping_decay_rate = 0.1
damping_factor = initial_damping  # Initialize the damping variable at the start of the game

# Circle settings for graphics and collision
circle_center_x, circle_center_y = screen_width / 2, screen_height / 2
circle_center = [circle_center_x, circle_center_y]
circle_radius = 300
circle_thickness = 10
outer_circle_radius_increment = 0

# Color and drawing settings
black = (0, 0, 0)
rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
rainbow_colors_shifted = rainbow_colors
segment_angle = 360 / len(rainbow_colors)
current_color_index = 0
trail_current_color_index = 0
circle_color = rainbow_colors[current_color_index]
trail_color = rainbow_colors[trail_current_color_index]
color_change_duration = 2.0  # Duration in seconds to complete a color transition
trail_color_change_duration = 1.0  # Duration in seconds to complete a color transition
color_change_timer = 0.0  # Timer to track the color transition progress
trail_color_change_timer = 0.0  # Timer to track the color transition progress
next_color_index = (current_color_index + 1) % len(rainbow_colors)
trail_next_color_index = (trail_current_color_index + 1) % len(rainbow_colors)
interpolation_factor = 0.0  # Factor to interpolate between current and next color
max_ball_size = 300
increase_factor = 0.1

# Font settings for text display
debug_font = pygame.font.SysFont('Comic Sans Ms', 16)
debug_font2 = pygame.font.SysFont('Comic Sans Ms', 24)
# Fullscreen setting
FullScreen = True  # Variable to keep track of fullscreen status

# Clock for controlling frame rate
clock = pygame.time.Clock()

# System management and event tracking
done = 0
done2 = 0
ftime = 0
dtcount = 0
cpt = 0
vertex_shift = math.radians(1)  # Shift each vertex by 5 degrees upon being hit

# Initial vertex angles for the equilateral triangle
vertex_angles = [i * 2 * math.pi / 3 for i in range(3)]  # 0, 120, and 240 degrees

balls = [
    {
        'speed': [0, 0],
        'size': ball_size,
        'color': (255, 255, 255),
        'type': 'main',
        'pos': [
            circle_center[0] + circle_radius * math.cos(vertex_angles[0]),
            circle_center[1] + circle_radius * math.sin(vertex_angles[0])
        ],
        'target_index': 1
    },
    {
        'speed': [0, 0],
        'size': ball_size,
        'color': (255, 255, 255),
        'type': 'main',
        'pos': [
            circle_center[0] + circle_radius * math.cos(vertex_angles[1]),
            circle_center[1] + circle_radius * math.sin(vertex_angles[1])
        ],
        'target_index': 2
    },
    {
        'speed': [0, 0],
        'size': ball_size,
        'color': (255, 255, 255),
        'type': 'main',
        'pos': [
            circle_center[0] + circle_radius * math.cos(vertex_angles[2]),
            circle_center[1] + circle_radius * math.sin(vertex_angles[2])
        ],
        'target_index': 0
    }
]
# Global variable to store rainbow balls
rainbow_balls = []
frozen_balls = []
lines = []
trail_positions = []
spark_trails = []  # Store ongoing spark trails

# Assuming a BPM that you might want to dynamically adjust according to your MIDI file
bpm = 130  # Default BPM, but consider extracting this from the MIDI file if it varies
ticks_per_beat = midi_file.ticks_per_beat
current_midi_tick = 0  # This will track where in the MIDI file we are
seconds_per_tick = 60.0 / (bpm * ticks_per_beat)

ticks_per_second = ticks_per_beat * (bpm / 60)
segment_length_ticks = int(ticks_per_second)

last_play_time = 0

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

def ensure_color_values(color):
    """Ensure all color components are within the 0-255 range, increasing brightness."""
    return tuple(min(255, int(c + 0.2 * (255 - c))) for c in color)  # Increase color brightness

def apply_glow_effect(surface, position, color, radius):
    """Apply a glow effect by drawing multiple concentric circles with increasing alpha."""
    glow_intensity = 10  # Number of layers
    for i in range(glow_intensity):
        alpha = int(120 * (1 - i / glow_intensity))  # Decrease alpha gradually
        glow_color = (*color, alpha)  # Create RGBA from RGB
        temp_surface = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, glow_color, (radius, radius), radius - i * (radius / glow_intensity))
        surface.blit(temp_surface, (position[0] - radius, position[1] - radius), special_flags=pygame.BLEND_RGBA_ADD)


def update_instruments():
    for track in midi_file.tracks:
        for msg in track:
            if msg.type == 'program_change':
                current_instruments[msg.channel] = msg.program

# Helper functions for color manipulation
def lighten_color(color, amount=0.5):
    """Lightens the given color by multiplying (1-luminosity) by the given amount."""
    return tuple(min(255, int(c + (255 - c) * amount)) for c in color)


def darken_color(color, amount=0.5):
    """Darkens the given color by multiplying (1-luminosity) by the given amount."""
    return tuple(max(0, int(c * (1 - amount))) for c in color)


def fade_to_white(color, fade_factor):
    """Gradually fades the given color towards white by the fade factor."""
    new_color = [min(255, int(c + fade_factor * (255 - c))) for c in color]
    return tuple(new_color)


def fade_to_black(color, fade_factor):
    """Gradually fades the given color towards black by the fade factor."""
    new_color = [max(0, int(c * (1 - fade_factor))) for c in color]
    return tuple(new_color)


def interpolate_color(color_start, color_end, factor):
    """Interpolate between two colors by a factor between 0 and 1."""
    red = round(color_start[0] + (color_end[0] - color_start[0]) * factor)
    green = round(color_start[1] + (color_end[1] - color_start[1]) * factor)
    blue = round(color_start[2] + (color_end[2] - color_start[2]) * factor)
    return (int(min(255, max(0, red))), int(min(255, max(0, green))), int(min(255, max(0, blue))))

def shift_colors(rainbow_colors, shift_factor):
    """Shift all colors in the rainbow_colors list towards the next color."""
    new_colors = []
    for i in range(len(rainbow_colors)):
        current_color = rainbow_colors[i]
        next_color = rainbow_colors[(i + 1) % len(rainbow_colors)]
        interpolated_color = interpolate_color(current_color, next_color, shift_factor)
        new_colors.append(interpolated_color)
    return new_colors

# Function to play background audio
def play_audio(index, file_path):
    try:
        sound = pygame.mixer.Sound(file_path)
        channel.play(sound)

        # Keep the program running until the music stops
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(2.5)
    except Exception as e:
        print(f"Error occurred: {e}")


def background_audio_player(index, file_path):
    """Function to play audio in the background."""
    thread = threading.Thread(target=play_audio, args=(index, file_path,))
    thread.start()


# Function to update damping factor
def update_damping():
    global damping_factor
    if damping_factor > minimum_damping:
        damping_factor *= (1 - damping_decay_rate)
        damping_factor = max(damping_factor, minimum_damping)


def safe_draw_circle(screen, color, pos_x, pos_y, radius):
    # Ensure the x and y positions are within the screen boundaries
    pos_x = int(max(0, min(screen.get_width(), pos_x)))
    pos_y = int(max(0, min(screen.get_height(), pos_y)))

    # Ensure the radius is non-negative and within a reasonable size
    radius = int(max(1, min(screen.get_height() // 2, radius)))  # Avoid overly large or negative radii

    # Use pygame's gfxdraw to draw the circle with the adjusted parameters
    pygame.gfxdraw.filled_circle(screen, pos_x, pos_y, radius, color)


def add_ball(space, color, elasticity):
    global circle_center_x

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

def add_main_ball(space, color, elasticity):
    global circle_center_x, circle_center_y, circle_radius

    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    # Specify the position
    body.position = (screen_width / 2, screen_height / 2)

    shape = pymunk.Circle(body, 200 + 10)
    shape.color = color
    shape.elasticity = elasticity
    space.add(body, shape)
    return shape

def setup_space():
    space = pymunk.Space()
    space.gravity = (0, 900)  # Adjust gravity to match your game's theme
    return space

def draw_balls(screen, balls):
    """Draws balls on the Pygame screen with their specified colors."""
    for ball in balls:
        pos = int(ball.body.position.x), int(ball.body.position.y)
        safe_draw_circle(screen, (255, 255, 255), int(ball.body.position.x), int(ball.body.position.y), int(ball.radius + 2))
        pygame.draw.circle(screen, ball.color, pos, int(ball.radius))


draw_circle_color = circle_color
def change_color(dt):
    global color_change_timer, next_color_index, rainbow_colors, current_color_index, circle_color

    # Update the color change timer and interpolation factor
    color_change_timer += dt * 50
    if color_change_timer >= color_change_duration:
        color_change_timer -= color_change_duration
        current_color_index = next_color_index
        next_color_index = (current_color_index + 1) % len(rainbow_colors)
    interpolation_factor = color_change_timer / color_change_duration

    # Calculate the current color
    current_color = rainbow_colors[current_color_index]
    next_color = rainbow_colors[next_color_index]
    circle_color = interpolate_color(current_color, next_color, interpolation_factor)
    circle_color = ensure_color_values(circle_color + (general_opacity,))

ball_speed = 800  # pixels per second
max_speed = 2000


def update_triangle_ball(index, ball, dt):
    global max_speed, circle_center, circle_radius, spark_trails, bounce_count, vertex_angles, vertex_shift,ball_speed, color_index, draw_circle_color

    target_index = ball['target_index']
    target_angle = vertex_angles[target_index]
    target_x = circle_center[0] + circle_radius * math.cos(target_angle)
    target_y = circle_center[1] + circle_radius * math.sin(target_angle)

    vector_x = target_x - ball['pos'][0]
    vector_y = target_y - ball['pos'][1]
    distance_to_target = math.sqrt(vector_x ** 2 + vector_y ** 2)

    # Move the ball towards the target
    if distance_to_target > ball_speed * dt:
        norm_factor = ball_speed * dt / distance_to_target
        ball['pos'][0] += vector_x * norm_factor
        ball['pos'][1] += vector_y * norm_factor
    else:

        if(index == 0):
            #handle_bounce(outport, midi_track, bpm)
            background_audio_player(index, 'output_{:04d}.mp3'.format(bounce_count))  # Uncomment to enable dynamic sound playback
            bounce_count += 1



            if(ball_speed < max_speed):
                ball_speed = ball_speed * acceleration_factor

            initiate_sparks_on_collision(spark_trails, [target_x, target_y])

            color_collision_angle = math.atan2(vector_x, vector_y) * 180 / math.pi % 360
            color_index = int(color_collision_angle // segment_angle)
            draw_circle_color = circle_color
            change_color(dt)

        # Ball reaches the vertex, update position to the vertex and shift the vertex
        ball['pos'][0], ball['pos'][1] = target_x, target_y
        ball['target_index'] = (target_index + 1) % 3

        # Shift the vertex angle slightly
        vertex_angles[target_index] += vertex_shift


def interpolate_trail_positions(start_pos, end_pos, steps):
    x_step = (end_pos[0] - start_pos[0]) / steps
    y_step = (end_pos[1] - start_pos[1]) / steps
    return [(start_pos[0] + x_step * i, start_pos[1] + y_step * i) for i in range(steps)]

def initiate_sparks_on_collision(spark_trails, collision_point):
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
            'life': spark_duration
        }
        sparks.append(spark)

    spark_trails.append(sparks)


def play_next_note(outport, midi_track, current_note_index):
    while current_note_index < len(midi_track):
        msg = midi_track[current_note_index]
        # Increment index immediately to avoid getting stuck on a message
        current_note_index += 1

        if msg.type == 'note_on' and msg.velocity > 0:  # Check for playable 'note_on' message
            outport.send(msg)
            # Calculate the time until the corresponding 'note_off'
            duration_ticks = 0
            for next_msg in midi_track[current_note_index:]:  # Start from the current index
                duration_ticks += next_msg.time
                if (next_msg.type == 'note_off' and next_msg.note == msg.note) or \
                   (next_msg.type == 'note_on' and next_msg.note == msg.note and next_msg.velocity == 0):
                    break

            # Convert ticks to seconds and delay
            duration_seconds = duration_ticks * seconds_per_tick

            # Send 'note_off' message
            off_msg = mido.Message('note_off', channel=msg.channel, note=msg.note, velocity=64, time=0)
            outport.send(off_msg)

            return current_note_index  # Return the updated index after playing the note

    return current_note_index  # Return the index if the end of the track is reached without a 'note_on'



def handle_bounce(outport, midi_track, bpm):
    global current_note_index  # Tracks the current position in the MIDI track
    current_note_index = play_next_note(outport, midi_track, current_note_index)

def shift_rainbow_colors(shift_amount):
    global rainbow_colors_shifted
    shifted_colors = []

    # Calculate the amount to shift each color
    hue_shift = shift_amount / len(rainbow_colors_shifted)

    # Shift each color in the rainbow_colors table
    for color in rainbow_colors_shifted:
        # Convert RGB color to HSV color
        hsv_color = colorsys.rgb_to_hsv(color[0] / 255, color[1] / 255, color[2] / 255)

        # Shift the hue component
        shifted_hue = (hsv_color[0] + hue_shift) % 1.0

        # Convert back to RGB color
        rgb_color = colorsys.hsv_to_rgb(shifted_hue, hsv_color[1], hsv_color[2])

        # Scale RGB values to 0-255 range and append to shifted_colors
        shifted_colors.append((int(rgb_color[0] * 255), int(rgb_color[1] * 255), int(rgb_color[2] * 255)))

    # Update rainbow_colors with shifted_colors
    rainbow_colors_shifted = shifted_colors




# Assuming you have some track selected for this
midi_track = midi_file.tracks[0]  # Select the appropriate trackss that contains the notes
current_note_index = 0  # Initialize the note index


# Function to render text onto the screen
def draw_text(surface, text, position, font, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def ensure_color_values(color):
    """Ensure all color components are within the 0-255 range."""
    return tuple(min(255, max(0, int(c))) for c in color)

update_instruments()

def play_full_midi(midi_file, outport, bpm=130):
    ticks_per_beat = midi_file.ticks_per_beat
    seconds_per_tick = 60.0 / (bpm * ticks_per_beat)

    last_event_time = 0
    start_time = time.time()

    try:
        for track in midi_file.tracks:
            for msg in track:
                if not msg.is_meta:
                    current_event_time = last_event_time + msg.time * seconds_per_tick
                    while time.time() - start_time < current_event_time:
                        time.sleep(0.001)  # Sleep briefly to prevent a tight loop
                    outport.send(msg)
                    last_event_time = current_event_time
    except Exception as e:
        print(f"Error during MIDI playback: {e}")

    print("MIDI playback finished.")

# Function to start MIDI playback in a background thread
def start_midi_playback():
    threading.Thread(target=play_full_midi, args=(midi_file, outport)).start()


def change_instrument(outport, channel, program):
    """
    Change the instrument on a specific MIDI channel.

    Parameters:
    - outport: A Mido port object for output.
    - channel: MIDI channel (0-15).
    - program: Program number (0-127) corresponding to the instrument.
    """
    # Create a program change message
    msg = mido.Message('program_change', channel=channel, program=program)

    # Send the message through the output port
    outport.send(msg)
    print(f"Instrument changed on channel {channel} to program {program}")


def change_volume(outport, channel, volume):
    """
    Change the volume on a specific MIDI channel.

    Parameters:
    - outport: A Mido port object for output.
    - channel: MIDI channel (0-15).
    - volume: Volume level (0-127).
    """
    # Make sure the volume is within the MIDI range
    volume = max(0, min(127, volume))

    # Create a control change message for volume (controller number 7)
    msg = mido.Message('control_change', channel=channel, control=7, value=volume)

    # Send the message through the output port
    outport.send(msg)
    print(f"Volume set to {volume} on channel {channel}")

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

def draw_sparks(screen, spark_trails, color):
    # Iterate over each list of sparks in the spark trails
    for sparks in spark_trails:
        for spark in sparks:
            # Extract the position from the spark dictionary
            position = spark['position']
            # Draw each spark as a small circle at its position
            pygame.draw.circle(screen, color, (int(position[0]), int(position[1])), 2)


change_volume(outport, channel=0, volume=100)
timebefore = 0
instrucount = 81

#11 #12 #57 #58 #64 #70
#81 #82 electronic
#87 88
#95
#99 electro chinese
#100 synthe
#106 instruc exo
#109 tube
#112 trompet
#113 xylo
#115 marimba

change_instrument(outport, channel=0, program=instrucount)

space = setup_space()
add_walls(space, screen_width, screen_height)

#big_ball = add_main_ball(space, circle_color, 1.2)

# Create a persistent surface
persistent_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
persistent_surface.set_alpha(255)  # Optional: set transparency for the persistent surface



# Game loop
while True:

    dt = clock.tick(120) / 1000  # Delta time in seconds

    ftime = ftime + dt
    dtcount += dt

    if(ftime > 25):
        max_speed = 2500

    if(ftime > 32):
        max_speed = 5000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            outport.close()
            pygame.midi.quit()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                if FullScreen:
                    Ekran = pygame.display.set_mode((910, 540))
                    FullScreen = False
                else:
                    Ekran = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    FullScreen = True
        if event.type == pygame.QUIT:
            run = False

    # Update each ball
    for index, ball in enumerate(balls):
        update_triangle_ball(index, ball, dt)


    if outer_circle_radius_increment > 0:
        outer_circle_radius_increment -= 1 * dt * decrement_speed
        decrement_speed = decrement_speed * 1.004

    screen.fill(black)

    # Outer circle for expansion effect
    expanded_radius = int(circle_radius + outer_circle_radius_increment)
    outer_circle_color = darken_color(draw_circle_color, 0.2)
    pygame.gfxdraw.filled_circle(screen, int(circle_center[0]), int(circle_center[1]), expanded_radius + circle_thickness, outer_circle_color)


    # Circle with lighter outside area
    lighter_circle_color = lighten_color(draw_circle_color, 0.3)
    pygame.gfxdraw.filled_circle(screen, int(circle_center[0]), int(circle_center[1]), circle_radius, lighter_circle_color)
    pygame.gfxdraw.filled_circle(screen, int(circle_center[0]), int(circle_center[1]), circle_radius - circle_thickness, black)

    draw_text(screen, '@musique.ball', (circle_center_x-50, circle_center_y),
              debug_font, (150,150,150))

    border_thickness = 4

    update_sparks(spark_trails, dt)

    draw_sparks(screen, spark_trails, circle_color)

    # Ball with border
    for index, ball in enumerate(balls):
        # Draw the inner circle using the safe draw function
        safe_draw_circle(persistent_surface, circle_color, int(ball['pos'][0]), int(ball['pos'][1]), int(ball['size'] / 2) + 2)
        safe_draw_circle(persistent_surface, (0, 0, 0), int(ball['pos'][0]), int(ball['pos'][1]), int(ball['size'] / 2))

    screen.blit(persistent_surface, (0, 0))


    for index, ball in enumerate(balls):
        # Draw the inner circle using the safe draw function
        safe_draw_circle(screen, (255,255,255), int(ball['pos'][0]), int(ball['pos'][1]), int(ball['size'] / 2))

    pygame.display.flip()
