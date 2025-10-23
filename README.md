# Engraver

Scripts to generate engraving files from audio.

## Installation

1. Install conda (for example, from [Miniforge](https://docs.conda.io/projects/conda/en/stable/)).
1. Follow instructions [here](https://cadquery.readthedocs.io/en/latest/installation.html) to install the library. (Only required to export path to STEP and DXF)
1. Install all other packages listed in *requirements.txt*

## Usage

1. Add your *.mp3* audio file to the *audio_files* folder
1. In *parameters.py*, edit *input_filename* with the name of your file. Modify any other relevant parameter.
1. Run *main.py* and check that it created a new engraving file named *input_filename.iso*
1. Copy the file to a USB stick
1. Run the program on the CNC machine (TRIDENT TR 60A)

# Documentation

## Architecture

The software is organized into multiple files to improve readability. They are:

1. **main.py:** Calls functions from other modules to create the engraving files.
1. **audio_processor.py:** Reads, filter, crop, extend, and extract the amplitude of audio files.
1. **amp2engraving.py:** Convert an amplitude series to an engraving object.
1. **exporter.py:** Saves an engraving object in different formats.
1. **parameters.py:** Groups all software parameters in a single structure and saves it as a text file.
1. **geometry.py:** Mathematical utility functions to switch between coordinate frames.

## Current version: G-code creator

The current state of the project can generate G-codes for the TRIDENT TR 60A. The python script reads an audio file and extracts an amplitude time series. It is then converted into a helical path that the engraving tip must follow. This path is exported as a G-code file (or multiple to respect the size limit) that is ready to use on the machine.

## Current version: Wire creator

The project can also generate a STEP and a DXF file representing the engraving path. There is no volume information, making generation fast and files "light". We are working with suppliers to see if this option is ok for them.


# Legacy documentation
Many features included in the code are not relevant for the final use, as the engraving technique has changed multiple times. Here is some information about those topics.


## Construction of a volumic engraving using a CAD software

The engraving automation is split in two part: Python and a CAD Macro. Both SolidWorks and FreeCAD can be used. FreeCAD struggles to perform clean volumic engraving but is faster for 3D sketches.

### Python: From audio to trajectory

A Python script (*main.py*) reads an audio file. From the amplitude time series of the audio, a 3D trajectory is generated following a helical path. This trajectory is cut into several pieces, each spanning half a turn, saved individually in a *.csv* file. All files are in a designated folder.

All parameters can be modified in *parameters.py*.

### CAD Macro: From trajectory to 3D shape

The Macro starts by creating the Z axis and a cylinder. Then, for each .csv file in the designated folder, the following actions occur: 

1. Create a 3D sketch of the trajectory
1. Create a 3D sketch of the groove cross section
1. Perform a swept cut with the two sketches

Most graphical updates and other options are disabled during the generation to accelerate the process.

**Parameters of the cylinder (radius, length) in the macro must agree with the Python script to avoid errors.**

### Why is it no longer used?

1. Large file size: Obtained 3D files are over 500 MB for 5 s of sound. CAM software struggle to work with such large files. For example, Techgraving was not able to create programs from any of the files.
1. Generation time: The 3D file generation is exceptionnaly slow even on powerful computers. It is limited by SolidWorks; volume operations are performed CPU only and is not threadable. 


## Construction of a volumic engraving using Python

### Principle

A Python script reads an audio file. From the amplitude time series of the audio, a 3D trajectory is generated following a helical path. Then, pythonocc-core is used to create a cylinder and engrave the path. Each segment is engraved individually, as I did not figure out how to use the sweep function.

### Why is it no longer used?

1. Same drawbacks as the CAD software option
1. Limited output formats: Only .STEP files can be created.
1. UI: This method does not provide a basic user interface. Therefore, checking the results is annoying and time consuming.


## Construction of a surface depth map

### Principle

The engraving is represented as an image. The image represents the unravelled surface of the cylinder. The intensity of each pixel indicates the depth to engrave; black is the deepest. The image is saved in a lossless format to keep all details.

### Why is it no longer used?

1. Projection warpings: Techgraving encountered some warping while projecting the image to a cylinder. Thus, the sound would be warped, and the edges would not meet perfectly "at the back of the cylinder".