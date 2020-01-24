from nprandomart import generate
from nprandomart.randomart import SIZE_1D
import random
import numpy as np
from PIL import Image

def get_image():
    art = generate(random.randrange(20,150))
    u,v = np.meshgrid(np.linspace(0,1,SIZE_1D),np.linspace(0,1,SIZE_1D))
    print('evaluating expressions')
    (r, g, b) = art.eval(u, v)
    print('evaluation done')
    rgbArray = np.zeros((SIZE_1D, SIZE_1D, 3), 'uint8')
    rgbArray[..., 0] = r * 256
    rgbArray[..., 1] = g * 256
    rgbArray[..., 2] = b * 256
    img = Image.fromarray(rgbArray)
    return img



