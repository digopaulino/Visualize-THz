import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget
from BasicFunctions import *



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    # Starts GUI
    def initUI(self):
        self.setWindowTitle("THz Plotter")
        self.setGeometry(100, 100, 1000, 600)

        # Sets layout structure to be inherent from all objects in window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Creates empty figure space
        self.fig, self.axs = plt.subplots(ncols=2, figsize=(8,3))
        self.canvas = FigureCanvas(self.fig)

        # Creates button
        self.button = QPushButton("Open")
        self.button.setGeometry(10, 10, 100, 30)
        self.button.clicked.connect(self.open_file)

        # Adds objects to layout
        layout.addWidget(self.button)
        layout.addWidget(self.canvas, 1)

        # Adds navigation toolbar (zoom, home, change axes, etc)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

        # Updates the window
        self.show()


    # Function to import data. To do: move to BasicFunctions.py
    def import_data(self, data_file):
        data = np.genfromtxt(data_file, skip_header=1).transpose()
        self.scan_properties = {}
        
        if 'Average' in data_file:
            with open(data_file) as open_file:
                first_line = open_file.readline()
            
            self.scan_properties['Unit'] = first_line.split('Lock-In 1: ')[1].split('/')[0]      # Returns a string with unit, ie, '10 mV'
            self.scan_properties['Start Position'] = first_line.split('THz Start: ')[1].split(', ')[0]
            self.scan_properties['# of data points'] = first_line.split('mm, ')[1].split(', ')[0]
            self.scan_properties['Time resolution'] = first_line.split('points, ')[1].split(' - ')[0]

        data[0] = np.abs(data[0])
        fft = do_fft(data)
            
        return data, fft

    # Function to select and load the data file
    def open_file(self):
        # Selecting file
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(self, "Select data files", "", "Data files (*.*)")

        # Setting plot colors
        colors = ['r', 'b', 'lime', 'c', 'g', 'm', 'y', 'k']
        color_id = 0  # Counter for indexing the colors list
        
        if file_paths:
            for file_path in file_paths:
                data, fft = self.import_data(str(file_path))    # Imports data
                
                # Plots data
                self.axs = plot_spectrum(data, fft, axs=self.axs, color=colors[color_id], label=file_path.split('/')[-1])
                color_id = (color_id + 1) % len(colors)

                self.axs[1].legend()
            
            # Updates the plot
            self.canvas.draw()


# Runs
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
