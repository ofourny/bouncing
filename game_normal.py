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
import pymunk
from sparks import initiate_sparks_on_collision, draw_sparks, initiate_sparks, update_sparks
from draw import safe_draw_circle
from color import shift_colors, darken_color, interpolate_color, lighten_color, fade_to_black, fade_to_white


# Initialize Pygame modules
pygame.midi.init()
pygame.init()
pygame.font.init()

# Screen dimensions and settings
screen_width, screen_height = 1920, 1080
screen = pygame.display.set_mode((screen_width, screen_height))

# MIDI settings and file path
midi_path = 'mid/ball10.mid'
midi_file = mido.MidiFile(midi_path, clip=True)
output_id = pygame.midi.get_default_output_id()  # Get the default MIDI output ID

# Assuming you have some track selected for this
midi_track = midi_file.tracks[0]  # Select the appropriate trackss that contains the notes
current_note_index = 0  # Initialize the note index

# Create channels for multiple sound effects
channel1 = pygame.mixer.Channel(0)
channel2 = pygame.mixer.Channel(1)
channel3 = pygame.mixer.Channel(2)
channel4 = pygame.mixer.Channel(3)

# Load sounds
sound1 = pygame.mixer.Sound('mid/ball6_1.mp3')
sound2 = pygame.mixer.Sound('mid/ball6_1.mp3')
sound3 = pygame.mixer.Sound('mid/ball6_1.mp3')
sound4 = pygame.mixer.Sound('mid/ball6_1.mp3')


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

# Game physics and gameplay settings
gravity = 9  # Adjust the gravity effect here
bounce_factor = 50  # Bounce factor; values >1 will make the ball bounce higher
bounce_count = 0
current_note_index = 0
decrement_speed = 20
general_opacity = 230
collision_cooldown = 0
acceleration_factor = 1.2
max_acceleration_factor = 3
ball_size_small = 49
ball_size = 50

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
last_color_hit = (0, 255, 0)
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

# Ball settings
balls = [
    {'pos': [circle_center_x, circle_center_y+30], 'speed': [-20, 20], 'size': ball_size, 'color': (255, 0, 0), 'original_color': (255, 0, 0)},  # Red ball
    {'pos': [circle_center_x + 10, circle_center_y], 'speed': [20, 20], 'size': ball_size, 'color': (0, 255, 0),
     'original_color': (0, 255, 0)},  # Green ball
    {'pos': [circle_center_x-10, circle_center_y], 'speed': [20, 20], 'size': ball_size, 'color': (255, 0, 0), 'original_color': (255, 0, 0)},   # Red ball
    {'pos': [circle_center_x, circle_center_y+50], 'speed': [-20, 20], 'size': ball_size, 'color': (255, 0, 0), 'original_color': (255, 0, 0)}  # Red ball
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

# Function to play background audio
def play_audio(index, file_path):
    try:
        channel = [channel1, channel2, channel3, channel4][index]
        sound = [sound1, sound2, sound3, sound4][index]
        channel.play(sound)

        # Keep the program running until the music stops
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
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


draw_circle_color = circle_color
def change_color(dt):
    global color_change_timer, next_color_index, rainbow_colors, current_color_index, circle_color

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
    circle_color = ensure_color_values(circle_color + (general_opacity,))


ball_speed = 800  # pixels er second
trail_max_position = 2000

def update_ball(index, ball, dt):
    global bounce_count, cpt, last_color_hit
    max_speed = 1000  # Maximum speed limit for any ball

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

        if(ball['size'] == 50):
            ball['color'] = fade_to_white(ball['color'], 0.1)  # Adjust fade factor as needed

        last_color_hit = (255, 0, 0)

        if 'original_color' in ball:
            initiate_sparks_on_collision(spark_trails, [next_x, next_y], ball['original_color'])

        # Update bounce count
        if(index == 1 and ball['size'] == 50):
            bounce_count += 1
            #handle_bounce(outport, midi_track, bpm)
            background_audio_player(index, 'output_{:04d}.mp3'.format(cpt))  # Uncomment to enable dynamic sound playback
            last_color_hit = (0, 255, 0)

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



# Global variable to store rainbow balls
rainbow_balls = []

def spawn_rainbow_balls():
    global rainbow_balls
    colors = [
        (255, 0, 0),  # Bright Red
        (255, 0, 0),  # Bright Red
        (255, 0, 0),  # Bright Red
    ]

    start_x, start_y = circle_center_x, circle_center_y
    for i, color in enumerate(colors):
        angle = i * (360 / 16)
        speed_x = 20 * math.cos(math.radians(angle))
        speed_y = 20 * math.sin(math.radians(angle))
        rainbow_balls.append({'pos': [start_x, start_y], 'speed': [speed_x, speed_y], 'size': 49, 'color': color})


timebefore = 0

# Create a persistent surface
persistent_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
persistent_surface.set_alpha(255)  # Optional: set transparency for the persistent surface

# Game loop
while True:

    dt = clock.tick(120) / 1000  # Delta time in seconds

    ftime = ftime + dt
    dtcount += dt

#    if(ftime > timebefore):
#        change_instrument(outport, channel=0, program=instrucount)
#        timebefore = ftime+5
#        instrucount = instrucount +1
#        print(instrucount)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            outport.close()
            pygame.midi.quit()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                if FullScreen:
                    Ekran = pygame.display.set_mode((960, 540))
                    FullScreen = False
                else:
                    Ekran = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    FullScreen = True
        if event.type == pygame.QUIT:
            run = False

    # With physics
    #space.step(1 / 50.0)

    # Inside the game loop, check for 100 bounces
    if ftime > 20 and done == 0:
        spawn_rainbow_balls()  # Spawn rainbow balls at 100 bounces
        done = 1

    if ftime < 35:
        # Update each ball
        for index, ball in enumerate(balls):
            update_ball(index, ball, dt)

        for index, ball in enumerate(rainbow_balls):
            update_ball(index, ball, dt)

        if outer_circle_radius_increment > 0:
            outer_circle_radius_increment -= 1 * dt * decrement_speed
            decrement_speed = decrement_speed * 1.001

    if ftime >= 43:
        for index, ball in enumerate(balls):
            if(index == 0):
                ball['color'] = (0, 255, 0)  # Adjust fade factor as needed
            else:
                ball['color'] = (255, 0, 0)  # Adjust fade factor as needed



    if outer_circle_radius_increment > 0:
        outer_circle_radius_increment -= 1 * dt * decrement_speed
        decrement_speed = decrement_speed * 1.004

    screen.fill(black)

    # Outer circle for expansion effect
    expanded_radius = int(circle_radius + outer_circle_radius_increment)
    outer_circle_color = darken_color(last_color_hit, 0.2)
    pygame.gfxdraw.filled_circle(screen, int(circle_center[0]), int(circle_center[1]), expanded_radius + circle_thickness, outer_circle_color)


    # Circle with lighter outside area
    lighter_circle_color = lighten_color(last_color_hit, 0.3)
    pygame.gfxdraw.filled_circle(screen, int(circle_center[0]), int(circle_center[1]), circle_radius, lighter_circle_color)
    pygame.gfxdraw.filled_circle(screen, int(circle_center[0]), int(circle_center[1]), circle_radius - circle_thickness, black)

    draw_text(screen, '@musique.ball', (circle_center_x-50, circle_center_y),
              debug_font, (150,150,150))

    border_thickness = 4

    update_sparks(spark_trails, dt)

    draw_sparks(screen, spark_trails)


    # Ball with border
    for index, ball in enumerate(balls):

        if(ftime < 38):
            final_color = ball['color']
            ball_color = (255,255,255)
        else:
            final_color = ball['original_color']
            ball_color = ball['original_color']


            # Draw the inner circle using the safe draw function
        safe_draw_circle(screen, ball_color, int(ball['pos'][0]), int(ball['pos'][1]), int(ball['size'] / 2) + 2)
        safe_draw_circle(screen, final_color, int(ball['pos'][0]), int(ball['pos'][1]), int(ball['size'] / 2))

    screen.blit(persistent_surface, (0, 0))

    # Drawing rainbow balls in the game loop
    for ball in rainbow_balls:
        safe_draw_circle(screen, (255,255,255), int(ball['pos'][0]), int(ball['pos'][1]), int(ball['size'] / 2) + 2)
        pygame.gfxdraw.filled_circle(screen, int(ball['pos'][0]), int(ball['pos'][1]), ball['size'] // 2, ball['color'])


    # Ball with border
    for index, ball in enumerate(balls):

        if(ftime >= 38):

            final_color = ball['original_color']
            ball_color = ball['original_color']
            # Draw the inner circle using the safe draw function
            safe_draw_circle(screen, ball_color, int(ball['pos'][0]), int(ball['pos'][1]),
                             int(ball['size'] / 2) + 2)
            safe_draw_circle(screen, final_color, int(ball['pos'][0]), int(ball['pos'][1]),
                             int(ball['size'] / 2))

        if(ftime > 35) :
            draw_text(screen, str(index+1), ( int(ball['pos'][0])-6, int(ball['pos'][1]-16)),
                      debug_font2, (0, 0, 0))


    full_time = 35 - ftime
    if(full_time < 0) :
        full_time = 0

    draw_text(screen, 'Time : '+ str(int(full_time)), (circle_center_x - 50 , circle_center_y + circle_radius +35),
              debug_font2, (150, 150, 150))

    pygame.display.flip()
