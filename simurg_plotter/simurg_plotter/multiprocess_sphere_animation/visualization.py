import concurrent.futures
import io
import multiprocessing

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

from .data_processing import get_all_data

global_min_value: int
global_max_value: int


def create_image(args):
    group, df, central_longitude, central_latitude, counter, min_value, max_value = args
    process_name = multiprocessing.current_process().name

    fig = plt.figure(figsize=(8, 6), dpi=300)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Orthographic(central_longitude=central_longitude,
                                                               central_latitude=central_latitude))

    ax.coastlines()
    ax.gridlines()
    ax.set_global()

    sc = plot_sphere(central_longitude, central_latitude, df, ax=ax, global_min_value=min_value,
                     global_max_value=max_value)

    buf = io.BytesIO()
    plt.savefig(buf, format='jpeg', bbox_inches='tight', dpi=150)
    plt.close(fig)

    buf.seek(0)
    image_bytes = buf.getvalue()
    print(f"Готово изображение номер {counter} в процессе {process_name}")

    return counter, image_bytes


def plot_sphere(central_longitude, central_latitude, dataframe, ax=None, global_min_value=None, global_max_value=None):
    if ax is None:
        fig, ax = plt.subplots(subplot_kw={
            'projection': ccrs.Orthographic(central_longitude=central_longitude, central_latitude=central_latitude)})

    ax.coastlines()
    ax.gridlines()
    ax.set_global()

    sc = ax.scatter(
        dataframe['lon'],
        dataframe['lat'],
        c=dataframe['vals'],
        cmap='jet',
        transform=ccrs.Geodetic(),
        marker='o',
        vmin=global_min_value,
        vmax=global_max_value,
    )

    cbar = plt.colorbar(sc, ax=ax, orientation='vertical', pad=0.02)

    return sc


def create_animation(images, output_filename, duration=30):
    images.sort(key=lambda x: x[0])  # Сортируем изображения по номеру

    pil_images = [Image.open(io.BytesIO(img)) for _, img in images]

    pil_images[0].save(
        output_filename,
        save_all=True,
        append_images=pil_images[1:],
        duration=duration,
        loop=0
    )


def animate_sphere(file_path, central_longitude, central_latitude, output_filename=None):
    data = get_all_data(file_path)
    all_data = [(group, pd.DataFrame(dataset_data)) for group, dataset_data in data.items() if '/data/' in group]
    # global_max_value, global_min_value = find_min_max(all_data)
    global_max_value, global_min_value = 0.1, -0.1
    if abs(global_max_value) > abs(global_min_value):
        global_min_value = global_max_value * -1
    elif abs(global_max_value) < abs(global_min_value):
        global_max_value = global_min_value * -1

    print(f'max = {global_max_value}, min = {global_min_value}')
    num_images = len(all_data)
    images = []
    batch_size = 4  # Максимальное количество одновременно выполняемых задач

    with concurrent.futures.ProcessPoolExecutor(max_workers=batch_size) as executor:
        args_list = [(group, df, central_longitude, central_latitude, counter, global_min_value, global_max_value)
                     for counter, (group, df) in enumerate(all_data, start=1)]
        for counter, image_bytes in executor.map(create_image, args_list):
            images.append((counter, image_bytes))

    if output_filename is not None:
        create_animation(images, output_filename)