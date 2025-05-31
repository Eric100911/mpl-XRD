#! /usr/local/bin/python3.11

"""
[Description]
    This script generates a angle-voltage plot of a GMR angle displacement sensor.
[Input]
    The script uses a CSV file containing the sensor data in two columns:
    - Angle (in degrees)
    - Voltage on the sensor (in mV) taken while increasing the angle
[Usage]
    python3 Plot-5.py <data_dir> <plot_dir>
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

def plot_angle_to_voltage(data, plot_dir):
    """
    [Brief]
        Plots the angle and the voltage on the sensor.
    [Parameters]
        data:
            numpy arrays containing the sensor data in two columns:
            - Angle (in degrees)
            - Voltage on the sensor (in mV) taken while increasing the angle
        plot_dir:
            Directory where the plot will be saved.
    """
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot the data
    ax.plot(data[:, 0], data[:, 1], 'r+', markersize=10)

    # 使用三次多项式插值
    from scipy.interpolate import make_interp_spline
    x_smooth = np.linspace(data[:, 0].min(), data[:, 0].max(), 300)
    # 确保数据点按x值排序
    sorted_idx = np.argsort(data[:, 0])
    x_sorted = data[sorted_idx, 0]
    y_sorted = data[sorted_idx, 1]
    # 创建三次样条插值器（k=3表示三次多项式）
    spl = make_interp_spline(x_sorted, y_sorted, k=3)
    y_smooth = spl(x_smooth)
    ax.plot(x_smooth, y_smooth, 'k-')  # 黑色实线

    # 创建组合图例
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([], [],
            color='k',             # 曲线颜色
            linestyle='-',         # 实线
            marker='+',            # 数据点标记
            markersize=5,          # 保持与绘图一致
            markerfacecolor='r',   # 红色填充
            markeredgecolor='r',   # 红色边缘
            label='Data with Cubic Fit')  # 新标签
    ]

    # Set labels and title
    ax.set_xlabel('Angle (degrees)')
    ax.set_ylabel('Voltage (mV)')
    ax.set_title('Angle to Voltage Plot')
    ax.legend(handles=legend_elements)

    plt.show()
    plt.savefig(plot_dir)
    plt.close(fig)

def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python3 Plot-5.py <data_dir> <plot_dir>")
        sys.exit(1)

    # Read the data from the CSV file
    data_dir = sys.argv[1]
    plot_dir = sys.argv[2]
    data = pd.read_csv(data_dir).to_numpy()

    print(data)

    # Call the function to plot angle to voltage
    plot_angle_to_voltage(data, plot_dir)

if __name__ == "__main__":
    main()