# Engraver
Scripts to generate engraving files from audio


## Making it work:
1. Install conda (I used Miniforge from here: https://docs.conda.io/projects/conda/en/stable/).
1. Follow instruction on https://github.com/tpaviot/pythonocc-core?tab=readme-ov-file to install the library.
1. Install all other packages listed in requirements.txt

## Usage
1. Add your *.mp3* audio file in the *audio_files* folder
1. In *parameters.py*, edit *input_filename* with the name of your file. Modify any other relevant parameter.
1. Run *main.py* and check that it created a *.csv* file.
1. Open SolidWorks and create a new part
1. Run the macro *generator1.swp* (Outils/Macros/Executer)
1. When asked, select the *.csv* file that you just created.