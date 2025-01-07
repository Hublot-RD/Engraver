from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.gp import gp_Pnt
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopoDS import TopoDS_Shape
from math import cos, sin, tan, radians


def create_cylinder(r: float, l: float) -> TopoDS_Shape:
    """
    Create a cylinder with the given radius and length
    
    :param r: The radius of the cylinder in mm
    :param l: The length of the cylinder in mm
    """
    
    cylinder = BRepPrimAPI_MakeCylinder(r, l).Shape()
    return cylinder

def create_triangle(pos_surface: list[float], depth: float, angle: float) -> TopoDS_Shape:
    """
    Create a triangle with the given position, depth and angle.

    :param pos_surface: The position of the triangle in the surface. [R, phi, z]
    :param depth: The depth of the triangle in mm
    :param angle: The angle of the tip of the triangle in degrees
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

def create_path(points):
    # Create a wire from the given path points
    wire_builder = BRepBuilderAPI_MakePolygon()
    for point in points:
        wire_builder.Add(gp_Pnt(point[0], point[1], point[2]))
    # wire_builder.Close()
    path_wire = wire_builder.Wire()
    
    return path_wire

def extrude_shape_along_path(shape, path_wire):
    pipe_maker = BRepOffsetAPI_MakePipe(path_wire, shape)
    extruded_shape = pipe_maker.Shape()
    
    return extruded_shape

def subtract_shapes(shape1, shape2):
    # Perform the subtraction (shape1 - shape2)
    cut_shape = BRepAlgoAPI_Cut(shape1, shape2).Shape()
    return cut_shape

def export_to_step(shape, filename):
    # Initialize STEP writer
    step_writer = STEPControl_Writer()
    
    # Transfer the shape to the STEP writer
    step_writer.Transfer(shape, STEPControl_AsIs)
    
    # Write the shape to the STEP file
    status = step_writer.Write(filename)
    
    if status == IFSelect_RetDone:
        print(f"STEP file '{filename}' created successfully.")
    else:
        print("Error: Failed to create STEP file.")


if __name__ == "__main__":
    # Define the cylinder parameters
    R = 10.0  # Radius
    L = 50.0  # Length

    # Define the path points (example: a spiral path)
    path_points = [(R*cos(t), R*sin(t), t) for t in range(0, int(L), 1)]

    # Define the output STEP file name
    output_filename = "cylinder_with_cutout.stp"

    # Create the cylinder shape
    cylinder_shape = create_cylinder(R, L)

    # Create the triangle shape
    triangle_shape = create_triangle(pos_surface=[R, 0, 3], depth=3, angle=60)

    # Create the path wire
    path_wire = create_path(path_points[0:3])

    # Extrude the triangle along the path
    extruded_triangle_shape = extrude_shape_along_path(triangle_shape, path_wire)

    # Subtract the extruded triangle from the cylinder
    result_shape = subtract_shapes(cylinder_shape, extruded_triangle_shape)

    # Export the result to a STEP file
    export_to_step(result_shape, output_filename)