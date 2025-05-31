#! /usr/local/bin/python3.11

"""
[Description]
    This script generates a series of plots of a GMR current sensor performance.
[Input]
    The script uses two CSV files each containing the sensor data in three columns:
    - Current on the magnet (in mA)
    - Voltage on the sensor (in V) taken while increasing the magnetic field
    - Voltage on the sensor (in V) taken while decreasing the magnetic field 
[Usage]
    python3 Plot-4.py <data_no_ofst_dir> <data_ofst_dir> <plot_no_ofst_dir> <plot_ofst_dir>
[Objectives]
    - Plot the relation between the current on the wire and the voltage on the sensor.
    - Perform a linear regression on the data. See how the offset magnetic field affects the linearity.
    - Compare the effect of magnetic hysteresis on the sensor performance.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy import stats
from scipy.constants import mu_0

def plot_current_to_voltage_and_fit(data, plot_dir):
    """
    [Brief]
        Plots the current on the wire and the voltage on the sensor.
        Perform linear regression on the data separately: on increasing and decreasing current.
    [Parameters]
        data:
            numpy arrays containing the sensor data in three columns:
            - Current on the wire (in mA)
            - Voltage on the sensor (in V) taken while increasing the magnetic field
            - Voltage on the sensor (in V) taken while decreasing the magnetic field 
        plot_dir:
            Directory where the plot will be saved.
    [Return value]
        Fit results:
            slope_inc, intercept_inc, r_value_inc
            slope_dec, intercept_dec, r_value_dec

    """
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot the data
    ax.plot(data[:, 0], data[:, 1], 'r+', markersize=10)
    ax.plot(data[:, 0], data[:, 2], 'rx', markersize=10)

    # Perform linear regression on the increasing current data
    slope_inc, intercept_inc, rrr_value_inc, p_value_inc, std_err_inc = stats.linregress(data[:, 0], data[:, 1])
    y_fit_inc = slope_inc * data[:, 0] + intercept_inc
    ax.plot(data[:, 0], y_fit_inc, 'b--', label='Fit Increasing Current')

    # Perform linear regression on the decreasing current data
    slope_dec, intercept_dec, r_value_dec, p_value_dec, std_err_dec = stats.linregress(data[:, 0], data[:, 2])
    y_fit_dec = slope_dec * data[:, 0] + intercept_dec
    ax.plot(data[:, 0], y_fit_dec, 'g--', label='Fit Decreasing Current')

    # Set labels and title
    ax.set_xlabel('Current on Wire (mA)')
    ax.set_ylabel('Voltage on Sensor (V)')
    ax.set_title('Current to Voltage Characteristic of GMR Sensor')
    ax.legend()

    # Save the plot
    plt.savefig(plot_dir)

    # Show the plot
    plt.show()

    # Print the fit results
    print(f"Fit Increasing Current: slope = {slope_inc}, intercept = {intercept_inc}, r_value = {r_value_inc}")
    print(f"Fit Decreasing Current: slope = {slope_dec}, intercept = {intercept_dec}, r_value = {r_value_dec}")
    # Return the fit results
    return slope_inc, intercept_inc, r_value_inc, slope_dec, intercept_dec, r_value_dec

def get_current_voltage(data_dir):
    """
    [Brief]
        Reads the CSV files containing the sensor data and calculates the current on the wire.
    [Parameters]
        data_dir:
            Path to the CSV file containing the sensor data.
    [Output]
        Returns a numpy array containing the current on the wire and voltage on the sensor.
    """
    # Read the CSV file
    data = np.array(pd.read_csv(data_dir).values)
    return data

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 5:
        print("Usage: python3 Plot-4.py <data_no_ofst_dir> <data_ofst_dir> <plot_no_ofst_dir> <plot_ofst_dir>")
        sys.exit(1)

    # Get the input and output file paths from command line arguments
    data_no_ofst_dir = sys.argv[1]
    data_ofst_dir    = sys.argv[2]
    plot_no_ofst_dir = sys.argv[3]
    plot_ofst_dir    = sys.argv[4]

    # Read the data from the CSV files
    data_no_ofst = get_current_voltage(data_no_ofst_dir)
    data_ofst    = get_current_voltage(data_ofst_dir)

    # Plot the current to voltage characteristic and save the plots
    plot_current_to_voltage_and_fit(data_no_ofst, plot_no_ofst_dir)
    plot_current_to_voltage_and_fit(data_ofst, plot_ofst_dir)

