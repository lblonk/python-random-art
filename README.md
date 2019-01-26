# Numpy - Version of Random Art in Python - includes the Mandlebrot set -

This is an altered version of Andrej Bauer's Simple Random Art program.

For an introduction to this program, please see (https://github.com/andrejbauer/simple-random-art).

In this altered version, numpy is used for the evaluation of the mathematical formulae that 
determine the color of the individual pixels, which results in a speedup of the 'painting of the picture' 
of two orders of magnitude (roughly 100 times faster)

In addition, as also advised by Andrey in his 'further work' section, the PIL library is used for display of the image. 
This, combined with the faster execution time, facilitates painting much larger picures than the original version. 

Finally, in this branch; a famous fractal; the mandlebrot set, is included. 

You need Python 3.5 and numpy or later to run the program. 
To start the program, run `python randomart.py` from the command-line,
or from a Python IDE such as pycharm