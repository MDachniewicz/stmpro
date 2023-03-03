import numpy as np
from scipy import fft


def fft_image(image):
    return fft.fftshift(fft.fft2(image))


def ifft_image(fft_image):
    return np.real(fft.ifft2(fft.ifftshift(fft_image)))
