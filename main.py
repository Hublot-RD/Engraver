from math import pi
import numpy as np
from PIL import Image
import warnings
# from builder3d import export_path_to_csv
from audio_processor import mp3_to_amplitude_series, apply_low_pass_filter
from parameters import default_parameters as p


# Extract amplitudes from audio
amplitudes, frame_rate, *_ = mp3_to_amplitude_series(p.input_folder+p.input_filename, channels='left', start_time=p.start_time, duration=p.duration)
if p.filter_active:
    # Apply low pass filter
    amplitudes, frame_rate = apply_low_pass_filter(amplitudes, frame_rate, cutoff_freq=p.cutoff_freq, downsample=True)

# Create blank image
img_height, img_width = int(p.L / p.pixel_size), int(2 * p.R * np.pi / p.pixel_size)
image = p.white * np.ones((img_height, img_width), dtype=np.uint8)

# Create path points from amplitudes
for i,amp in enumerate(amplitudes):
    phase = (i) * p.speed_angular/frame_rate

    x = p.R * phase
    y = phase*p.pitch/(2*pi) + amp*p.max_amplitude/2 + p.end_margin + p.start_pos
    if y > p.L - p.end_margin:
        warnings.warn(f"Engraving stopped by end of cylinder.")
        break
    else:
        # Color the corresponding pixel in the image according to the distance to the center of the engraving
        x_pixel, y_pixel = int(x / p.pixel_size) % img_width, int(y / p.pixel_size)
        for j in range(p.engraving_pixel_width):
            dy = j - p.engraving_pixel_width//2
            if 0 <= y_pixel+dy < img_height:
                y_pixel_center = (y_pixel+dy + 0.5) * p.pixel_size
                distance = abs(y - y_pixel_center)
                image[y_pixel+dy, x_pixel] = int(min(p.white * distance/(p.width/2), p.white))
        # image[y_pixel-2:y_pixel+3, x_pixel] = 255*2/3
        # image[y_pixel-1:y_pixel+2, x_pixel] = 255*1/3
        # image[y_pixel, x_pixel] = 0

print(f"Path contains {i+1}/{len(amplitudes)} points ({round((i+1)/len(amplitudes)*100,3)} %) from the audio segment.")
# used_length = path_points_plane[-1][-1] - p.start_pos - p.end_margin
# print(f"Engraving takes {round(used_length, 3)} mm, {round(used_length/(p.L - 2*p.end_margin)*100, 3)} % of the available space of the cylinder.")

# Save the image
Image.fromarray(image).save(p.output_filename+".tiff", format="TIFF", quality=100, subsampling=0)

# Export parameters to a text file
# with open(p.output_folder+p.output_filename+"_parameters.txt", 'w') as f:
#     f.write(str(p))
