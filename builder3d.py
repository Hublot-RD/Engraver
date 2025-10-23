import cadquery as cq
from math import pi, cos
import exporter


def create_tip_path_wire(tip_path: list[tuple[float, float, float]], filename: str = "my_tip_path") -> None:
    """
    Create a wire following the path and export it as an STEP file.

    :param tip_path: A list of points defining the path of the needle tip in the engraving. Each point is a tuple in cartesian coordinates [x, y, z].
    :param filename: The name of the output STEP file. Default is 'my_engraved_cylinder.stp'
    """
    # Create a wire from the given points
    vectors = []
    for p in tip_path:
        x, y, z = p
        vectors.append(cq.Vector(x, y, z))

    # Create the wire
    wire = cq.Wire.makePolygon(vectors)

    # Export the result to a STEP file
    cq.Workplane("XY").add(wire).val().exportStep(filename)


# Example usage
if __name__ == "__main__":
    from numpy import linspace
    
    # Define the cylinder parameters
    R = 26.5  # Radius
    L = 125.0  # Length

    # Define the engraving parameters
    depth = 0.05  # Depth of the cut [mm]
    angle = 90.0  # Angle of the cut
    pitch = 3 # Pitch of the spiral [mm]
    end_margin = 55 # Non engraved margin at each end of the cylinder

    # Define the path points (example: a spiral path)
    path_points = [(R-depth, t/pitch*pi, t+end_margin+cos(10*t)) for t in linspace(0, L-2*end_margin, 1000)]

    # Create the csv file with the path point coordinates
    output_filename = "./3d_files/test_tip_path.csv"
    exporter.export_path_to_csv(path_points, output_filename, files_per_turn=5)

    # # Create the cylinder with a cutout along the path
    # output_filename = "./3d_files/test_engraved_cylinder.stp"
    # create_engraved_cylinder(R, L, angle, path_points, output_filename)

    # # Create a wire of the same path
    # output_filename = "./3d_files/test_tip_path.stp"
    # create_tip_path_wire(path_points, output_filename)
