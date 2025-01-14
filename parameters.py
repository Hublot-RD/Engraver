# Cylinder
R = 27.0  # Radius [mm]
L = 120.0  # Length [mm]
# L = 10

# Engraving
depth = 0.2  # Depth of the cut [mm]
angle = 90.0  # Angle of the cut [°]
pitch = 4 # Pitch of the spiral [mm]
max_amplitude = 1.5 # Maximal amplitude of the engraved audio signal [mm]
# speed = 100 # Longitudinal reading speed of the engraving [mm/s]
speed = 33.5*3.1415/30*150 # Longitudinal reading speed of a 12" vinyl at the outer edge [mm/s]
end_margin = 55 # Margin at the start and end of the cylinder [mm]

# Audio
filter_active = True
cutoff_freq = 5000 # Hz

# Folders and file name
input_folder = "./audio_files/"
input_filename = "michel.mp3"
output_folder = "./3d_files/"
# output_filename = "engraved_cylinder.stp"
output_filename = "tip_path_audio"