from math import pi, asin, hypot
import numpy as np
from PIL import Image
import warnings
from audio_processor import mp3_to_amplitude_series, apply_low_pass_filter
from parameters import default_parameters as p
from geometry import cyl2cart


def amplitudes_to_cylinder_image(amplitudes, frame_rate):
    # Create blank image
    img_height, img_width = int(p.L / p.pixel_size), int(2 * p.R * np.pi / p.pixel_size)
    image = p.white * np.ones((img_height, img_width), dtype=np.uint8)

    # Color the pixel in the image
    for i,amp in enumerate(amplitudes):
        phase = (i) * p.speed_angular/frame_rate

        x = p.R * phase
        y = phase*p.pitch/(2*pi) + amp*p.max_amplitude/2 + p.end_margin + p.start_pos
        if y > p.L - p.end_margin:
            warnings.warn(f"Engraving stopped by end of cylinder.")
            break
        else:
            x_pixel, y_pixel = int(x / p.pixel_size) % img_width, int(y / p.pixel_size)
            if p.interpolate:
                # Color according to the distance to the center of the engraving
                for j in range(p.engraving_pixel_width):
                    dy = j - p.engraving_pixel_width//2
                    if 0 <= y_pixel+dy < img_height:
                        y_pixel_center = (y_pixel+dy + 0.5) * p.pixel_size
                        distance = abs(y - y_pixel_center)
                        image[y_pixel+dy, x_pixel] = int(min(p.white * distance/(p.width/2), p.white))
            else:
                # Color 100% black the pixel where the center of the engraving lies, and fade gradually to white
                image[y_pixel-2:y_pixel+3, x_pixel] = 255*2/3
                image[y_pixel-1:y_pixel+2, x_pixel] = 255*1/3
                image[y_pixel, x_pixel]             = 255*0/3

    print(f"Path contains {i+1}/{len(amplitudes)} points ({round((i+1)/len(amplitudes)*100,3)} %) from the audio segment.")

    # Save the image
    Image.fromarray(image).save(p.output_folder+p.output_filename+".tiff", 
                                format="TIFF",
                                quality=100, 
                                compression=None, 
                                dpi=(25.4/p.pixel_size, 25.4/p.pixel_size),
                                artist="Vincent Philippoz",
                                description=f"Plan de gravure pour un cylindre de {p.L} mm de long et {p.R*2} mm de diametre.",
                                copyright="Hublot SA",
                                software="Python 3",
                                )

def amplitudes_to_disc_image(amplitudes, frame_rate):
    # Create blank image (square)
    img_side = int(2 * p.R / p.pixel_size)
    center = int(img_side / 2)
    image = p.white * np.ones((img_side, img_side), dtype=np.uint8)

    # Create a center mark on the image
    length_cross_half, width_cross_half = int(1/p.pixel_size), int(0.1/p.pixel_size) 
    image[center-length_cross_half:center+length_cross_half, center-width_cross_half:center+width_cross_half] = 0
    image[center-width_cross_half:center+width_cross_half, center-length_cross_half:center+length_cross_half] = 0



    # Color the pixel in the image
    path_points = []
    R_max, R_min = p.R - p.end_margin - p.start_pos, p.end_margin
    path_points.append((R_max, 0))
    for i,amp in enumerate(amplitudes):
        _, prev_teta = path_points[-1]
        
        teta = prev_teta + 2 * asin(p.speed_angular/(2*frame_rate))
        r = R_max * (1 - teta*p.pitch/(2*pi*R_max)) + amp*p.max_amplitude/2


        if r < R_min:
            warnings.warn(f"Engraving stopped by center of disc.")
            break
        else:
            path_points.append((r, teta))

            x, y, _ = cyl2cart(r, teta, 0)
            x_pixel_exact, y_pixel_exact = x / p.pixel_size + center, y / p.pixel_size + center
            x_pixel_approx, y_pixel_approx = int(x_pixel_exact), int(y_pixel_exact)
            if p.interpolate:
                # Color according to the distance to the center of the engraving
                for j in range(p.engraving_pixel_width):
                    for k in range(p.engraving_pixel_width):
                        dx, dy = j - p.engraving_pixel_width//2, k - p.engraving_pixel_width//2
                        if 0 <= int(x_pixel_exact)+dx < img_side and 0 <= int(y_pixel_exact)+dy < img_side:
                            x_currpixel_center = (x_pixel_approx+dx + 0.5 - center) * p.pixel_size
                            y_currpixel_center = (y_pixel_approx+dy + 0.5 - center) * p.pixel_size
                            distance = hypot(x-x_currpixel_center, y - y_currpixel_center)
                            image[y_pixel_approx+dy, x_pixel_approx+dx] = int(min(p.white * distance/(p.width/2), image[int(y_pixel_exact)+dy, int(x_pixel_exact)+dx]))
            else:
                raise NotImplementedError

    # Save the image
    Image.fromarray(image).save(p.output_folder+p.output_filename+".tiff", 
                                format="TIFF",
                                quality=100, 
                                compression=None, 
                                dpi=(25.4/p.pixel_size, 25.4/p.pixel_size),
                                artist="Vincent Philippoz",
                                description=f"Plan de gravure pour un cylindre de {p.L} mm de long et {p.R*2} mm de diametre.",
                                copyright="Hublot SA",
                                software="Python 3",
                                )

if __name__ == "__main__":
    # Extract amplitudes from audio
    amplitudes, frame_rate, *_ = mp3_to_amplitude_series(p.input_folder+p.input_filename, channels='left', start_time=p.start_time, duration=p.duration)
    if p.filter_active:
        amplitudes, frame_rate = apply_low_pass_filter(amplitudes, frame_rate, cutoff_freq=p.cutoff_freq, downsample=True)

    # Convert amplitudes to engraving file
    amplitudes_to_disc_image(amplitudes, frame_rate)
    
    # Export parameters to a text file
    with open(p.output_folder+p.output_filename+"_parameters.txt", 'w') as f:
        f.write(str(p))

