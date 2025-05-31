#! /usr/local/bin/python3.11

"""
[Description]
    This script generates a plot of the magneto-electric conversion characteristic of a GMR analog sensor.
[Input]
    The script uses two CSV files each containing the sensor data in two columns:
    - Current on the magnet (in mA), voltage on the sensor (in mV).
    The scripts also receives the turns in unit length of the solenoid as a parameter (in SI units, i.e. m^-1).
    - This allows to calculate the magnetic field in Gauss. 
    - The permeability mu_0 will be adopted from imported library.
[Usage]
    python3 Plot-2.py <data_incr_dir> <data_desc_dir> <turns_in_m> <plot_dir>
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.constants import mu_0
from scipy.interpolate import interp1d, make_interp_spline
from scipy.signal import savgol_filter

def plot_sensor_characteristic(data_incr, data_desc, plot_dir):
    """
    [Brief]
    Plots the magneto-electric conversion characteristic of a GMR analog sensor.
    [Parameters]
        data_incr, data_desc:
            numpy arrays containing the sensor data in two columns:
            - Magnetic field in Gauss
            - Voltage on the sensor in mV
        plot_dir:
            Directory where the plot will be saved.
    [Configuration]
        Shows the original data points.
        Curves are in black; datapoints are in red and diffrent shapes.
    [Output]
        The plot is displayed on the screen and saved as a PNG file specified by plot_dir.
    """
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot the data
    ax.plot(data_incr[:, 0], data_incr[:, 1], 'r+', markersize=10)
    ax.plot(data_desc[:, 0], data_desc[:, 1], 'rx', markersize=10)

    # Interpolate to get a smooth curve
    x_incr = np.linspace(data_incr[:, 0].min(), data_incr[:, 0].max(), 1000)
    x_desc = np.linspace(data_desc[:, 0].min(), data_desc[:, 0].max(), 1000)
    y_incr = make_interp_spline(data_incr[:, 0], data_incr[:, 1], k=3)(x_incr)
    y_desc = make_interp_spline(data_desc[:, 0], data_desc[:, 1], k=3)(x_desc)

    # 修改这里：移除曲线部分的label参数
    ax.plot(x_incr, y_incr, 'k-')
    ax.plot(x_desc, y_desc, 'k-')

    # 创建自定义图例
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([], [], 
            color='k', 
            linestyle='-',
            marker='+',
            markersize=5,
            markerfacecolor='r',
            markeredgecolor='r',
            label='Increasing Field'),
        Line2D([], [], 
            color='k', 
            linestyle='-',
            marker='x',
            markersize=5,
            markerfacecolor='r',
            markeredgecolor='r',
            label='Decreasing Field')
    ]

    # Set labels and title
    ax.set_xlabel('Magnetic Field (Gs)')
    ax.set_ylabel('Voltage (V)')
    ax.set_title('Magneto-Electric Conversion Characteristic of GMR Analog Sensor')
    ax.legend(handles=legend_elements)  # 使用自定义图例
    
    # Save the plot
    plt.savefig(plot_dir)
    
    # Show the plot
    plt.show()

def get_mag_voltage(data_incr_dir, data_desc_dir, turns_in_m):
    """
    [Brief]
    Reads the CSV files containing the sensor data and calculates the magnetic field in Gauss.
    [Parameters]
        data_incr_dir, data_desc_dir:
            Paths to the CSV files containing the sensor data.
        turns_in_m:
            Turns in unit length of the solenoid (in SI units, i.e. m^-1).
    [Output]
        Returns two numpy arrays containing the magnetic field in Gauss and voltage on the sensor in mV.
    """
    # Read the CSV files
    data_incr = np.array(pd.read_csv(data_incr_dir).values.astype(float))
    data_desc = np.array(pd.read_csv(data_desc_dir).values.astype(float))
    # Calculate the magnetic field in Gauss
    data_incr[:, 0] = (data_incr[:, 0] * mu_0 * turns_in_m) / 1e-4
    data_desc[:, 0] = (data_desc[:, 0] * mu_0 * turns_in_m) / 1e-4
    # Sort by magnetic field
    data_incr = data_incr[data_incr[:, 0].argsort()]
    data_desc = data_desc[data_desc[:, 0].argsort()]

    return data_incr, data_desc

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 5:
        print("Usage: python3 Plot-2.py <data_incr_dir> <data_desc_dir> <turns_in_m> <plot_dir>")
        sys.exit(1)

    # Get the command line arguments
    data_incr_dir = sys.argv[1]
    data_desc_dir = sys.argv[2]
    turns_in_m = float(sys.argv[3])
    plot_dir = sys.argv[4]

    # Get the magnetic field and voltage data
    data_incr, data_desc = get_mag_voltage(data_incr_dir, data_desc_dir, turns_in_m)

    # Plot the sensor characteristic
    plot_sensor_characteristic(data_incr, data_desc, plot_dir)
    # End of script