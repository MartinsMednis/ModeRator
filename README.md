![Image Alt](https://github.com/MartinsMednis/ModeRator/blob/master/screenshot01.jpg)

![Image Alt](https://github.com/MartinsMednis/ModeRator/blob/master/screenshot02.jpg)

# ModeRator
ModeRator - The Model Comparator is aiming to help modelers to identify common elements in different models that cannot be detected using other modeling tools.

To run the program cd into src/ and run

    ./moderator_gtk.py

## How to install depencencies on Fedora 23
You might need to have RPM Fusion repository enabled.

    dnf install python-Levenshtein python-xlrd libsbml python-libsbml

## How to install depencencies on Ubuntu 16.04
Since the previous version the installation is greatly simplified. No need to `sudo`. The following commands will install the required dependencies:

    pip install --user pyparsing
    pip install --user xlrd
    pip install --user python-libsbml

## Run ModeRator

    cd moderator/src
    ./moderator_gtk.py
