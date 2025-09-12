from math import pi, asin, hypot, sin, sqrt, floor
import numpy as np
from PIL import Image
import warnings

import exporter
from parameters import default_parameters as p
from geometry import cyl2cart


def amplitudes_to_cylinder_points(amplitudes: np.ndarray, frame_rate: float) -> None:
    """
    Convert a series of sound amplitudes to a list of points on a cylinder.
    
    The points are calculated based on the parameters defined in the `parameters.py` file.
    The points are then exported to a CSV file.


    Parameters
    ----------
    amplitudes : np.ndarray
        Array of sound amplitudes.
    frame_rate : float
        Frame rate of the audio signal in Hz.
        
    Returns
    -------
    None
    """
    path_points_cyl = []
    path_points_plane = []
    for i,amp in enumerate(amplitudes):
        radius = p.R-p.depth
        phase = (i) * p.speed_angular/frame_rate
        elevation = phase*p.pitch/(2*pi) + amp*p.max_amplitude/2 + p.end_margin + p.start_pos + p.offset_from_centerline
        if p.right_thread: phase = -phase

        x = p.R
        y = radius * phase
        z = elevation
        if elevation > p.L - p.end_margin:
            warnings.warn(f"Engraving stopped by end of cylinder.")
            break
        else:
            path_points_cyl.append((radius, phase, elevation))
            path_points_plane.append((x, y, z))

    used_length = path_points_cyl[-1][-1] - p.start_pos - p.end_margin
    print(f"Path contains {i+1}/{len(amplitudes)} points ({round((i+1)/len(amplitudes)*100,3)} %) from the audio segment.")
    print(f"Engraving takes {round(used_length, 3)} mm, {round(used_length/(p.L - 2*p.end_margin)*100, 3)} % of the available space of the cylinder.")

    # Create the engraved cylinder and wire
    exporter.export_path_to_csv(path_points_cyl, p.output_folder+p.output_filename+'_cyl', split_files=p.split_files, files_per_turn=p.files_per_turn, cyl_coord=True)
    # exporter.export_path_to_csv(path_points_plane, p.output_folder+p.output_filename+'_plan', split_files=p.split_files, files_per_turn=p.files_per_turn, cyl_coord=False)

def amplitudes_to_disc_points(amplitudes: np.ndarray, frame_rate: float) -> None:
    """
    Convert a series of sound amplitudes to a list of points on a disc.
    
    The points are calculated based on the parameters defined in the `parameters.py` file.
    The points are then exported to a CSV file.


    Parameters
    ----------
    amplitudes : np.ndarray
        Array of sound amplitudes.
    frame_rate : float
        Frame rate of the audio signal in Hz.
        
    Returns
    -------
    None
    """
    path_points = []
    R_max, R_min = p.R - p.end_margin - p.start_pos, p.end_margin
    path_points.append((R_max+p.offset_from_centerline+amplitudes[0]*p.max_amplitude/2, 0, p.L-p.depth))
    for i,amp in enumerate(amplitudes[1:]):
        _, prev_teta, z = path_points[-1]
        
        teta = prev_teta + 2 * asin(p.speed_angular/(2*frame_rate))
        r = R_max * (1 - teta*p.pitch/(2*pi*(R_max - R_min))) + amp*p.max_amplitude/2 + p.offset_from_centerline

        if r < R_min:
            warnings.warn(f"Engraving stopped by center of disc.")
            break
        else:
            path_points.append((r, teta, z))

    used_radius = R_max - path_points[-1][0]
    print(f"Path contains {i+1}/{len(amplitudes)} points ({round((i+1)/len(amplitudes)*100,3)} %) from the audio segment.")
    print(f"Engraving is {round(used_radius, 3)} mm wide, {round(used_radius/(R_max - R_min)*100, 3)} % of the available space of the disc.")

    # Export the path to a CSV file
    out_name = p.output_folder+p.output_filename
    exporter.export_path_to_csv(path_points, out_name, split_files=p.split_files, files_per_turn=p.files_per_turn, cyl_coord=True)
    print(f"Exported file to {out_name}.")

def amplitudes_to_cylinder_image(amplitudes: np.ndarray, frame_rate: float) -> None:
    """
    Convert a series of sound amplitudes to a depth map on a cylinder.
    
    The depth map is represented as a 2D image, where each pixel corresponds to a point on the cylinder developped surface.
    The pixel color is calculated based on the parameters defined in the `parameters.py` file.
    The image is then exported in TIFF format, without compression.


    Parameters
    ----------
    amplitudes : np.ndarray
        Array of sound amplitudes.
    frame_rate : float
        Frame rate of the audio signal in Hz.
        
    Returns
    -------
    None
    """
    # Create blank image
    img_height, img_width = int(p.L / p.pixel_size), int(2 * p.R * np.pi / p.pixel_size)
    image = p.white * np.ones((img_height, img_width), dtype=np.uint8)

    # Color the pixel in the image
    for i,amp in enumerate(amplitudes):
        phase = (i) * p.speed_angular/frame_rate

        x = p.R * phase
        y = phase*p.pitch/(2*pi) + amp*p.max_amplitude/2 + p.end_margin + p.start_pos + p.offset_from_centerline
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
                image[y_pixel-2:y_pixel+3, x_pixel] = p.white*2/3
                image[y_pixel-1:y_pixel+2, x_pixel] = p.white*1/3
                image[y_pixel, x_pixel]             = p.white*0/3

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

def amplitudes_to_disc_image(amplitudes: np.ndarray, frame_rate: float) -> None:
    """
    Convert a series of sound amplitudes to a depth map on a disc.
    
    The depth map is represented as a 2D image, where each pixel corresponds to a point on the disc.
    The pixel color is calculated based on the parameters defined in the `parameters.py` file.
    The image is then exported in TIFF format, without compression.


    Parameters
    ----------
    amplitudes : np.ndarray
        Array of sound amplitudes.
    frame_rate : float
        Frame rate of the audio signal in Hz.

    Returns
    -------
    None
    """
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
    R_max, _ = p.R - p.end_margin - p.start_pos, p.end_margin
    path_points.append((R_max+p.offset_from_centerline+amplitudes[0]*p.max_amplitude/2, 0))
    for _,amp in enumerate(amplitudes):
        _, prev_teta = path_points[-1]
        
        teta = prev_teta + 2 * asin(p.speed_angular/(2*frame_rate))
        r = R_max * (1 - teta*p.pitch/(2*pi*R_max)) + amp*p.max_amplitude/2 + p.offset_from_centerline

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

def amplitudes_to_gcode(amplitudes: np.ndarray, frame_rate: float) -> None:
    """
    Convert a series of sound amplitudes to G-code for engraving on a cylinder.
    
    The G-code is generated based on the parameters defined in the `parameters.py` file.
    The G-code is then exported to a file.

    Parameters
    ----------
    amplitudes : np.ndarray
        Array of sound amplitudes.
    frame_rate : float
        Frame rate of the audio signal in Hz.

    Returns
    -------
    None
    """
    # Initialisation g-code blocks 
    text = ""
    gcode_one_pass = ""

    # Create g-code blocks for one pass of engraving
    length_one_pass = 0
    points = []
    x0, a0 = 0, 0
    for i,amp in enumerate(amplitudes):
        # Compute point
        phase = (i) * p.speed/p.R / frame_rate
        elevation = phase*p.pitch/(2*pi) + amp*p.max_amplitude/2 + p.end_margin + p.start_pos + p.offset_from_centerline
        if p.right_thread: phase = -phase
        points.append([phase, elevation]) 

        # Compute length of segment
        dphase = p.speed_angular/frame_rate
        dl = sqrt((sin(dphase) * (p.R-p.depth))**2 + (dphase*p.pitch/(2*pi) + amp*p.max_amplitude/2)**2)
        if elevation > p.L - p.end_margin:
            warnings.warn(f"Engraving stopped by end of cylinder.")
            break
        else:
            line = f"\nX{round(elevation, 3)}A{round(np.rad2deg(phase), 3)}"
            gcode_one_pass += line
            length_one_pass += dl
            if i == 0:
                x0 = round(elevation, 3)
                a0 = round(np.rad2deg(phase), 3)

    check_intersection(np.array(points), frame_rate)

    # Repeat for each pass
    cutted_depth = p.start_depth
    passes_depth = []
    total_length = 0.0
    while cutted_depth < p.depth:
        pass_depth = min(p.depth - cutted_depth, p.depth_of_cut)
        if pass_depth <= 0.01*p.depth_of_cut:
            break
        passes_depth.append(pass_depth)

        # Add one pass to gcode
        cutted_depth += pass_depth
        if len(passes_depth) > 1: 
            text += p.depth_change_sequence(cutted_depth, x0, a0)
        text += gcode_one_pass
        total_length += length_one_pass

    # Export G-code to a file
    exporter.export_text_to_gcode(text, x0, a0)
    print(f"Number of passes: {len(passes_depth)} ({[round(d*1e3, 0) for d in passes_depth]} [um])")
    print(f"Total engraving length: {total_length:.3f} mm")
    print(f"Machining time: ~{total_length / p.feed_rate // 60:.0f}h{total_length / p.feed_rate % 60:.0f}min")

def check_intersection(pts: np.ndarray, frame_rate: float) -> int:
    """
    Check if the engraving path intersects itself.
    
    This function is used to ensure that the engraving path does not overlap itself,
    which could lead to issues during the reading process. If such overlap occurs, it counts
    the number of intersections.

    Parameters
    ----------
    pts : np.ndarray
        Array of engraving points, in polar coordinates. [phase in rad, elevation]
    frame_rate : float
        Frame rate of the audio signal in Hz.

    Returns
    -------
    Number of detected intersections.
    """
    intersections = 0
    pts_per_turn = 2 * np.pi * p.R / p.speed * frame_rate
    nb_turns = floor(pts[-1, 0] / (2 * np.pi))

    # For each "angle", check if engraving points X coord. are strictly increasing with enough margin 
    for i in range(int(pts_per_turn)):
        curr_pts_elev = [pts[int(min(j*pts_per_turn+i, pts.shape[0]-1)) , 1] for j in range(nb_turns)]

        # Check that the elevation is strictly increasing
        for k in range(len(curr_pts_elev)-1):
            if curr_pts_elev[k+1] - curr_pts_elev[k] <= p.width + p.intersection_margin:
                intersections += 1
                if intersections >= 1: 
                    warnings.warn(f"Engraving path intersects itself at least at angle {round(np.rad2deg(pts[i, 0]) % 360, 2)}°, loop {k+1}&{k+2}. \t{curr_pts_elev}")
                warnings.warn(f"Engraving path intersects itself at least at angle {round(np.rad2deg(pts[i, 0]) % 360, 2)}°, loop {k+1}&{k+2}. \t{curr_pts_elev}")
                print(curr_pts_elev)
    return intersections