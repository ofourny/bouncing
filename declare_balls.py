## balls for triangle

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

#balls for follow the ball

# Ball settings
balls = [
    {'pos': [circle_center_x, circle_center_y+30], 'speed': [-20, 20], 'size': ball_size, 'color': (255, 0, 0), 'original_color': (255, 0, 0)},  # Red ball
    {'pos': [circle_center_x + 10, circle_center_y], 'speed': [20, 20], 'size': ball_size, 'color': (0, 255, 0),
     'original_color': (0, 255, 0)},  # Green ball
    {'pos': [circle_center_x-10, circle_center_y], 'speed': [20, 20], 'size': ball_size, 'color': (255, 0, 0), 'original_color': (255, 0, 0)},   # Red ball
    {'pos': [circle_center_x, circle_center_y+50], 'speed': [-20, 20], 'size': ball_size, 'color': (255, 0, 0), 'original_color': (255, 0, 0)}  # Red ball
]
