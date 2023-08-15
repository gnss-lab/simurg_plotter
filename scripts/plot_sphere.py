import pandas as pd
from matplotlib import pyplot as plt

from sphere_animation.animation import plot_sphere
from sphere_animation.utils import get_all_data

if __name__ == '__main__':
    file_path = 'files/...'
    central_longitude = 104.280606  # Долгота
    central_latitude = 52.289588  # Широта

    data = get_all_data(file_path)
    all_data = [(group, pd.DataFrame(dataset_data)) for group, dataset_data in data.items() if '/data/' in group]
    plot_sphere(central_longitude, central_latitude, all_data[0][1])
    plt.show()
