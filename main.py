from math import pi
from numpy import linspace
from builder3d import create_engraved_cylinder 


if __name__ == "__main__":
    # Define the cylinder parameters
    R = 27.0  # Radius
    L = 120.0  # Length

    # Define the engraving parameters
    depth = 1.0  # Depth of the cut [mm]
    angle = 90.0  # Angle of the cut
    pitch = 5 # Pitch of the spiral [mm]

    # Define the path points (example: a spiral path)
    path_points = [(R-depth, t/pitch*pi, t) for t in linspace(0, L, 200)]

    # Define the output STEP file name
    output_filename = "./3d_files/cylinder_with_cutout.stp"

    # Create the cylinder with a cutout along the path
    create_engraved_cylinder(R, L, angle, path_points, output_filename)