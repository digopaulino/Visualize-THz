import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget
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
                data, fft, props = import_data(str(file_path))    # Imports data
                
                # Plots data
                self.axs = plot_spectrum(data, fft, axs=self.axs, color=colors[color_id], label=file_path.split('/')[-1])
                color_id = (color_id + 1) % len(colors)

                self.axs[1].legend()
            
            # Updates the plot
            self.canvas.draw()


# Runs code
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
