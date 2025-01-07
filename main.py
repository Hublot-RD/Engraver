from math import cos, sin
from builder3d import create_engraved_cylinder 


if __name__ == "__main__":
    # Define the cylinder parameters
    R = 10.0  # Radius
    L = 50.0  # Length

    # Define the engraving parameters
    depth = 1.0  # Depth of the cutout
    angle = 90.0  # Angle of the cut

    # Define the path points (example: a spiral path)
    path_points = [(R*cos(t), R*sin(t), t) for t in range(0, int(L), 1)]

    # Define the output STEP file name
    output_filename = "cylinder_with_cutout.stp"

    # Create the cylinder with a cutout along the path
    create_engraved_cylinder(R, L, depth, angle, path_points[0:5], output_filename)