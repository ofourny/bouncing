def fade_to_white(color, fade_factor):
    """ Gradually fades the given color towards white by the fade factor. """
    new_color = [min(255, int(c + fade_factor * (255 - c))) for c in color]
    return tuple(new_color)


