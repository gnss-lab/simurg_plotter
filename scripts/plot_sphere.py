import pandas as pd
from matplotlib import pyplot as plt

from simurg_plotter.sphere_animation.animation import plot_sphere
from simurg_plotter.sphere_animation.utils import get_all_data

if __name__ == '__main__':
    file_path = r"C:\Users\kuzne\OneDrive\Документы\work\files_for_simurg_plotter\roti_2015_254_-90_90_N_-180_180_E_3a01.h5"
    central_longitude = 104.280606  # Долгота
    central_latitude = 52.289588  # Широта

    # ROTI:          0   - 0.5
    # Variations:   -0.2 - 0.2
    # TecTrusted:    0   - 100
    vmax = 0.5
    vmin = 0

    data = get_all_data(file_path)
    all_data = [(group, pd.DataFrame(dataset_data)) for group, dataset_data in data.items() if '/data/' in group]
    scater = plot_sphere(central_longitude, central_latitude, all_data[45][1], vmax=vmax, vmin=vmin, scale=True,
                         scale_label="TECu/min")

    plt.show()
