#! /usr/local/bin/python3.11
"""
[Description]
    This script generates a plot of a GMR material's resistance as a function of the magnetic field.
[Input]
    The script uses two CSV files each containing the sensor data in two columns:
    - Current on the magnet (in mA), current on the sensor (in mA).
    The scripts also receives the turns in unit length of the solenoid as a parameter (in SI units, i.e. m^-1).
    - also the voltage from (in V) the input source.
[Usage]
    python3 Plot-2.py <data_incr_dir> <data_desc_dir> <turns_in_m> <voltage_in_V> <plot_dir> 
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.constants import mu_0

def plot_resistance_to_B(data_incr, data_desc, plot_dir):
    """
    [Brief]
    Plots the resistance of a GMR material as a function of the magnetic field.
    [Parameters]
        data_incr, data_desc:
            numpy arrays containing the sensor data in two columns:
            - Magnetic field in Gauss
            - Resistance in Ohm
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
    ax.plot(data_incr[:, 0], data_incr[:, 1], 'k-', label='Increasing Field')
    ax.plot(data_desc[:, 0], data_desc[:, 1], 'k-', label='Decreasing Field')
    ax.plot(data_incr[:, 0], data_incr[:, 1], 'r+', markersize=3)
    ax.plot(data_desc[:, 0], data_desc[:, 1], 'rx', markersize=3)

    # Set labels and title
    ax.set_xlabel('Magnetic Field (Gs)')
    ax.set_ylabel('Resistance (Ohm)')
    ax.set_title('Resistance of GMR Material as a Function of Magnetic Field')
    ax.legend()
    
    # Save the plot
    plt.savefig(plot_dir)
    
    # Show the plot
    plt.show()

def get_resistance(data_incr_dir, data_desc_dir, turns_in_m, voltage_in_V):
    """
    [Brief]
    Reads the data from the CSV files and calculates the resistance of the GMR material.
    [Parameters]
        data_incr_dir, data_desc_dir:
            Paths to the CSV files containing the sensor data.
        turns_in_m:
            Turns in unit length of the solenoid (in SI units, i.e. m^-1).
        voltage_in_V:
            Voltage from the input source (in V).
    [Output]
        Returns two numpy arrays containing the magnetic field and resistance data.
    """
    # Read the data from the CSV files
    data_incr = np.array(pd.read_csv(data_incr_dir).values.astype(float))
    data_desc = np.array(pd.read_csv(data_desc_dir).values.astype(float))

    # Calculate the magnetic field in Gauss
    B_incr = (data_incr[:, 0] / (turns_in_m * mu_0)) * 1e4
    B_desc = (data_desc[:, 0] / (turns_in_m * mu_0)) * 1e4

    # Calculate the resistance
    R_incr = voltage_in_V / (data_incr[:, 1] * 1e-3)
    R_desc = voltage_in_V / (data_desc[:, 1] * 1e-3)

    # Combine the magnetic field and resistance data
    resistance_data_incr = np.column_stack((B_incr, R_incr))
    resistance_data_desc = np.column_stack((B_desc, R_desc))

    return resistance_data_incr, resistance_data_desc

if __name__ == "__main__":
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 6:
        print("Usage: python3 Plot-2.py <data_incr_dir> <data_desc_dir> <turns_in_m> <voltage_in_V> <plot_dir>")
        sys.exit(1)

    # Get the command line arguments
    data_incr_dir = sys.argv[1]
    data_desc_dir = sys.argv[2]
    turns_in_m = float(sys.argv[3])
    voltage_in_V = float(sys.argv[4])
    plot_dir = sys.argv[5]

    # Get the resistance data
    resistance_data_incr, resistance_data_desc = get_resistance(data_incr_dir, data_desc_dir, turns_in_m, voltage_in_V)

    # Plot the resistance to magnetic field
    plot_resistance_to_B(resistance_data_incr, resistance_data_desc, plot_dir)