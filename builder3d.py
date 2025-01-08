from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.gp import gp_Pnt
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Wire
from math import cos, sin, tan, radians
import numpy as np

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

def create_triangle(pos_surface: list[float], depth: float, angle: float) -> TopoDS_Shape:
    """
    Create a triangle with the given position, depth and angle.

    :param pos_surface: The position of the triangle on the surface. [R, phi, z]
    :param depth: The depth of the triangle in mm
    :param angle: The angle of the tip of the triangle in degrees
    :return: The resulting triangle shape
    """
    R, φ, z = pos_surface
    dz = depth * tan(radians(angle/2))
    mf = 1.5 # margin factor. It ensures that the triangle intersects the surface of the cylinder. Could be as large as needed.
    
    # Define the points of the triangle
    p1 = gp_Pnt((R - depth)*cos(φ), (R - depth)*sin(φ), z)
    p2 = gp_Pnt(mf*R*cos(φ), mf*R*sin(φ), z - mf*dz)
    p3 = gp_Pnt(mf*R*cos(φ), mf*R*sin(φ), z + mf*dz)
    
    # Create a wire from the points
    triangle_wire = BRepBuilderAPI_MakePolygon(p1, p2, p3, True).Wire()
    
    # Create a face from the wire
    triangle_face = BRepBuilderAPI_MakeFace(triangle_wire).Face()
    
    return triangle_face

def create_triangle_at_start(tip_path: list[list[float]], angle: float) -> TopoDS_Shape:
    """
    Create a triangle at the start of the tip path, with the correct orientation.

    The triangle is coplanar to the z axis. Also, it points towards the center of the cylinder at the middle of the path.

    :param tip_path: List of two points defining the path of the tip. In cylindrical coordinates [R, φ, z]
    :param angle: Angle of the tip, in degrees.
    """
    h = 3 # height of the triangle TODO: make it a parameter
    dz = h * tan(radians(angle/2))

    start_tip, end_tip = tip_path
    _, φ, _ = g.midpoint(start_tip, end_tip)

    print(f"φ: {φ}")

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

def create_path(points: list[list[float]]) -> TopoDS_Wire:
    """
    Create a path wire from a list of points.

    :param points: A list of points defining the path. Each point is a list in cylindrical coordinates [R, φ, z].
    :return: The resulting path wire.
    """
    wire_builder = BRepBuilderAPI_MakePolygon()
    for point in points:
        x, y, z = g.cyl2cart(*point)
        print(x, y, z)
        wire_builder.Add(gp_Pnt(x, y, z))
    path_wire = wire_builder.Wire()
    
    return path_wire

def extrude_shape_along_path(shape, path_wire: TopoDS_Wire) -> TopoDS_Shape:
    """
    Extrude a shape along a path.

    :param shape: The shape to extrude.
    :param path_wire: The path along which to extrude the shape.
    :return: The resulting shape after extrusion.
    """
    pipe_maker = BRepOffsetAPI_MakePipe(path_wire, shape)
    extruded_shape = pipe_maker.Shape()
    
    return extruded_shape

def subtract_shapes(shape1, shape2) -> TopoDS_Shape:
    """
    Subtract shape2 from shape1.

    :param shape1: The shape from which to subtract.
    :param shape2: The shape to subtract.
    :return: The resulting shape after subtraction.
    """
    cut_shape = BRepAlgoAPI_Cut(shape1, shape2).Shape()
    return cut_shape

def export_to_step(shape: TopoDS_Shape, filename: str) -> None:
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

def carve_edge(cylinder: TopoDS_Shape, edge: list[list[float]], angle: float) -> TopoDS_Shape:
    """
    Carve one edge on the cylinder.

    :param cylinder: Cylinder to carve
    :param edge: A list of two points defining the path of the carving. Each point is a list in cylindrical coordinates [R, φ, z].
    """
    # Create the triangle shape
    triangle_shape = create_triangle_at_start(tip_path=edge, angle=angle)

    edge_wire = create_path(edge)

    # Extrude the triangle along the path
    extruded_triangle_shape = extrude_shape_along_path(triangle_shape, edge_wire)

    # Subtract the extruded triangle from the cylinder
    cylinder = subtract_shapes(cylinder, extruded_triangle_shape)

    return cylinder

def carve_corner(cylinder: TopoDS_Shape, edge: list[list[float]]) -> TopoDS_Shape:
    return cylinder


def create_engraved_cylinder(R: float, L: float, angle: float, path: list[list[float]], filename: str = "my_engraved_cylinder") -> None:
    """
    Create a cylinder with a cutout along a path.
    
    :param R: The radius of the cylinder in mm
    :param L: The length of the cylinder in mm
    :param angle: The angle of the tip of the carving in degrees
    :param path: A list of points defining the path of the needle tip in the engraving. Each point is a list [x, y, z].
    :param filename: The name of the output STEP file. Default is 'my_engraved_cylinder.stp'
    """
    # Create the cylinder shape
    cylinder_shape = create_cylinder(R, L)

    for i in range(len(path) - 1):
        edge = [path[i], path[i+1]]
        print(f"Carving edge {i+1}: {edge},\t{g.distance_cyl(edge[0], edge[1])}")

        cylinder_shape = carve_edge(cylinder_shape, edge, angle)
        cylinder_shape = carve_corner(cylinder_shape, path[i+1])

    # # Create the path wire
    # path_wire = create_path(path)

    # Export the result to a STEP file
    export_to_step(cylinder_shape, filename)