from math import floor, pi
import os
# from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
# from OCC.Core.IFSelect import IFSelect_RetDone
# from OCC.Core.TopoDS import TopoDS_Shape

from parameters import default_parameters as p
import geometry as g


def export_path_to_csv(path: list[tuple[float, float, float]], filename: str, split_files: bool=True, files_per_turn: float = 4, cyl_coord: bool=True) -> None:
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
        nb_loops = floor(path[-1][1] / (2*pi/files_per_turn))
        for i in range(nb_loops):
            end = next((index for index, point in enumerate(path) if point[1] >= (i+1)*2*pi/files_per_turn), len(path))
            loops.append(path[start:end])
            start = end - 2 # -2 so that the next loop has 2 points in common with the previous one

        for i, loop in enumerate(loops):
            # Format i as string with three numbers
            loop_filename = f"{folder}/{filename}_{i :03d}.csv"
            export_path_to_csv(loop, loop_filename, False)
        print(f"CSV files created successfully in folder '{folder}'.")
    else:
        filename += '.csv'
        with open(filename, "w") as file:
            for point in path:
                if cyl_coord: x, y, z = g.cyl2cart(*point)
                else: x, y, z = point
                file.write(f"{x/1000}, {y/1000}, {z/1000}\n")
        # print(f"CSV file '{filename}' created successfully.")

def export_text_to_gcode(text: str) -> None:
    """
    Export the given text to a G-code file.

    INITIAL_GCODE and FINAL_GCODE are included in the exported file. 
    If the file size exceeds the maximum limit, it is split into multiple files.

    Parameters
    ----------
    text : str
        The text to export.
    """
    # Split the text into chunks if it exceeds the maximum size
    for file_num, idx in enumerate(range(0, len(text), p.max_text_size)):
        chunk = text[idx:idx+p.max_text_size]
        filename = p.output_folder+p.output_filename+f"_{file_num+1}."+p.file_format
        chunk = p.INITIAL_GCODE(str(file_num+1)) + chunk + p.FINAL_GCODE
        with open(filename, 'w') as f:
            f.write(chunk)
        print(f"G-code exported to {filename}")

# def export_shape_to_step(shape: TopoDS_Shape, filename: str) -> None:
#     """
#     Export a shape as an STL file.

#     :param shape: The shape to export.
#     :param filename: Filename for the STL file. Can include .stl or not.
#     """
#     # Initialize STEP writer
#     step_writer = STEPControl_Writer()
    
#     # Transfer the shape to the STEP writer
#     step_writer.Transfer(shape, STEPControl_AsIs)
    
#     if filename.endswith(".stp") is False:
#         filename += ".stp"
#     status = step_writer.Write(filename)
    
#     if status == IFSelect_RetDone:
#         print(f"STEP file '{filename}' created successfully.")
#     else:
#         print("Error: Failed to create STEP file.")