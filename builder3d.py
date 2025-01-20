from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeRevol, BRepPrimAPI_MakePrism
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.gp import gp_Pnt, gp_Ax1, gp_Dir, gp_Vec
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Wire
from math import tan, radians, floor
import numpy as np
import os, glob

import geometry as g


def create_cylinder(r: float, l: float) -> TopoDS_Shape:
    """
    Create a cylinder with the given radius and length
    
    :param r: The radius of the cylinder in mm
    :param l: The length of the cylinder in mm
    :return: The resulting cylinder shape
    """
    cylinder = BRepPrimAPI_MakeCylinder(r, l).Shape()
    return cylinder

def create_triangle_for_edge(tip_path: list[tuple[float, float, float]], angle: float) -> TopoDS_Shape:
    """
    Create a triangle at the start of the tip path, with the correct orientation.

    The triangle is coplanar to the z axis. Also, it points towards the center of the cylinder at the middle of the path.

    :param tip_path: List of two points defining the path of the tip. In cylindrical coordinates [R, φ, z]
    :param angle: Angle of the tip, in degrees.
    """
    h = 10 # height of the triangle TODO: make it a parameter
    dz = h * tan(radians(angle/2))

    start_tip, end_tip = tip_path
    _, φ, _ = g.midpoint(start_tip, end_tip)

    # Define triangle points in carthesion coordinates, after rotation
    t = np.array(g.cyl2cart(0, 0, 0))
    bh = np.array(g.cyl2cart(h, φ, dz))
    bl = np.array(g.cyl2cart(h, φ, -dz))

    # Move the triangle to the start of the tip path
    start_tip_cart = np.array(g.cyl2cart(*start_tip))
    t += start_tip_cart
    bh += start_tip_cart
    bl += start_tip_cart
    
    # Create a face from points of the triangle
    p1 = gp_Pnt(*t)
    p2 = gp_Pnt(*bh)
    p3 = gp_Pnt(*bl)
    triangle_wire = BRepBuilderAPI_MakePolygon(p1, p2, p3, True).Wire()
    triangle_face = BRepBuilderAPI_MakeFace(triangle_wire).Face()
    
    return triangle_face

def create_triangle_for_corner(tip_path: list[tuple[float, float, float]], angle: float) -> TopoDS_Shape:
    """
    Create a triangle at the start of the tip path, with the correct orientation.

    The triangle is coplanar to the z axis. Also, it points towards the center of the cylinder at the middle of the path.

    :param tip_path: List of two points defining the path of the tip. In cylindrical coordinates [R, φ, z]
    :param angle: Angle of the tip, in degrees.
    """
    h = 10 # height of the triangle TODO: make it a parameter
    dz = h * tan(radians(angle/2))

    left, corner, _ = tip_path
    _, φ, _ = g.midpoint(left, corner)

    # Define triangle points in carthesion coordinates, after rotation
    t = np.array(g.cyl2cart(0, 0, 0))
    bh = np.array(g.cyl2cart(h, φ, dz))
    bl = np.array(g.cyl2cart(h, φ, -dz))

    # Move the triangle to the start of the tip path
    start_tip_cart = np.array(g.cyl2cart(*corner))
    t += start_tip_cart
    bh += start_tip_cart
    bl += start_tip_cart
    
    # Create a face from points of the triangle
    p1 = gp_Pnt(*t)
    p2 = gp_Pnt(*bh)
    p3 = gp_Pnt(*bl)
    triangle_wire = BRepBuilderAPI_MakePolygon(p1, p2, p3, True).Wire()
    triangle_face = BRepBuilderAPI_MakeFace(triangle_wire).Face()
    
    return triangle_face

def subtract_shapes(shape1, shape2) -> TopoDS_Shape:
    """
    Subtract shape2 from shape1.

    :param shape1: The shape from which to subtract.
    :param shape2: The shape to subtract.
    :return: The resulting shape after subtraction.
    """
    cut_shape = BRepAlgoAPI_Cut(shape1, shape2).Shape()
    return cut_shape

def export_shape_to_step(shape: TopoDS_Shape, filename: str) -> None:
    """
    Export a shape as an STL file.

    :param shape: The shape to export.
    :param filename: Filename for the STL file. Can include .stl or not.
    """
    # Initialize STEP writer
    step_writer = STEPControl_Writer()
    
    # Transfer the shape to the STEP writer
    step_writer.Transfer(shape, STEPControl_AsIs)
    
    if filename.endswith(".stp") is False:
        filename += ".stp"
    status = step_writer.Write(filename)
    
    if status == IFSelect_RetDone:
        print(f"STEP file '{filename}' created successfully.")
    else:
        print("Error: Failed to create STEP file.")

def export_path_to_csv(path: list[tuple[float, float, float]], filename: str, split_files: bool=True) -> None:
    """
    Export a path as one or multiple CSV files in cartesian coordinates.

    :param path: The path to export.
    :param filename: Filename for the CSV file. Can include .csv or not.
    :param split_files: If True, each loop will be written to a separate file, in a folder. If False, all points will be written to a single file.
    """
    if filename.endswith(".csv") is True:
        filename = filename[:-4]

    if split_files:
        folder = filename + "_files"
        filename = filename.split("/")[-1]

        # Create new empty folder
        os.makedirs(folder, exist_ok=True)
        # files = glob.glob(folder+'*')
        # for f in files:
        #     os.remove(f)

        # Split the path into each loop
        start = 0
        loops = []
        nb_loops = floor(path[-1][1] / (2*pi))
        for i in range(nb_loops):
            end = next((index for index, point in enumerate(path) if point[1] >= (i+1)*2*pi), len(path))
            loops.append(path[start:end])
            start = end - 1 # -1 so that the next loop starts at the same point as the previous one

        for i, loop in enumerate(loops):
            loop_filename = f"{folder}/{filename}_{i}.csv"
            export_path_to_csv(loop, loop_filename, False)
        print(f"CSV files created successfully in folder '{folder}'.")
    else:
        filename += '.csv'
        with open(filename, "w") as file:
            for point in path:
                x, y, z = g.cyl2cart(*point)
                file.write(f"{x/1000}, {y/1000}, {z/1000}\n")
        print(f"CSV file '{filename}' created successfully.")

def carve_edge(cylinder: TopoDS_Shape, tip_path: list[tuple[float, float, float]], angle: float) -> TopoDS_Shape:
    """
    Carve one edge on the cylinder.

    :param cylinder: Cylinder to carve
    :param edge: A list of two points defining the path of the carving. Each point is a tuple in cylindrical coordinates [R, φ, z].
    """
    # Create the triangle shape
    triangle_shape = create_triangle_for_edge(tip_path=tip_path, angle=angle)

    # Create extrusion vector
    tip_path = [g.cyl2cart(*point) for point in tip_path]
    displacement = [tip_path[1][i]-tip_path[0][i] for i in range(3)]
    displacement_Vec = gp_Vec(*displacement)

    # Extrude the triangle along the path
    extruded_triangle_shape = BRepPrimAPI_MakePrism(triangle_shape, displacement_Vec).Shape()

    # Subtract the extruded triangle from the cylinder
    cylinder = subtract_shapes(cylinder, extruded_triangle_shape)

    return cylinder

def carve_corner(cylinder: TopoDS_Shape, tip_path: list[tuple[float, float, float]], angle: float) -> TopoDS_Shape:
    """
    Carve one corner on the cylinder.

    :param cylinder: Cylinder to carve
    :param edge: A list of three points defining the corner of the carving. Each point is a tuple in cylindrical coordinates [R, φ, z].
    """
    left, corner, right = tip_path

    # Create the triangle shape
    triangle_shape = create_triangle_for_corner(tip_path=tip_path, angle=angle)

    # Create revolve parameters
    x, y, z = g.cyl2cart(*corner)
    axis = gp_Ax1(gp_Pnt(x, y, z), gp_Dir(0, 0, 1)) # Along z axis
    angle = (right[1] - left[1]) / 2

    # Extrude the triangle along the path
    revol = BRepPrimAPI_MakeRevol(triangle_shape, axis, angle)
    revolveded_triangle_shape = revol.Shape()

    # Subtract the extruded triangle from the cylinder
    cylinder = subtract_shapes(cylinder, revolveded_triangle_shape)
    return cylinder

def create_engraved_cylinder(R: float, L: float, angle: float, tip_path: list[tuple[float, float, float]], filename: str = "my_engraved_cylinder") -> None:
    """
    Create a cylinder with a cutout along a path and export it as an STEP file.
    
    :param R: The radius of the cylinder in mm
    :param L: The length of the cylinder in mm
    :param angle: The angle of the tip of the carving in degrees
    :param tip_path: A list of points defining the path of the needle tip in the engraving. Each point is a tuple in cylindrical coordinates [R, φ, z].
    :param filename: The name of the output STEP file. Default is 'my_engraved_cylinder.stp'
    """
    # Create the cylinder shape
    cylinder_shape = create_cylinder(R, L)

    # Carve edges
    for i in range(len(tip_path) - 2):
        edge = [tip_path[i], tip_path[i+1], tip_path[i+2]]
        # print(f"Carving edge {i+1}: {edge},\t{g.distance_cyl(edge[0], edge[1])}")

        cylinder_shape = carve_edge(cylinder_shape, edge[:-1], angle)
        cylinder_shape = carve_corner(cylinder_shape, edge, angle)
    
    # Carve final edge
    cylinder_shape = carve_edge(cylinder_shape, [tip_path[-2], tip_path[-1]], angle)

    # Export the result to a STEP file
    export_shape_to_step(cylinder_shape, filename)

def create_tip_path_wire(tip_path: list[tuple[float, float, float]], filename: str = "my_tip_path") -> None:
    """
    Create a wire following the path and export it as an STEP file.

    :param tip_path: A list of points defining the path of the needle tip in the engraving. Each point is a tuple in cylindrical coordinates [R, φ, z].
    :param filename: The name of the output STEP file. Default is 'my_engraved_cylinder.stp'
    """
    # Create a wire from the given points
    wire_builder = BRepBuilderAPI_MakePolygon()
    for point in tip_path:
        point = g.cyl2cart(*point)
        wire_builder.Add(gp_Pnt(*point))
    wire = wire_builder.Wire()
    
    # Export the result to a STEP file
    export_shape_to_step(wire, filename)


# Example usage
if __name__ == "__main__":
    from math import pi
    from numpy import linspace
    
    # Define the cylinder parameters
    R = 27.0  # Radius
    L = 120.0  # Length

    # Define the engraving parameters
    depth = 0.2  # Depth of the cut [mm]
    angle = 90.0  # Angle of the cut
    pitch = 3 # Pitch of the spiral [mm]
    end_margin = 5 # Non engraved margin at each end of the cylinder

    # Define the path points (example: a spiral path)
    path_points = [(R-depth, t/pitch*pi, t+end_margin) for t in linspace(0, L-2*end_margin, 500)]

    # Create the csv file with the path point coordinates
    output_filename = "./3d_files/test_tip_path.csv"
    export_path_to_csv(path_points, output_filename)

    # # Create the cylinder with a cutout along the path
    # output_filename = "./3d_files/test_engraved_cylinder.stp"
    # create_engraved_cylinder(R, L, angle, path_points, output_filename)

    # # Create a wire of the same path
    # output_filename = "./3d_files/test_tip_path.stp"
    # create_tip_path_wire(path_points, output_filename)
