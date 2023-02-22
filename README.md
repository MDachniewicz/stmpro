# STMpro

## Description

STMpro is an open-source program for scanning tunneling microscopy (STM) data analysis. 
The main objective of this project is to provide compatibility with files from Scienta Omicron (Omicron Nanotechnology) microscopes.

STMpro is still in early development phase, there are many bugs and missing features. Compatibility was tested with files from Matrix v3.1.

## Features

- Opening topography(.Z_mtrx) and single I(V) curves(.I(V)_mtrx) spectroscopy files 
- Opening and saving topography data from .xyz files
- Reading height profiles
- Linewise and plane leveling topography data
- Topography data filters

## Future

It is planned to:
- introduce full support for spectroscopy files (I(V), I(Z))
- add more data processing options
- improve graphical interface
- add options to customise the appearance of graphs and images

STMpro is hobby project, thus regular updates should not be expected.

## Dependencies

- PyQt5
- Numpy
- Matplotlib
- Scipy
- Scikit-image

## Installation
Windows (8, 10, 11) binaries are available [here](https://github.com/MDachniewicz/stmpro/releases)

For 
1. Install Python 3.9
2. Install dependencies <code>pip install -r requirements.txt</code>
3. Run STM.py <code>python -m STM.py

