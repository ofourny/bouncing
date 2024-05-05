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