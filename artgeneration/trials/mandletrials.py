from artgeneration.nprandomart.mandle import main_cardioid_boundary,mandelbrot_set4
import matplotlib.pyplot as plt


real = .6685  # X start position, X width, chosen at a nice-looking location
imag = -.1905
imag,real = main_cardioid_boundary(0)
delta = 0.0050
# img = calculate_mandle_image(imag,real,delta,delta,512)
for i in range(1):
    print(i)
    img = mandelbrot_set4(imag,imag+ delta,real,real+ delta,1024,1024,265)

plt.imshow(img[2])
plt.show()

