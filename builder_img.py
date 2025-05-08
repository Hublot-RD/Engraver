from PIL import Image
import numpy as np

# Create white image
myarr = 255 * np.ones((100, 100), dtype=np.uint8)

# Save the image
Image.fromarray(myarr).save("test.tiff", format="TIFF", quality=100, subsampling=0)