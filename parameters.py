from math import tan, radians, sqrt
from datetime import date
import attrs
from typing import Literal
import json


@attrs.define
class ParameterSet:
    # Surface
    SURFACE_TYPE:           Literal['cylinder', 'disc'] = attrs.field(default='cylinder')
    R:                      float = attrs.field(default=52/2)  # Radius of the cylinder [mm]
    L:                      float = attrs.field(default=100.0)  # Length of the cylinder [mm]

    # Engraving
    ENGRAVING_OUTPUT_TYPE:  Literal['gcode', 'points', 'image', 'wire'] = attrs.field(default='gcode')
    depth:                  float = attrs.field(default=0.100)  # Depth of the cut [mm]
    angle:                  float = attrs.field(default=60.0)  # Angle of the cut [°]
    width:                  float = attrs.field(init=False, default=None)  # Width of the cut [mm] - calculated, not initialized
    pitch:                  float = attrs.field(default=0.500) # Pitch of the spiral [mm]
    max_amplitude:          float = attrs.field(default=0.045) # Maximal amplitude of the engraved audio signal (peak-peak) [mm]
    speed_angular:          float = attrs.field(default=11.32) # Rotational speed the cylinder [rad/s]
    speed:                  float = attrs.field(init=False) # Longitudinal reading speed of the tip in the engraving [mm/s] - calculated
    end_margin:             float = attrs.field(default=0) # Margin at the start and end of the engraving surface [mm]
    start_pos:              float = attrs.field(default=2.5) # Position of the start of the engraving
    split_files:            bool = attrs.field(default=False) # True if the path must be split into multiple files
    files_per_turn:         int = attrs.field(default=20) # Number of files per turn of the cylinder
    offset_from_centerline: float = attrs.field(default=0.0) #-width/2 # Used to create the path of the corner of the triangle on the surface [mm]
    intersection_margin:    float = attrs.field(default=0.010) # Margin
    right_thread:           bool = attrs.field(default=True) # True if the engraving spiral is right threaded, otherwise left threaded
    
    # Audio
    filter_active:          bool = attrs.field(default=True)
    cutoff_freq:            int = attrs.field(default=3000) # Hz
    start_time:             float = attrs.field(default=0) # How many seconds to crop from the start of the audio
    duration:               float = attrs.field(default=28.5) # Duration of the audio signal [s]
    silent_start_duration:  float = attrs.field(default=0.5) # Duration of the silent start [s]
    target_volume:          float = attrs.field(default=-18.0) # Target amplitude for the sound [dBFS]. In Europe, the EBU recommend that −18 dBFS equates to the alignment level.

    # Image
    pixel_size:             float = attrs.field(default=0.01) # Size of a pixel in the image [mm]
    engraving_pixel_width:  int = attrs.field(init=False) # Width of the engraving in pixels with a margin of 1 pixel on each side - calculated
    interpolate:            bool = attrs.field(default=True)
    white:                  int = attrs.field(default=255) # Color for the engraving
    black:                  int = attrs.field(default=0) # Color for the engraving

    # Folders and file name
    input_folder:           str = attrs.field(default="./audio_files/")
    input_filename:         str = attrs.field(default="DJSaphir.mp3")
    output_folder:          str = attrs.field(default="./3d_files/") # "images" or "3d_files"
    output_filename:        str = attrs.field(init=False)

    # G-code
    feed_rate:              float = attrs.field(default=450.0) # [mm/min]
    spindle_speed:          int = attrs.field(default=15000) # [rpm]
    clearance:              float = attrs.field(default=5.0) # [mm]
    depth_of_cut:           float = attrs.field(default=0.045) # [mm] Depth of cut for one pass
    start_depth:            float = attrs.field(default=0.000) # [mm] Initial depth of the engraving
    tool_number:            int = attrs.field(default=22)
    corrector_number:       int = attrs.field(default=22)
    file_format:            str = attrs.field(default="iso")
    max_text_size:          int = attrs.field(default=900*1024*1024) # [bytes] (= 900 MB)
    FINAL_GCODE:            str = attrs.field(init=False)

    def INITIAL_GCODE(self, x0: str = '0.0', a0: str = '0.0', file_ID: str = '') -> str:
        # Start outside of the cylinder and penetrate from the side
        depth_first_pass = self.depth_of_cut + self.start_depth
        y0 = round(2*sqrt(2*self.R*depth_first_pass - depth_first_pass**2), 3) 
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
G0X{x0}Y{y0}A{a0}
G43Z150.H{self.corrector_number}M13S{round(self.spindle_speed, 0)}
G0Z{round(self.R-self.start_depth-self.depth_of_cut,3)}
G1Y0.F{round(self.feed_rate,3)}"""

    def depth_change_sequence(self, desired_depth: float, x0: float, a0: float) -> str:
        '''
        Generate the G-code for changing the depth of the engraving.

        Goes up, to initial position, then enter the cylinder from y0 to 0. 

        :param desired_depth: The depth of the engraving for the next pass.
        :return: The G-code for changing the depth.
        '''
        y0 = round(2*sqrt(2*self.R*desired_depth - desired_depth**2), 3)
        return f"""
( Depth change to {round(1e3*desired_depth,0)} um )
G0Z{round(self.R+self.clearance,3)}
G0X{x0}Y{y0}A{a0}
M01
( New depth: {round(1e3*desired_depth,0)} um )
M13S{round(self.spindle_speed, 0)}
G0Z{round(self.R-desired_depth,3)}
G1Y0.F{round(self.feed_rate,3)}"""

    def __attrs_post_init__(self):
        # Calculate derived attributes
        self.width = 2 * self.depth * tan(radians(self.angle/2))
        self.speed = self.speed_angular * self.R
        self.engraving_pixel_width = round(self.width / self.pixel_size)
        self.output_filename = f'{round(self.depth*1e3)}_{round(self.max_amplitude*1e3)}_{round(self.pitch*1e3)}_{self.input_filename.split(".")[0]}_path'
        self.FINAL_GCODE = f"""
G0Z{round(self.R-self.depth+self.clearance,3)}
G0Z150.
G49G53Z0.
M15
G53Z0.
M30
%
"""
        
    def __str__(self) -> str:
        txt = ''
        for a in attrs.fields(self.__class__):
            txt += f'{a.name} = {getattr(self, a.name)}\n'
        
        txt += f'\nCreated on {date.today()}'
        return txt
    
    def export_parameters_to_txt(self) -> None:
        """
        Exports the ParameterSet object to a text file in JSON format.
        """
        with open(self.output_folder+self.output_filename+"_parameters.txt", 'w') as f:
            json.dump(attrs.asdict(self), f, indent=4)

    @classmethod
    def from_txt(cls, filename: str) -> "ParameterSet":
        """
        Imports a ParameterSet object from a text file in JSON format.
        """
        print(f"Importing parameters from {filename}")
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

                # Remove keys that are calculated
                non_init_fields = [field.name for field in attrs.fields(cls) if field.init is False]
                for field_name in non_init_fields:
                    data.pop(field_name, None)

                return cls(**data)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found. Returning default ParameterSet.")
            return cls()  # Return a default ParameterSet
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in '{filename}'. Returning default ParameterSet.")
            return cls()  # Return a default ParameterSet
        except TypeError as e:
            print(f"Error: Type mismatch or invalid value in file: {e}. Returning default ParameterSet.")
            return cls()  # Return a default ParameterSet
    
default_parameters = ParameterSet()
# default_parameters = ParameterSet.from_txt("./3d_files/25_100_500_squeezie_path_parameters.txt")

if __name__ == '__main__':
    default_parameters.export_parameters_to_txt()