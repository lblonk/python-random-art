#!/usr/bin/python

# See README.md for documentation and LICENCE for licencing information.

import random
from tkinter import * # Change "tkinter" to "Tkinter" in Python 2
from PIL import ImageTk, Image
import numpy as np
np.seterr(divide='ignore', invalid='ignore')

SIZE_1D = 900
SIZE_2D = (SIZE_1D,SIZE_1D)

# Utility functions
def average(c1, c2, w=0.5):
    '''Compute the weighted average of two colors. With w = 0.5 we get the average.'''
    (r1,g1,b1) = c1
    (r2,g2,b2) = c2
    r3 = w * r1 + (1 - w) * r2
    g3 = w * g1 + (1 - w) * g2
    b3 = w * b1 + (1 - w) * b2
    return (r3, g3, b3)

def well(x):
    '''A function which looks a bit like a well.'''
    return 1 - 2 / (1 + x*x) ** 8

def tent(x):
    '''A function that looks a bit like a tent.'''
    return 1 - 2 * np.abs(x)

# We next define classes that represent expression trees.

# Each object that represents an expression should have an eval(self,x,y) method
# which computes the value of the expression at (x,y). The __init__ should
# accept the objects representing its subexpressions. The class definition
# should contain the arity attribute which tells how many subexpressions should
# be passed to the __init__ constructor.

class VariableX():
    arity = 0
    def __init__(self): pass
    def __repr__(self): return "x"
    def eval(self,x,y): return (x,x,x)

class VariableY():
    arity = 0
    def __init__(self): pass
    def __repr__(self): return "y"
    def eval(self,x,y): return (y,y,y)

class Constant():
    arity = 0
    def __init__(self):
        ones = np.ones(SIZE_2D)
        self.c = (ones*random.uniform(0,1),
                  ones*random.uniform(0,1),
                  ones*random.uniform(0,1))
    def __repr__(self):
        return 'Constant(%g,%g,%g)' % self.c
    def eval(self,x,y): return self.c

class Average():
    arity = 2
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    def __repr__(self):
        return 'Sum(%s, %s)' % (self.e1, self.e2)
    def eval(self,x,y):
        return average(self.e1.eval(x,y), self.e2.eval(x,y))

class Product():
    arity = 2
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    def __repr__(self):
        return 'Product(%s, %s)' % (self.e1, self.e2)
    def eval(self,x,y):
        (r1,g1,b1) = self.e1.eval(x,y)
        (r2,g2,b2) = self.e2.eval(x,y)
        r3 = r1 * r2
        g3 = g1 * g2
        b3 = b1 * b2
        return (r3, g3, b3)

class Mod():
    arity = 2
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    def __repr__(self):
        return 'Mod(%s, %s)' % (self.e1, self.e2)
    def eval(self,x,y):
        (r1,g1,b1) = self.e1.eval(x,y)
        (r2,g2,b2) = self.e2.eval(x,y)
        try:
            r3 = np.where(r2>0,np.remainder(r1,r2),1.)
            g3 = np.where(g2>0,np.remainder(g1,g2),1.)
            b3 = np.where(b2>0,np.remainder(b1,b2),1.)
            return (r3, g3, b3)
        except:
            return (np.zeros(SIZE_2D),np.zeros(SIZE_2D),np.zeros(SIZE_2D))

class Well():
    arity = 1
    def __init__(self, e):
        self.e = e
    def __repr__(self):
        return 'Well(%s)' % self.e
    def eval(self,x,y):
        (r,g,b) = self.e.eval(x,y)
        return (well(r), well(g), well(b))

class Tent():
    arity = 1
    def __init__(self, e):
        self.e = e
    def __repr__(self):
        return 'Tent(%s)' % self.e
    def eval(self,x,y):
        (r,g,b) = self.e.eval(x,y)
        return (tent(r), tent(g), tent(b))

class Sin():
    arity = 1
    def __init__(self, e):
        self.e = e
        self.phase = random.uniform(0, np.pi)
        self.freq =  random.uniform(1.0, 6.0)
    def __repr__(self):
        return 'Sin(%g + %g * %s)' % (self.phase, self.freq, self.e)
    def eval(self,x,y):
        (r1,g1,b1) = self.e.eval(x,y)
        r2 = np.sin(self.phase + self.freq * r1)
        g2 = np.sin(self.phase + self.freq * g1)
        b2 = np.sin(self.phase + self.freq * b1)
        return (r2,g2,b2)

class Level():
    arity = 3
    def __init__(self, level, e1, e2):
        self.treshold = random.uniform(-1.0,1.0)
        self.level = level
        self.e1 = e1
        self.e2 = e2
    def __repr__(self):
        return 'Level(%g, %s, %s, %s)' % (self.treshold, self.level, self.e1, self.e2)
    def eval(self,x,y):
        (r1, g1, b1) = self.level.eval(x,y)
        (r2, g2, b2) = self.e1.eval(x,y)
        (r3, g3, b3) = self.e2.eval(x,y)
        r4 = np.where(r1 < self.treshold,r2,r3)
        g4 = np.where(g1 < self.treshold,g2,g3)
        b4 = np.where(b1 < self.treshold,b2,b3)
        return (r4,g4,b4)

class Mix():
    arity = 3
    def __init__(self, w, e1, e2):
        self.w = w
        self.e1 = e1
        self.e2 = e2
    def __repr__(self):
        return 'Mix(%s, %s, %s)' % (self.w, self.e1, self.e2)
    def eval(self,x,y):
        # w = 0.5 * (self.w.eval(x,y)[0] + 1.0)
        c1 = self.e1.eval(x,y)
        c2 = self.e2.eval(x,y)
        return average(c1,c2,)

# The following list of all classes that are used for generation of 
# expressions is used by the generate function below.

operators = (VariableX, VariableY, Constant, Average, Product, Mod, Sin, Tent, Well, Level, Mix)

# We precompute those operators that have arity 0 and arity > 0

operators0 = [op for op in operators if op.arity == 0]
operators1 = [op for op in operators if op.arity > 0]

def generate(k = 50):
    '''Randonly generate an expession of a given size.'''
    if k <= 0: 
        # We used up available size, generate a leaf of the expression tree
        op = random.choice(operators0)
        return op()
    else:
        # randomly pick an operator whose arity > 0
        op = random.choice(operators1)
        # generate subexpressions
        i = 0 # the amount of available size used up so far
        args = [] # the list of generated subexpression
        for j in sorted([random.randrange(k) for l in range(op.arity-1)]):
            args.append(generate(j - i))
            i = j
        args.append(generate(k - 1 - i))
        return op(*args)

class Art():
    """A simple graphical user interface for random art. It displays the image,
       and the 'Again!' button."""

    def __init__(self, master, size=SIZE_2D):
        master.title('Random art')
        self.canvas = Canvas(master, width=SIZE_1D, height=SIZE_1D)
        b = Button(master, text='Again!', command=self.redraw)
        # b.grid(row=1,column=0)
        self.canvas.pack(expand=YES, fill=BOTH)
        b.pack()
        self.draw_alarm = None
        self.redraw()

    def redraw(self):
        if self.draw_alarm: self.canvas.after_cancel(self.draw_alarm)
        self.canvas.delete(ALL)
        self.art = generate(random.randrange(20,150))
        self.draw()

    def draw(self):
        u,v = np.meshgrid(np.linspace(0,1,SIZE_1D),np.linspace(0,1,SIZE_1D))
        print('evaluating expressions')
        (r, g, b) = self.art.eval(u, v)
        print('evaluation done')
        rgbArray = np.zeros((SIZE_1D, SIZE_1D, 3), 'uint8')
        rgbArray[..., 0] = r * 256
        rgbArray[..., 1] = g * 256
        rgbArray[..., 2] = b * 256
        img = Image.fromarray(rgbArray)
        # img.save('myimg.jpeg') #TODO add save button
        self.img_tk = ImageTk.PhotoImage(img)
        self.canvas.create_image(1, 1, image=self.img_tk, anchor=NW)

# Main program
win = Tk()
arg = Art(win)
win.mainloop()



