


def lighten_color(color, amount=0.5):
    """Lightens the given color by multiplying (1-luminosity) by the given amount."""
    return tuple(min(255, int(c + (255 - c) * amount)) for c in color)


def darken_color(color, amount=0.5):
    """Darkens the given color by multiplying (1-luminosity) by the given amount."""
    return tuple(max(0, int(c * (1 - amount))) for c in color)


def fade_to_white(color, fade_factor):
    """Gradually fades the given color towards white by the fade factor."""
    new_color = [min(235, int(c + fade_factor * (235 - c))) for c in color]
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

