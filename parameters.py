from math import pi, tan, radians
from datetime import date

class ParameterSet:
    # Surface
    SURFACE_TYPE = 'disc'  # 'cylinder' or 'disc'
    R = 53.0/2  # Radius [mm]
    L = 5.0  # Length [mm]

    # Engraving
    ENGRAVING_OUTPUT_TYPE = 'image'  # 'points' or 'image'
    depth = 0.025  # Depth of the cut [mm]
    angle = 90.0  # Angle of the cut [°]
    width = 2 * depth * tan(radians(angle/2))  # Width of the cut [mm]
    pitch = 1 # Pitch of the spiral [mm]
    max_amplitude = 0.025 # Maximal amplitude of the engraved audio signal (peak-peak) [mm]
    speed_angular = 33.5/33.5*45*pi/30 # Rotational speed of a 12" vinyl [rad/s]
    speed = speed_angular*150/2 # Longitudinal reading speed of a 12" vinyl at the inner edge [mm/s]
    end_margin = 5 # Margin at the start and end of the engraving surface [mm]
    start_pos = 0 # Position of the start of the engraving
    split_files = False # True if the path must be split into multiple files
    files_per_turn = 20 # Number of files per turn of the cylinder
    offset_from_centerline = 0 #-width/2 # Used to create the path of the corner of the triangle on the surface [mm]

    # Audio
    filter_active = True
    cutoff_freq = 5000 # Hz
    start_time = 1 # How many seconds to crop from the start of the audio
    duration = 0.1 # Duration of the audio signal [s]

    # Image
    pixel_size = 0.01 # Size of a pixel in the image [mm]
    engraving_pixel_width = round(width / pixel_size) # Width of the engraving in pixels with a margin of 1 pixel on each side
    interpolate = True
    white = 255 # Color for the engraving
    black = 0 # Color for the engraving

    # Folders and file name
    input_folder = "./audio_files/"
    input_filename = "1000Hz.mp3"
    output_folder = "./3d_files/" # "images" or "3d_files"
    output_filename = f'{round(depth*1e3)}_{round(max_amplitude*1e3)}_{round(pitch*1e3)}_{input_filename.split(".")[0]}_path'
    
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        txt = ''
        for attr in [a for a in dir(self) if not a.startswith('__')]:
            txt += f'{attr} = {eval("self." + attr)}\n'
        
        txt += f'\nCreated on {date.today()}'
        return txt
    
default_parameters = ParameterSet()