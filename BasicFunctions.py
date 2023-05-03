## Plots the THz spectra with the fourier transform
## Requires numpy and pandas 

import os
import argparse

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.fft import rfft, rfftfreq
from scipy.optimize import curve_fit


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

def back_sub(data, deg=0):                      # Gets raw data array, fits a polynomial and returns array without x, y without background, and background
    fit = np.polyfit(data[0], data[1], deg)
    back = np.polyval(fit, data[0])

    return np.array([data[0], data[1] - back, back])

def average_files(data_list):               
    # Gets list of data arrays, and returns and array with 
    # times, average values
    
    sum_array = np.zeros(len(data_list[0][1]))
    for d in data_list:
        sum_array = sum_array + d[1]

    return np.array([data_list[0][0], sum_array / len(data_list)])

def avg_err_files(data_list):                  
    # Gets list of data arrays, and returns and array with 
    # times, average values, std_error

    N = len(data_list)
    average = average_files(data_list)

    sum_array = np.zeros(len(data_list[0][1]))
    for d in data_list:
        sum_array = sum_array + (average[1] - d[1])**2 

    return np.array([data_list[0][0], average[1], np.sqrt( sum_array/(N*(N-1)) )  ])




def import_files(prefix, time, n_averages=1, poly_order=0):
    raw_list = []
    i = 0
    while len(raw_list) < n_averages:                                   # Iterates until all files have been found
        
        file = prefix + str(int(time)+i) + '.d22'
        if os.path.exists(file):                                        # Returns true if the file exists, and appends file to list
            raw_list.append(  np.genfromtxt(file).transpose()   )
        
        i += 1
    
    no_back_list = [  back_sub(raw_data, deg=poly_order)  for raw_data in raw_list   ]      # Subtracts background
    no_back_fft_list = [ do_fft(data) for data in no_back_list   ]                          # Does FFT for all files

    return avg_err_files(no_back_list), avg_err_files(no_back_fft_list)         # Calculates the average and standard error, and returns the values


def import_average_file(file, return_props=False):
    data = np.genfromtxt(file, skip_header=1).transpose()


    data[0] = np.abs(data[0])

    fft = do_fft(data)

    if return_props:
        properties = {}
        with open(file) as open_file:
            first_line = open_file.readline()
        
        properties['Unit'] = first_line.split('Lock-In 1: ')[1].split('/')[0]      # Returns a string with unit, ie, '10 mV'
        properties['Start Position'] = first_line.split('THz Start: ')[1].split(', ')[0]
        properties['# of data points'] = first_line.split('mm, ')[1].split(', ')[0]
        properties['Time resolution'] = first_line.split('points, ')[1].split(' - ')[0]

        return data, fft, properties

    else:
        return data, fft






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
        peak_ind = np.argmax(  np.abs(data[1]))
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



if __name__ == '__main__':
    # Importing arguments to file
    parser = argparse.ArgumentParser(description='''This scripts plots the time dependence of the electric field and its Fourier transform.
    It can calculate the average of several files, and also subtract a polynomial background to the time-dependent data.''')

    parser.add_argument('-f','--files', help='Data file to be plotted. If this is a list, the plot will be the averaged.', nargs='*')
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



    datas = [[]] * len(files)
    ffts = [[]] * len(files)

    for i, f in enumerate(files):
        
        if 'Average' in f:
            raw_data = np.genfromtxt(f, skip_header=1).transpose()
            
            with open(f) as open_file:
                first_line = open_file.readline()
            unit_scale, unit = first_line.split('Lock-In 1: ')[1].split('/')[0].split(' ')      # Returns a list with the unit value and unit string

            raw_data[1] = raw_data[1] * int(unit_scale)
            
            raw_data[0] = np.abs(raw_data[0])

        else:
            raw_data = np.genfromtxt(file).transpose()

            unit = None

            raw_data[0] = np.abs(raw_data[0])

        if not bg_order < 0:
            datas[i] = back_sub(raw_data, deg=bg_order)
        else:
            datas[i] = raw_data
        
        ffts[i] = do_fft(datas[i])

    if len(files) > 1:
        final_data  = avg_err_files(datas)
        final_fft   = avg_err_files(ffts)
    else:
        final_data  = datas[0]
        final_fft   = ffts[0]

    axs = plot_spectrum(final_data, final_fft, color=plot_color, label=label_text, normalize=normalize)

    if unit:
        axs[0].text(0.6, 0.8, f'Voltage in {unit}', transform=axs[0].transAxes)

    if label_text:
        plt.legend()

    plt.show()



