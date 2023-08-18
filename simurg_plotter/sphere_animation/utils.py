from datetime import datetime

import cartopy.crs as ccrs
import h5py
from matplotlib import pyplot as plt
from matplotlib.ticker import FormatStrFormatter

LAYOUT_PROP = {
    "fig_size": (10, 5),
    "projection": ccrs.PlateCarree(),
    "transform": ccrs.PlateCarree(),
    "min_lat": -90,
    "max_lat": 90,
    "min_lon": -180,
    "max_lon": 180
}

WATER_MARK = "Created by SIMuRG"


def plot_sphere(central_longitude, central_latitude, dataframe, ax=None, fig=None, cmap='jet', vmin=None, vmax=None,
                scale=None,
                scale_label=None):
    """
    Plot data on a sphere using an orthographic projection.

    :param central_longitude: The central longitude for the orthographic projection.
    :type central_longitude: float
    :param central_latitude: The central latitude for the orthographic projection.
    :type central_latitude: float
    :param dataframe: A DataFrame containing the data to be plotted.
                      It should have columns 'lon', 'lat', and 'vals'.
    :type dataframe: pandas.DataFrame
    :param ax: The AxesSubplot object to plot on. If not provided,
               a new subplot will be created.
    :type ax: matplotlib.axes._subplots.AxesSubplot, optional
    :param fig: The Figure object that the subplot should belong to. If not provided,
                a new figure will be created.
    :type fig: matplotlib.figure.Figure, optional
    :param cmap: The colormap to use for the scatter plot. Default is 'jet'.
    :type cmap: str, optional
    :param vmin: The minimum value for the color scale. Default is None.
    :type vmin: float, optional
    :param vmax: The maximum value for the color scale. Default is None.
    :type vmax: float, optional
    :param scale: Whether to show color scale (colorbar) alongside the plot. Default is False.
    :type scale: bool, optional
    :param scale_label: Label for the color scale. Default is None.
    :type scale_label: str, optional
    :return: The PathCollection of scatter points on the plot.
    :rtype: matplotlib.collections.PathCollection
    """
    if ax is None or fig is None:
        projection = ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude)
        fig, ax = plt.subplots(subplot_kw={'projection': projection})

    ax.coastlines()
    ax.gridlines()
    ax.set_global()

    scatter = ax.scatter(
        dataframe['lon'],
        dataframe['lat'],
        c=dataframe['vals'],
        cmap=cmap,
        transform=LAYOUT_PROP['transform'],
        marker='o',
        vmin=vmin,
        vmax=vmax
    )

    if scale:
        # Create colorbar if scale is True
        cbar = plt.colorbar(scatter, ax=ax, orientation='vertical', label=scale_label)
        cbar.ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    # Create watermark
    fig.suptitle(WATER_MARK, fontsize=8, x=0.85, alpha=0.3)


    return scatter


def convert_to_custom_format(input_date, output_format="%Y-%m-%dT%H:%M:%SZ (DOY %j)"):
    """
    Convert a given input date and time to a custom format.

    :param input_date: The input date and time in the format 'YYYY-MM-DD HH:MM:SS.ssssss'.
    :type input_date: str
    :param output_format: The desired output format. Default is '%Y-%m-%dT%H:%M:%SZ (DOY %j)'.
    :type output_format: str
    :return: The input date and time in the specified custom format.
    :rtype: str
    """
    parsed_date = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S.%f")
    formatted_date = parsed_date.strftime(output_format)
    return formatted_date


def get_all_data(file_path):
    """
    Retrieve all data from an HDF5 file.

    :param file_path: The path to the HDF5 file.
    :type file_path: str
    :return: A dictionary containing all the data from the HDF5 file.
    :rtype: dict
    """
    data = {}

    def visit_item(name, obj):
        if isinstance(obj, h5py.Group):
            visit_group(obj)
        elif isinstance(obj, h5py.Dataset):
            data[obj.name] = obj[()]

    def visit_group(group):
        group.visititems(visit_item)

    with h5py.File(file_path, 'r') as file:
        file.visititems(visit_item)

    data = {k: v for k, v in data.items() if '/data' in k}
    return data
