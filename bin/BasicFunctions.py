## Plots the THz spectra with the fourier transform
## Requires numpy and pandas 

import os
import argparse

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq


# Plot parameters
params = {'font.family'         : 'DejaVu Sans',  
            'font.size'           : 18,        
            #   'text.usetex'         : True,

          'axes.linewidth'      : 2,

          'lines.linewidth'     : 2,              
            'lines.markersize'    : 6,

          'xtick.direction'     : 'in',   
            'xtick.minor.visible' : True,
            'xtick.major.width'   : 2,
            'xtick.minor.width'   : 1.5,
            'xtick.major.size'    : 5,
            'xtick.minor.size'    : 3,
            'xtick.top'           : True,

          'ytick.direction'     : 'in',   
            'ytick.minor.visible' : True,
            'ytick.major.width'   : 2,
            'ytick.minor.width'   : 1.5,
            'ytick.major.size'    : 5,
            'ytick.minor.size'    : 3,
            'ytick.right'         : True,

          'legend.frameon'      : False,          
            'legend.fontsize'     : 'small',
            
          'figure.dpi'          : 60,            
            'figure.figsize'      : (8,6),     
            'figure.autolayout'   : True,
            'figure.facecolor'    : 'white',
          
          'animation.html'      : 'jshtml'
          }
plt.rcParams.update(params) 

def do_fft(data):       # Gets time (ps) and E_field from the "data" array, and return Freq (THz) and FFT_Amplitude
    t = data[0]
    E = data[1]
    
    N = len(E)
    dt = abs(t[1] - t[0])

    fft_amp = rfft(E)[:N//2]
    fft_freq = rfftfreq(N, dt)[:N//2]

    return np.array([fft_freq, np.abs(fft_amp)])


# Function to import data. To do: move to BasicFunctions.py
def import_data(data_file):
    data = np.genfromtxt(data_file, skip_header=1).transpose()
    scan_properties = {}
    
    if 'Average' in data_file:
        with open(data_file) as open_file:
            first_line = open_file.readline()
        
        scan_properties['Unit'] = first_line.split('Lock-In 1: ')[1].split('/')[0]      # Returns a string with unit, ie, '10 mV'
        scan_properties['Start Position'] = first_line.split('THz Start: ')[1].split(', ')[0]
        scan_properties['# of data points'] = first_line.split('mm, ')[1].split(', ')[0]
        scan_properties['Time resolution'] = first_line.split('points, ')[1].split(' - ')[0]

    data[0] = np.abs(data[0])
    fft = do_fft(data)
        
    return data, fft, scan_properties




# Function to plot E vs t, and its Fourier transform
def plot_spectrum(data, fft, axs=None, color='black', label=None, normalize=False, linestyle='-', marker='', alpha=1, dpi=80, dislocate0=True):

    if axs is None:
        plt.close('all')
        fig, axs = plt.subplots(ncols=2, figsize=(16,6), dpi=dpi)


    if normalize:
        norm_t = data[1].max()
        norm_fft = fft[1].max()
        axs[0].set_ylabel('Normalized Electric Field (a.u.)')
        axs[1].set_ylabel('Normalized FFT Amplitude (a.u.)')
    else:
        norm_t, norm_fft = 1,1
        axs[0].set_ylabel('Electric Field (a.u.)')
        axs[1].set_ylabel('FFT Amplitude (a.u.)')
    
    if dislocate0:
        peak_ind = np.argmax( np.abs(data[1]))
        peak_time = data[0][peak_ind]
    else:
        peak_time = 0
        

    axs[0].plot(data[0] - peak_time, data[1]/norm_t, color=color, linestyle=linestyle, marker=marker, alpha=alpha, label=label)
    axs[0].axhline(0, linestyle='dashed', color='grey', linewidth=1)

    axs[0].set_xlabel('Time (ps)')

    axs[1].plot(fft[0], fft[1]/norm_fft, color=color, label=label, linestyle=linestyle, marker=marker, alpha=alpha)
    axs[1].set_xlabel('Frequency (THz)')
    axs[1].set_yscale('log')
    axs[1].set_ylim(bottom=(fft[1]/norm_fft).max()/1e4)
    axs[1].set_xlim(left=0)

    axs[1].grid()

    return axs



def plot_polarization_projection(v_data, h_data, t_min, t_max, dpi=80, colors=['red', 'blue'], plot_intensity=True):
    colors = colors
    labels = ['Vertical', 'Horizontal']

    norm = v_data[1].max()

    ts_long = v_data[0] - v_data[0][ np.argmax(v_data[1])  ]
    E_v_long = v_data[1] / norm
    E_h_long = h_data[1] / norm

    ind_min = np.argmin(np.abs(ts_long - t_min))
    ind_max = np.argmin(np.abs(ts_long - t_max))

    ts = ts_long[ind_min:ind_max]
    E_v = E_v_long[ind_min:ind_max]
    E_h = E_h_long[ind_min:ind_max]
    
    plt.close('all')
    fig, axs = plt.subplots(ncols=2, figsize=(16,6), dpi=dpi)
    
    axs[0].plot(ts, E_v, color=colors[0], label=labels[0])
    axs[0].plot(ts, E_h, color=colors[1], label=labels[1])
    
    if plot_intensity:
        axs[0].plot(ts, np.sqrt(E_v**2 + E_h**2), color='black', label=r'($E_x^2$ + $E_h^2$)$^{1/2}$')

    axs[1].plot(E_v, E_h, color='lime')

    axs[0].axhline(0, color='black', linestyle='dashed', linewidth=1)
    axs[0].set_xlabel('Time (ps)')
    axs[0].set_ylabel('Electric Field (a.u.)')
    axs[0].legend()

    axs[1].set_xlabel(r'$E_x$')
    axs[1].set_ylabel(r'$E_y$')

    axs[1].set_xlim(-1.25, 1.25)
    axs[1].set_ylim(-1.25, 1.25)

    axs[1].grid(color='black', linewidth=1, linestyle='dashed', alpha=0.5)


    return axs



if __name__ == '__main__':
    # Importing arguments to file
    parser = argparse.ArgumentParser(description='''This scripts plots the time dependence of the electric field and its Fourier transform.''')

    parser.add_argument('-f','--files', help='Data file to be plotted. If this is a list, only the first will be plotted. Use PlotTHz.py for more than one.', nargs='*')
    parser.add_argument('-b','--bg_sub', help='Insert the order of the polynomial to subtract the background. If negative, no background will be subtracted', default=-1, type=int)
    parser.add_argument('-n','--normalize', help='If called, plots will be normalized.', action="store_true")
    parser.add_argument('-c','--color', help='Insert the color for matplotlib', default='black')
    parser.add_argument('-l','--label', help='Insert the label of the data', default=None)

    args = parser.parse_args()

    files       = args.files                      # List of filed
    bg_order    = args.bg_sub                  # Background poly to subtract
    normalize   = args.normalize         # Boolean value if the time axis is inverted
    plot_color  = args.color
    label_text  = args.label

    if len(files) > 1:
        print('Plotting only first file. Use PlotTHz.py if more than one file.')

    data, fft, _ = import_data(files[0])


    axs = plot_spectrum(data, fft, color=plot_color, label=label_text, normalize=normalize)

    if label_text:
        plt.legend()

    plt.show()



