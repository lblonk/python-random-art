"""
A modified version of the original 'simple-random-art' tkinter app,
with added image save/load, and expression-tree-to-json buttons
"""
from nprandomart import generate
from nprandomart.randomart import SIZE_2D, SIZE_1D
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import random
import numpy as np
import jsonpickle
jsonpickle.set_encoder_options('json', indent=4)
import jsonpickle.ext.numpy as jsonpickle_numpy
jsonpickle_numpy.register_handlers()

class Art():
    """A  tkinter graphical user interface for random art"""

    def __init__(self, master):
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

if __name__ == '__main__':

    # Main program
    win = Tk()
    art = Art(win)
    win.mainloop()
