# visualize-thz
Repository with useful software for visualization THz spectroscopy data taken in the Ultrafast Dynamics Laboratory in McGill University.

## Directories
- bin/ contains the python code (described below) that can be run directly. 
- dist/ contains executable files (generated with Pyinstaller) that can be run without a command line.

## Files

- BasicFunction.py contains the basic python functions used in the programs

- PlotTHz.py makes a GUI that allows selecting the data file, and plotting both time and frequency domain plots of the selected file



## Required Python packages:
- numpy (1.24.3)
- pandas (2.0.1)
- matplotlib (3.7.1)
- scipy (1.10.1)
- PyQt6 (6.5.0)
