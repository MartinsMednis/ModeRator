![Image Alt](http://biosystems.lv/images/software/moderator2/moderator_screenshot.jpg)

# moderator
ModeRator - The Model Comparator is aiming to help modelers to identify common elements in different models that cannot be detected using other modeling tools.

To run the program cd into src/ and run

    ./moderator_gtk.py

## How to install depencencies on Fedora 23
You might need to have RPM Fusion repository enabled.

    dnf install python-Levenshtein python-xlrd libsbml python-libsbml

## How to install depencencies on Ubuntu
### Step 1 - install compiler and compile libSBML with Python bindings.

First, install compiler.

    apt-get install build-essential
    apt-get install python2.7-dev
    apt-get install libxml2-dev
    apt-get install swig

Dowload the source code from http://sourceforge.net/projects/sbml/

    cd into the unzipped directory of libsbml source code.
    cd libSBML-5.9.0-Source/
    ./configure --with-python
    make
    make install

Make libSBML accessible to Python. The actual path may differ.

    export PYTHONPATH=/usr/local/lib64/python2.7/site-packages/

### Step 2 - install pylevenshtein and xlrd libraries

Download pylevenshtein from http://code.google.com/p/pylevenshtein/. Extract it!

Install pylevenshtein:

    cd python-Levenshtein-0.10.1
    python setup.py build
    python setup.py install

Download xlrd from https://pypi.python.org/pypi/xlrd. Extract it!

Install xlrd:

    cd xlrd-0.9.2
    python setup.py build
    python setup.py install

### Step 3 - install pyparsing

    apt-get install python-pyparsing

### Step 4 - run ModeRator

    cd moderator-gtk/src/
    ./moderator_gtk.py
