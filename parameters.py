from math import pi
from datetime import date

class ParameterSet:
    # Cylinder
    R = 56.0/2  # Radius [mm]
    L = 120.0  # Length [mm]

    # Engraving
    depth = 0.025  # Depth of the cut [mm]
    angle = 90.0  # Angle of the cut [°]
    pitch = 0.125 # Pitch of the spiral [mm]
    max_amplitude = 0.1 # Maximal amplitude of the engraved audio signal (peak-peak) [mm]
    speed = 33.5*pi/30*150/2 # Longitudinal reading speed of a 12" vinyl at the inner edge [mm/s]
    end_margin = 5 # Margin at the start and end of the cylinder [mm]
    start_pos = 0 # Position of the start of the engraving

    # Audio
    filter_active = True
    cutoff_freq = 5000 # Hz
    start_time = 0 # How many seconds to crop from the start of the audio
    duration = 1 # Duration of the audio signal [s]

    # Folders and file name
    input_folder = "./audio_files/"
    input_filename = "1000Hz.mp3"
    output_folder = "./3d_files/"
    output_filename = input_filename.split('.')[0] + "_tip_path"
    
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        txt = ''
        for attr in [a for a in dir(self) if not a.startswith('__')]:
            txt += f'{attr} = {eval("self." + attr)}\n'
        
        txt += f'\nCreated on {date.today()}'
        return txt
    
default_parameters = ParameterSet()