#TODO: random zoom point mandle
# Points on the boundary of the Mandelbrot set generally have the most interesting orbits.  The easiest boundary points to compute are:
#
# * the spike along the negative real axis

# * the boundary of the period 2 disk:

import math

def main_cardioid_boundary(theta):
    r = (1 - math.cos(theta)) / 2
    x = r * math.cos(theta) + 0.25
    y = r * math.sin(theta)
    return x,y

def negative_real_axis_spike():
    pass

def period_2_disk(theta):
    r = 0.25
    x = r * math.cos(theta) - 1
    y = r * math.sin(theta)

# TODO: faster numba implementation: https://www.ibm.com/developerworks/community/blogs/jfp/entry/How_To_Compute_Mandelbrodt_Set_Quickly?lang=en
import numpy as np
def calculate_mandle_image(real,imag,dreal,dimag, image_size, iterations=256):
    dx = (imag, dimag)  # X start position, X width, chosen at a nice-looking location
    dy = (real,  dreal)  # Y start position, Y width, chosen at a nice-looking location
    v = np.zeros((image_size, image_size), 'float32')  # The color matrix
    # Create the const matrix and initialize it
    c = np.zeros((image_size, image_size), 'complex')
    c[:].real = np.linspace(dy[0], dy[0] + dy[1], image_size)[:, None]
    c[:].imag = np.linspace(dx[0], dx[0] + dx[1], image_size)[None, :]
    z = c.copy()
    print('doing mandlebrot image generation..')
    for i in range(iterations):
        z *= z  # Compute z = z*z
        z += c  # Compute z = z + c
        # Set colors for which z has diverged
        v += (np.abs(z) >= 4) * (v == 0) * i
    print('finished mandlebrot image generation')
    return v / np.max(v)

from numba import njit
"""
http://numba.pydata.org/numba-doc/0.21.0/user/examples.html
AND:
One can make the code run faster by avoiding a square root computation when 
computing np.abs(z) > 2 .  We can get an equivalent condition by squaring both sides, which yields:
z.real * z.real + z.imag * z.imag > 4
We can do even better, by breaking the complex number into its constituents, 
i.e. into two floating point numbers.  The code becomes:
"""
@njit
def mandelbrot(creal,cimag,maxiter):
    real = creal
    imag = cimag
    for n in range(maxiter):
        real2 = real*real
        imag2 = imag*imag
        if real2 + imag2 > 4.0:
            return n
        imag = 2* real*imag + cimag
        real = real2 - imag2 + creal
    return 0


@njit
def mandelbrot_set4(xmin,xmax,ymin,ymax,width,height,maxiter):
    real_axis = np.linspace(xmin, xmax, width)
    imag_axis = np.linspace(ymin, ymax, height)
    n3 = np.empty((width,height))
    for i in range(width):
        for j in range(height):
            n3[i,j] = mandelbrot(real_axis[i],imag_axis[j],maxiter)
    return (real_axis,imag_axis,n3)

