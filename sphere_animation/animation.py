import os

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter

from .utils import plot_sphere, get_all_data


def animate_sphere(file_path, central_longitude, central_latitude, file_path_to_save=None):
    data = get_all_data(file_path)
    all_data = [(group, pd.DataFrame(dataset_data)) for group, dataset_data in data.items() if '/data/' in group]

    fig, ax = plt.subplots(subplot_kw={
        'projection': ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude)})
    sc = plot_sphere(central_longitude, central_latitude, all_data[0][1], ax=ax)
    cbar = plt.colorbar(sc, ax=ax, orientation='vertical', label='Values', pad=0.05, aspect=20)

    def animate(i):
        ax.clear()
        group_name = os.path.basename(all_data[i][0])
        plot_sphere(central_longitude, central_latitude, all_data[i][1], ax=ax)
        ax.set_title(f'Group: {group_name}')

    anim = FuncAnimation(fig, animate, frames=len(all_data), interval=30, repeat=False)
    if file_path_to_save is not None and '.gif' in file_path_to_save:
        anim_file = file_path_to_save
        writer = PillowWriter(fps=30)
        anim.save(anim_file, writer=writer)
    plt.show()
