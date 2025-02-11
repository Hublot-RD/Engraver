# Engraver

Scripts to generate engraving files from audio.

## Making it work

1. Install conda (for example from [Miniforge](https://docs.conda.io/projects/conda/en/stable/)).
1. Follow instructions [here](https://github.com/tpaviot/pythonocc-core?tab=readme-ov-file) to install the library.
1. Install all other packages listed in requirements.txt

## Usage

1. Add your *.mp3* audio file in the *audio_files* folder
1. In *parameters.py*, edit *input_filename* with the name of your file. Modify any other relevant parameter.
1. Run *main.py* and check that it created a folder *input_filename_files* containing *.csv* files.
1. Open SolidWorks and create a new part
1. Run the macro *full_pipeline.swp* (Outils/Macros/Executer)
1. When asked, select the folder *input_filename_files* that you just created.
1. Wait for the macro to finish. It may take a while.

## Architecture

The engraving automation is split in two part: Python and SolidWorks Macro.

### Python: From audio to trajectory

A Python script (*main.py*) reads an audio file. From the amplitude time serie of the audio, a 3D trajectory is generated following a helical path. This trajectory is cut into several pieces, each spanning half a turn, saved individually in a *.csv* file. All files are in a designated folder.

All parameters can be modified in *parameters.py*.

### Solidworks Macro: From trajectory to 3D shape

The Macro starts by creating the Z axis and a cylinder. Then, for each *.csv* file in the designated folder, the actions are:

1. Create a 3D sketch of the trajectory
1. Create a 3D sketch of the groove cross section
1. Perform a swept cut with the two sketches

Most graphical updates and other options are disabled during the generation to accelerate the process.

**Parameters of the cylinder (radius, length) must agree with the Python script to avoid errors.**
