"""
fast mandlebrot set calculation.
"""

from numba import njit
import numpy as np


@njit
def mandelbrot(creal, cimag, maxiter):
    """
    largely based on http://numba.pydata.org/numba-doc/0.21.0/user/examples.html
    plus added further optimizations:
    make the code run faster by avoiding a square root computation when
    computing np.abs(z) > 2 .  We can get an equivalent condition by squaring both sides, which yields:
    z.real * z.real + z.imag * z.imag > 4
    We can do even better, by breaking the complex number into its constituents.
    :param creal:
    :param cimag:
    :param maxiter:
    :return:
    """
    real = creal
    imag = cimag
    for n in range(maxiter):
        real2 = real * real
        imag2 = imag * imag
        if real2 + imag2 > 4.0:
            return n
        imag = 2 * real * imag + cimag
        real = real2 - imag2 + creal
    return 0


@njit
def mandelbrot_set4(xmin, xmax, ymin, ymax, size, maxiter=2500):
    print('starting mandlebrot set calculation')
    real_axis = np.linspace(xmin, xmax, size)
    imag_axis = np.linspace(ymin, ymax, size)
    n3 = np.empty((size, size))
    for i in range(size):
        for j in range(size):
            n3[i, j] = mandelbrot(real_axis[i], imag_axis[j], maxiter)

    print('finished mandlebrot set calculation')
    return n3
