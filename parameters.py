from math import pi, tan, radians
from datetime import date

class ParameterSet:
    # Surface
    SURFACE_TYPE = 'cylinder'  # 'cylinder' or 'disc'
    R = 53.0/2  # Radius [mm]
    L = 125.0  # Length [mm]

    # Engraving
    ENGRAVING_OUTPUT_TYPE = 'gcode'  # 'points', 'image' or 'gcode'
    depth = 0.025  # Depth of the cut [mm]
    angle = 90.0  # Angle of the cut [°]
    width = 2 * depth * tan(radians(angle/2))  # Width of the cut [mm]
    pitch = 0.5 # Pitch of the spiral [mm]
    max_amplitude = 0.100 # Maximal amplitude of the engraved audio signal (peak-peak) [mm]
    speed_angular = 11.32 # Rotational speed the cylinder [rad/s]
    speed = speed_angular*R # Longitudinal reading speed of the tip in the engraving [mm/s]
    end_margin = 0 # Margin at the start and end of the engraving surface [mm]
    start_pos = 10 # Position of the start of the engraving
    split_files = True # True if the path must be split into multiple files
    files_per_turn = 20 # Number of files per turn of the cylinder
    offset_from_centerline = 0 #-width/2 # Used to create the path of the corner of the triangle on the surface [mm]
    intersection_margin = 0.010 # Margin
    right_thread = True # True if the engraving spiral is right threaded, otherwise left threaded
    
    # Audio
    filter_active = True
    cutoff_freq = 3000 # Hz
    start_time = 0 # How many seconds to crop from the start of the audio
    duration = 12.0 # Duration of the audio signal [s]
    silent_start_duration = 0.5 # Duration of the silent start [s]

    # Image
    pixel_size = 0.01 # Size of a pixel in the image [mm]
    engraving_pixel_width = round(width / pixel_size) # Width of the engraving in pixels with a margin of 1 pixel on each side
    interpolate = True
    white = 255 # Color for the engraving
    black = 0 # Color for the engraving

    # Folders and file name
    input_folder = "./audio_files/"
    input_filename = "english.mp3"
    output_folder = "./3d_files/" # "images" or "3d_files"
    output_filename = f'{round(depth*1e3)}_{round(max_amplitude*1e3)}_{round(pitch*1e3)}_{input_filename.split(".")[0]}_path'

    # G-code
    feed_rate = 50.0 # [mm/min]
    spindle_speed = 6366 # [rpm]
    clearance = 5.0 # [mm]
    tool_number = 19
    corrector_number = 19
    file_format = "iso"
    max_text_size = 450*1024 # [bytes] (= 450 KB)
    def INITIAL_GCODE(self, x0: str = '0.0', a0: str = '0.0', file_ID: str = '') -> str:
        return f"""%
O0001 ({self.input_filename.split(".")[0]} {file_ID})
( PART NAME : {self.output_filename} )
( MACH TYPE : Fraiseuse vert. 4 axes )
( POST TYPE : Fraisage 4axes Fanuc 0iM.GCv11 )
( {date.today()} )
( OUTPUT IN ABSOLUTE MILLIMETERS )
G21
G53Z0.
G49
G17G80G40G94
M6T{self.tool_number}
G90G54
M11
G0X{x0}Y0.A{a0}
G43Z150.H{self.corrector_number}M13S{round(self.spindle_speed, 0)}
G0Z{round(self.R+self.clearance,3)}
G1Z{round(self.R-self.depth,3)}F{round(self.feed_rate,3)}"""
    FINAL_GCODE = f"""
G0Z{round(R-depth+clearance,3)}
G0Z150.
G49G53Z0.
M15
G53Z0.
M30
%
"""


    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        txt = ''
        for attr in [a for a in dir(self) if not a.startswith('__')]:
            txt += f'{attr} = {eval("self." + attr)}\n'
        
        txt += f'\nCreated on {date.today()}'
        return txt
    
default_parameters = ParameterSet()