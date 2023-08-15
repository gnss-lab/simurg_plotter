import os

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter

from .utils import plot_sphere, get_all_data


def animate_sphere(file_path, central_longitude, central_latitude, file_path_to_save=None):
    """
    Create an animated sphere plot from HDF5 data.

    This function creates an animated plot of data on a sphere using an orthographic projection.
    The animation cycles through different groups of data in the HDF5 file.

    :param file_path: Path to the HDF5 file containing the data.
    :type file_path: str
    :param central_longitude: The central longitude for the orthographic projection.
    :type central_longitude: float
    :param central_latitude: The central latitude for the orthographic projection.
    :type central_latitude: float
    :param file_path_to_save: Optional path to save the animation as a GIF file.
                              If not provided, the animation will be displayed interactively.
    :type file_path_to_save: str, optional
    """
    data = get_all_data(file_path)
    all_data = [(group, pd.DataFrame(dataset_data)) for group, dataset_data in data.items() if '/data/' in group]

    projection = ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude)
    fig, ax = plt.subplots(subplot_kw={'projection': projection})
    scatter = plot_sphere(central_longitude, central_latitude, all_data[0][1], ax=ax)
    plt.colorbar(scatter, ax=ax, orientation='vertical', label='Values', pad=0.05, aspect=20)

    def animate(i):
        """
        Animate function for updating the plot.

        This function is called for each frame of the animation to update the plot with new data.

        :param i: Frame index.
        :type i: int
        """
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
