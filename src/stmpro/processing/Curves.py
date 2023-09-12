import skimage as ski
import numpy as np

def extract_profile(image, start_point, end_point, width):
    profile = ski.measure.profile_line(image=image, src=start_point[::-1], dst=end_point[::-1], linewidth=width)

    return profile