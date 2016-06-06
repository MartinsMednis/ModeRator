![Image Alt](https://github.com/MartinsMednis/ModeRator/blob/master/screenshot01.jpg)

![Image Alt](https://github.com/MartinsMednis/ModeRator/blob/master/screenshot02.jpg)

# ModeRator
ModeRator - The Model Comparator is aiming to help modelers to identify common metabolites and reactions in different models.


## How to install depencencies on Ubuntu 16.04 and Fedora 23
If you are on Fedora, you might need to have RPM Fusion repository enabled.

Since the previous version the installation is greatly simplified. No need to `sudo`. The following commands will install the required dependencies:

    pip install --user pyparsing
    pip install --user xlrd
    pip install --user python-libsbml

## Run ModeRator

    cd moderator/src
    ./moderator_gtk.py
