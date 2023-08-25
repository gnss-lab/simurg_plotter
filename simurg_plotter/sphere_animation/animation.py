import os

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.font_manager import FontProperties

from .utils import plot_sphere, get_all_data, convert_to_custom_format


def animate_sphere(file_path, central_longitude, central_latitude, vmax=None, vmin=None, scale_label=None,
                   file_path_to_save=None):
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
    :param vmin: The minimum value for the color scale. Default is None.
    :type vmin: float, optional
    :param vmax: The maximum value for the color scale. Default is None.
    :type vmax: float, optional
    :param scale_label: Label for the color scale. Default is None.
    :type scale_label: str, optional
    :param file_path_to_save: Optional path to save the animation as a GIF file.
                              If not provided, the animation will be displayed interactively.
    :type file_path_to_save: str, optional
    """
    data = get_all_data(file_path)
    all_data = [(group, pd.DataFrame(dataset_data)) for group, dataset_data in data.items() if '/data/' in group]

    projection = ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude)
    fig, ax = plt.subplots(subplot_kw={'projection': projection})
    scatter = plot_sphere(central_longitude, central_latitude, all_data[0][1], all_data[0][0], ax=ax, fig=fig, vmin=vmin, vmax=vmax,
                          scale_label=scale_label)
    plt.colorbar(scatter, ax=ax, orientation='vertical', label=scale_label, pad=0.05, aspect=20)

    font = FontProperties(family='DejaVu Sans', size=14)

    def animate(i):
        """
        Animate function for updating the plot.

        This function is called for each frame of the animation to update the plot with new data.

        :param i: Frame index.
        :type i: int
        """
        ax.clear()
        group_name = os.path.basename(all_data[i][0])
        plot_sphere(central_longitude, central_latitude, all_data[i][1], all_data[i][0], fig=fig, ax=ax, vmin=vmin,
                    vmax=vmax,
                    scale_label=scale_label)

        ax.set_title(convert_to_custom_format(group_name), fontproperties=font)

    anim = FuncAnimation(fig, animate, frames=len(all_data), interval=30, repeat=False)

    if file_path_to_save is not None and '.gif' in file_path_to_save:
        anim_file = file_path_to_save
        writer = PillowWriter(fps=30)
        anim.save(anim_file, writer=writer)

    plt.show()
