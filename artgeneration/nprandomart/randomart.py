#!/usr/bin/python

# See README.md for documentation and LICENCE for licencing information.


import random
import numpy as np

np.seterr(divide='ignore', invalid='ignore')
thumbnail_size = 200

# Utility functions
def average(c1, c2, w=0.5):
    """Compute the weighted average of two colors. With w = 0.5 we get the average."""
    (r1, g1, b1) = c1
    (r2, g2, b2) = c2
    r3 = w * r1 + (1 - w) * r2
    g3 = w * g1 + (1 - w) * g2
    b3 = w * b1 + (1 - w) * b2
    return (r3, g3, b3)


def well(x):
    """A function which looks a bit like a well."""
    return 1 - 2 / (1 + x * x) ** 8


def tent(x):
    """A function that looks a bit like a tent."""
    return 1 - 2 * np.abs(x)


# We next define classes that represent expression trees.

# Each object that represents an expression should have an eval(self,x,y) method
# which computes the value of the expression at (x,y). The __init__ should
# accept the objects representing its subexpressions. The class definition
# should contain the arity attribute which tells how many subexpressions should
# be passed to the __init__ constructor.


class Operator:
    """
    base class for the operators
    """
    arity: int

    def eval(self, x: np.ndarray, y: np.ndarray):
        """this must be implemented in subclassed"""
        raise NotImplementedError


def store(eval_original):
    """
    decorator that stores the image for each operator
    """

    def eval_with_storage(*args):
        instance = args[0]
        img = eval_original(*args)
        if img[0].shape[0] <= thumbnail_size:  # only if thumbnail; storing for full size image would take too much mem
            instance.img = img
        return img

    return eval_with_storage


class VariableX(Operator):
    arity = 0

    def __init__(self): pass

    def __repr__(self): return "ReturnX(X,Y)"

    @store
    def eval(self, x, y): return (x, x, x)


class VariableY(Operator):
    arity = 0

    def __init__(self): pass

    def __repr__(self): return "ReturnY(X,Y)"

    @store
    def eval(self, x, y): return (y, y, y)


class Constant(Operator):
    arity = 0

    def __init__(self):
        self.c1 = random.uniform(0, 1)
        self.c2 = random.uniform(0, 1)
        self.c3 = random.uniform(0, 1)

    def __repr__(self):
        return f'ConstantColor'  # (r={self.c1:.2f},g={self.c2:.2f},b={self.c3:.2f})'

    @store
    def eval(self, x, y): return (np.ones_like(x) * self.c1,
                                  np.ones_like(x) * self.c2,
                                  np.ones_like(x) * self.c3)


# from .mandle import calculate_mandle_image
# class Mandle(Operator):
#     arity = 0
#     mandle = calculate_mandle_image(image_size=size)
#     def __init__(self): pass
#     def __repr__(self): return "mandlebrot"
#     def eval(self, x, y):
#         return (self.mandle,self.mandle,self.mandle)

class Average(Operator):
    arity = 2

    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return 'Average(E1,E2)'

    @store
    def eval(self, x, y):
        return average(self.e1.eval(x, y), self.e2.eval(x, y))


class Product(Operator):
    arity = 2

    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return 'Product(E1,E2)'

    @store
    def eval(self, x, y):
        (r1, g1, b1) = self.e1.eval(x, y)
        (r2, g2, b2) = self.e2.eval(x, y)
        r3 = r1 * r2
        g3 = g1 * g2
        b3 = b1 * b2
        return (r3, g3, b3)


class Mod(Operator):
    arity = 2

    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return 'Modulo(E1,E2)'

    @store
    def eval(self, x, y):
        (r1, g1, b1) = self.e1.eval(x, y)
        (r2, g2, b2) = self.e2.eval(x, y)
        try:
            r3 = np.where(r2 > 0, np.remainder(r1, r2), 0.)
            g3 = np.where(g2 > 0, np.remainder(g1, g2), 0.)
            b3 = np.where(b2 > 0, np.remainder(b1, b2), 0.)
            return (r3, g3, b3)
        except:
            return (np.zeros_like(x), np.zeros_like(x), np.zeros_like(x))


class Well(Operator):
    arity = 1

    def __init__(self, e):
        self.e = e

    def __repr__(self):
        return 'WellFunction(E1)'

    @store
    def eval(self, x, y):
        (r, g, b) = self.e.eval(x, y)
        return (well(r), well(g), well(b))


class Tent(Operator):
    arity = 1

    def __init__(self, e):
        self.e = e

    def __repr__(self):
        return 'TentFunction(E1)'

    @store
    def eval(self, x, y):
        (r, g, b) = self.e.eval(x, y)
        return (tent(r), tent(g), tent(b))


class Sin(Operator):
    arity = 1

    def __init__(self, e):
        self.e = e
        self.phase = random.uniform(0, np.pi)
        self.freq = random.uniform(1.0, 6.0)

    def __repr__(self):
        return f'Sine(E1)(phase={self.phase:.2f},freq={self.freq:.2f})'

    @store
    def eval(self, x, y):
        (r1, g1, b1) = self.e.eval(x, y)
        r2 = np.sin(self.phase + self.freq * r1)
        g2 = np.sin(self.phase + self.freq * g1)
        b2 = np.sin(self.phase + self.freq * b1)
        return (r2, g2, b2)


class Level(Operator):
    arity = 3

    def __init__(self, level, e1, e2):
        self.treshold = random.uniform(-1.0, 1.0)
        self.level = level
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return f'Level(E1,E2,E3)(treshold={self.treshold:.2f})'

    @store
    def eval(self, x, y):
        (r1, g1, b1) = self.level.eval(x, y)
        (r2, g2, b2) = self.e1.eval(x, y)
        (r3, g3, b3) = self.e2.eval(x, y)
        r4 = np.where(r1 < self.treshold, r2, r3)
        g4 = np.where(g1 < self.treshold, g2, g3)
        b4 = np.where(b1 < self.treshold, b2, b3)
        return (r4, g4, b4)


class Mix(Operator):
    arity = 3

    def __init__(self, w, e1, e2):
        self.w = w
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return 'Mix(E1,E2)'

    @store
    def eval(self, x, y):
        # w = 0.5 * (self.w.eval(x,y)[0] + 1.0) #TODO: fix
        c1 = self.e1.eval(x, y)
        c2 = self.e2.eval(x, y)
        return average(c1, c2, )


# The following list of all classes that are used for generation of
# expressions is used by the generate function below.

operators = (
VariableX, VariableY, Constant, Average, Product, Mod, Sin, Tent, Well, Level, Mix)  # ,Mandle TODO:reinstate Mandle

# We precompute those operators that have arity 0 and arity > 0

operators0 = [op for op in operators if op.arity == 0]
operators1 = [op for op in operators if op.arity > 0]


def generate(k=50):
    '''Randonly generate an expession of a given size.'''
    if k <= 0:
        # We used up available size, generate a leaf of the expression tree
        op = random.choice(operators0)
        return op()
    else:
        # randomly pick an operator whose arity > 0
        op = random.choice(operators1)
        # generate subexpressions
        i = 0  # the amount of available size used up so far
        args = []  # the list of generated subexpression
        for j in sorted([random.randrange(k) for l in range(op.arity - 1)]):
            args.append(generate(j - i))
            i = j
        args.append(generate(k - 1 - i))
        return op(*args)


def get_art(min_arity=20, max_arity=150):
    art = generate(random.randrange(min_arity, max_arity))
    return art