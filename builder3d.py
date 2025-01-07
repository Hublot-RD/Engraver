from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.gp import gp_Pnt
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Wire
from math import cos, sin, tan, radians


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

def create_path(points: list[list[float]]) -> TopoDS_Wire:
    """
    Create a path wire from a list of points.

    :param points: A list of points defining the path. Each point is a list [x, y, z].
    :return: The resulting path wire.
    """
    wire_builder = BRepBuilderAPI_MakePolygon()
    for point in points:
        wire_builder.Add(gp_Pnt(point[0], point[1], point[2]))
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


def create_engraved_cylinder(R: float, L: float, depth: float, angle: float, path: list[list[float]], filename: str = "my_engraved_cylinder") -> None:
    """
    Create a cylinder with a cutout along a path.
    
    :param R: The radius of the cylinder in mm
    :param L: The length of the cylinder in mm
    :param depth: The depth of the carving in mm
    :param angle: The angle of the tip of the carving in degrees
    :param path: A list of points defining the path of the cutout. Each point is a list [x, y, z].
    :param filename: The name of the output STEP file. Default is 'my_engraved_cylinder.stp'
    """
    # Create the cylinder shape
    cylinder_shape = create_cylinder(R, L)

    # Create the triangle shape
    triangle_shape = create_triangle(pos_surface=[R, 0, 3], depth=depth, angle=angle)

    # Create the path wire
    path_wire = create_path(path[0:3])

    # Extrude the triangle along the path
    extruded_triangle_shape = extrude_shape_along_path(triangle_shape, path_wire)

    # Subtract the extruded triangle from the cylinder
    result_shape = subtract_shapes(cylinder_shape, extruded_triangle_shape)

    # Export the result to a STEP file
    export_to_step(result_shape, filename)