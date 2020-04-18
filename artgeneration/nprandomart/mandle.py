"""
fast mandlebrot set calculation.
"""

from numba import njit
import numpy as np
from pathlib import Path
import json, random
from .randomart import Operator, store
this_dir = Path(__file__).parent
# load list of interesting mandlebrot locations,
# courtesy of David Eck: http://math.hws.edu/eck/js/mandelbrot/java/MandelbrotSettings/
with open(this_dir / 'resources/mandle_locations.json') as f:
    locations = json.load(f)['locations']
    locations = [loc for loc in locations if loc['max_iterations'] <= 5000]


class Mandle(Operator):
    arity = 0

    @classmethod
    def setup(cls):
        cls.set_random_location()

    @classmethod
    def set_random_location(cls):

        cls.cache = {}  # cache to store evaluations, as this is a very expensive function

        location = random.choice(locations)
        cls.xmin = location['limits']['xmin']
        cls.xmax = location['limits']['xmax']
        cls.ymin = location['limits']['ymin']
        cls.ymax = location['limits']['ymax']

        # shift locations a bit, otherwise would not be random
        x_shift = random.uniform(-0.4, 0.4) * (cls.xmax - cls.xmin)
        cls.xmin += x_shift
        cls.xmax += x_shift
        y_shift = random.uniform(-0.4, 0.4) * (cls.ymax - cls.ymin)
        cls.ymin += y_shift
        cls.ymax += y_shift

        cls.maxiter = location['max_iterations']

    def __init__(self):
        pass

    def __repr__(self):
        return "Mandlebrot"

    def __getstate__(self):
        """
        Custom getstate for to give desired encode behavior when using jsonpickle
        """
        state = {k: getattr(self, k) for k in ['xmin', 'xmax', 'ymin', 'ymax', 'maxiter']}
        return state

    def __setstate__(self, state):
        """
        Custom getstate for to give desired decode behavior when using jsonpickle
        """
        self.__class__.cache = {}
        for k, v in state.items():
            setattr(self, k, v)

    @store
    def eval(self, x, y):

        size = x.shape[0]  # i.e. 900 pixels
        try:
            mandle = self.cache[size]
        except KeyError:
            mandle = get_mandlebrot(self.xmin,
                                    self.xmax,
                                    self.ymin,
                                    self.ymax,
                                    size=size,
                                    maxiter=self.maxiter)

            normalize_to_one = random.choice([True, False, False]) # when not normalizing, it gives nice glitchy effects
            if normalize_to_one:
                mandle = mandle / mandle.max()
            self.cache[size] = mandle

        return (mandle, mandle, mandle)



@njit
def get_mandlebrot(xmin, xmax, ymin, ymax, size, maxiter):
    """
    fast, numba-based mandlebrot set calculation
    :return:
    """
    print('starting mandlebrot set calculation')
    real_axis = np.linspace(xmin, xmax, size)
    imag_axis = np.linspace(ymin, ymax, size)
    mandle = np.empty((size, size))
    for i in range(size):
        for j in range(size):
            mandle[i, j] = mandelbrot_single_point(real_axis[i], imag_axis[j], maxiter)

    print('finished mandlebrot set calculation')
    return mandle


@njit
def mandelbrot_single_point(creal, cimag, maxiter):
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


