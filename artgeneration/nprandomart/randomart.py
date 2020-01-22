#!/usr/bin/python

# See README.md for documentation and LICENCE for licencing information.

import os
import random
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
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
        self.c1 = random.uniform(0, 1)
        self.c2 = random.uniform(0, 1)
        self.c3 = random.uniform(0, 1)

    def __repr__(self):
        return 'Constant(%g,%g,%g)' % self.c

    def eval(self,x,y): return (np.ones(SIZE_2D)*self.c1,
                                np.ones(SIZE_2D)*self.c2,
                                np.ones(SIZE_2D)*self.c3)


from .mandle import calculate_mandle_image
class Mandle():
    arity = 0
    mandle = calculate_mandle_image(image_size=SIZE_1D)
    def __init__(self): pass
    def __repr__(self): return "mandlebrot"
    def eval(self, x, y):
        return (self.mandle,self.mandle,self.mandle)

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
            r3 = np.where(r2>0,np.remainder(r1,r2),0.)
            g3 = np.where(g2>0,np.remainder(g1,g2),0.)
            b3 = np.where(b2>0,np.remainder(b1,b2),0.)
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

operators = (VariableX, VariableY, Constant, Mandle, Average, Product, Mod, Sin, Tent, Well, Level, Mix)

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
    """A  graphical user interface for random art"""

    def __init__(self, master, size=SIZE_2D):
        master.title('Random art')

        button_frame = Frame(master)
        button_frame.pack(side =LEFT,fill=Y, expand=True)

        b = Button(button_frame, text='Again!', font='Helvetica 12 bold', command=self.redraw)
        b.pack(side=TOP, fill='x')
        b = Button(button_frame, text='Save picture', command=self.save_picture)
        b.pack(side=TOP, fill='x')
        b = Button(button_frame, text='Save expression', command=self.save_expression_tree)
        b.pack(side=TOP, fill='x')
        b = Button(button_frame, text='Load expression', command=self.load_expression_tree)
        b.pack(side=TOP, fill='x')

        picture_frame = Frame(master)
        picture_frame.pack(side=RIGHT)

        self.canvas = Canvas(picture_frame, width=SIZE_1D, height=SIZE_1D)
        self.canvas.pack(side=LEFT)

        self.draw_alarm = None
        self.redraw()

        self.last_used_dir = os.getcwd() # variable used for save/load actions

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
        self.img = Image.fromarray(rgbArray)
        self.img_tk = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(1, 1, image=self.img_tk, anchor=NW)

    def save_picture(self):
        """
        save the currently displayed picture to file
        """

        fp = filedialog.asksaveasfilename(initialdir = self.last_used_dir,
                                          initialfile = 'randomart1.bmp',
                                          confirmoverwrite = True,
                                          defaultextension = 'bmp',
                                          title = "select file",
                                          filetypes = (("bmp","*.bmp"),("all files","*.*")))

        self.last_used_dir = os.path.dirname(fp)

        # save picture itself
        try:
            self.img.save(fp)
        except Exception as e:
            messagebox.showinfo("error during image save ", str(e))
            return

        # save expression tree that defines the picture
        try:
            self._save_expression_tree(fp.replace('bmp','json'))
        except Exception as e:
            messagebox.showinfo("error during tree save ", str(e))
            return


    def save_expression_tree(self):
        """
        save the expressions that define the currently displayed picture to file
        """

        fp = filedialog.asksaveasfilename(initialdir=self.last_used_dir,
                                          initialfile='randomart1.json',
                                          confirmoverwrite=True,
                                          defaultextension='json',
                                          title="select file",
                                          filetypes=(("json", "*.json"), ("all files", "*.*")))

        self.last_used_dir = os.path.dirname(fp)
        self._save_expression_tree(fp)

    def _save_expression_tree(self,fp):

        jsonpickle = self._load_json_pickle_safe()

        try:
            s = jsonpickle.encode(self.art)
            with open(fp,'w') as f:
                f.write(s)

        except Exception as e:
            messagebox.showinfo("error during expression save ", str(e) )


    def load_expression_tree(self):
        """
        loads the expressions that define a picture from file, and render corresponding picture
        :return:
        """

        jsonpickle = self._load_json_pickle_safe()

        fp = filedialog.askopenfilename(initialdir = self.last_used_dir,
                                        initialfile = 'randomart1.json',
                                        defaultextension = 'json',
                                        title = "select file",
                                        filetypes = (("json","*.json"),("all files","*.*")))

        self.last_used_dir = os.path.dirname(fp)

        try:
            with open(fp,'r') as f:
                 s = f.read()

            self.art = jsonpickle.loads(s)
            self.draw()

        except Exception as e:
            messagebox.showinfo("error during expressiontree loading", str(e) )


    def _load_json_pickle_safe(self):
        """
        As jsonpickle may not be available, this import is wrapped in exception handling to keep the app alive if the import fails
        :return:
        """
        try:
            import jsonpickle
            jsonpickle.set_encoder_options('json', indent=4)
            import jsonpickle.ext.numpy as jsonpickle_numpy
            jsonpickle_numpy.register_handlers()
            return jsonpickle
        except Exception as e:
            messagebox.showinfo("import error", str(e))
            return None

# Main program
win = Tk()
arg = Art(win)
win.mainloop()


#TODO: turn into package with setup.py so that installing the dependancies is easier
#TODO: add choice of SIZE to UI

