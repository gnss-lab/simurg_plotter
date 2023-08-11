import cartopy.crs as ccrs
import h5py
import matplotlib.pyplot as plt
import pandas as pd

def plot_sphere(central_longitude, central_latitude, dataframe, ax=None):
    if ax is None:
        fig, ax = plt.subplots(subplot_kw={
            'projection': ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude)})

    ax.coastlines()
    ax.gridlines()
    ax.set_global()

    return ax.scatter(
        dataframe['lon'],
        dataframe['lat'],
        c=dataframe['vals'],
        cmap='jet',
        transform=ccrs.Geodetic(),
        marker='o',
    )

def get_all_data(file_path):
    data = {}

    def visit_item(name, obj):
        if isinstance(obj, h5py.Group) and name == '/data':
            visit_group(name, obj)
        elif isinstance(obj, h5py.Dataset):
            data[obj.name] = obj[()]

    def visit_group(name, group):
        group.visititems(visit_item)

    with h5py.File(file_path, 'r') as file:
        file.visititems(visit_item)

    return data
