import numpy as np
from scipy import fft


def fft_image(image):
    return np.abs(fft.fftshift(fft.rfft2(image)))
