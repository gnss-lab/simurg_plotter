import cartopy.crs as ccrs
import h5py
from matplotlib import pyplot as plt


def plot_sphere(central_longitude, central_latitude, dataframe, ax=None):
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
    :return: The PathCollection of scatter points on the plot.
    :rtype: matplotlib.collections.PathCollection
    """
    if ax is None:
        projection = ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude)
        fig, ax = plt.subplots(subplot_kw={'projection': projection})

    ax.coastlines()
    ax.gridlines()
    ax.set_global()

    scatter = ax.scatter(
        dataframe['lon'],
        dataframe['lat'],
        c=dataframe['vals'],
        cmap='jet',
        transform=ccrs.Geodetic(),
        marker='o',
    )

    return scatter


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
