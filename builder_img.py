from PIL import Image
import numpy as np

# Parameters
HEIGHT = 100
DIAMETER = 53
PIXEL_SIZE = 0.01

img_height, img_width = int(HEIGHT / PIXEL_SIZE), int(DIAMETER * np.pi / PIXEL_SIZE)

# Create white image
myarr = 255 * np.ones((img_height, img_width), dtype=np.uint8)
myarr[:, 20:30] = 0

# Save the image
Image.fromarray(myarr).save("test.tiff", format="TIFF", quality=100, subsampling=0)