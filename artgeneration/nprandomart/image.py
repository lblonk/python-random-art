import numpy as np
from PIL import Image


def get_image(art,size=200):

    u,v = np.meshgrid(np.linspace(0,1,size),np.linspace(0,1,size))
    print('evaluating expressions')
    (r, g, b) = art.eval(u, v)
    print('evaluation done')
    rgbArray = np.zeros((size, size, 3), 'uint8')
    rgbArray[..., 0] = r * 256
    rgbArray[..., 1] = g * 256
    rgbArray[..., 2] = b * 256
    img = Image.fromarray(rgbArray)
    return img
