import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as ticker

import numpy as np

def convert_to_dst_plot_data(data):
    times = list(data.keys())
    dst_values = list(data.values())
    time_numeric = matplotlib.dates.date2num(times)
    dst_plot_data = np.column_stack((time_numeric, dst_values))
    
    return dst_plot_data


def plot_dst(ax, dst_data, **kwargs):
        ax.plot(dst_data[:, 0], dst_data[:, 1])
        # ax.xticks(rotation=45)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(base=6))
        ax.set_xlabel('Date')
        # ax.set_ylabel('Dst Index')

        if 'time' in kwargs:
                time = kwargs['time']
                ax.axvline(x=time, color='r', linestyle='--')

