from simurg_plotter.global_ionospheric_map.visualization import plot

import pytest
import os
import numpy as np
from PIL import Image
import zipfile
import requests

TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp")
URL = "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz"

@pytest.fixture(scope="module")
def data_from_archive():
    # os.makedirs(TEMP_DIR, exist_ok=False)

    archive_path = os.path.join(os.path.dirname(__file__), TEMP_DIR, "test_gim_plot.zip")
    destination_folder = os.path.join(os.path.dirname(__file__), TEMP_DIR)
    # print(archive_path)

    # try:
    #     # Загружаем файл по URL
    #     response = requests.get(URL)
    #     with open(archive_path, "wb") as f:
    #         f.write(response.content)
        
    #     # Распаковываем zip-файл
    #     with zipfile.ZipFile(archive_path, "r") as zip_ref:
    #         zip_ref.extractall(destination_folder)
        
    #     print("Zip-файл успешно загружен и распакован.")
    # except Exception as e:
    #     print(f"Произошла ошибка при загрузке и распаковке zip-файла: {e}")
    maps_path = os.path.join(TEMP_DIR, "maps.npy")
    gims_path = os.path.join(TEMP_DIR, "gims.npy")
    image_paths = [os.path.join(TEMP_DIR, filename) for filename in os.listdir(TEMP_DIR) if filename.endswith(".png")]

    yield maps_path, gims_path, image_paths

    # os.remove(gims_path)
    # for image_path in image_paths:
    #     os.remove(image_path)
    # os.rmdir(TEMP_DIR)

def test_gim_plot(data_from_archive):
    maps_path, gims_path, image_paths = data_from_archive

    #maps = np.loadtxt(maps_path)

    script_dir = os.path.dirname(os.path.realpath(__file__))
    save_dir = os.path.join(script_dir, 'tests/temp')

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    #names = [os.path.join(save_dir, f'GIM_dat_{i}.png') for i in range(len(maps))]

    #names = [f'/tmp/GIM_dat_{i}.png' for i in range(len(maps))]
    #titles = [f'IRI(2016) {m.time}' for m in maps]
    gims = np.loadtxt(gims_path)
    #plot(gims, fig_path=names, titles = titles)
    for i, image_path in enumerate(image_paths):
        archive_image = Image.open(image_path)
       # created_image = Image.open(names[i])

        # Сравниваем изображения
        #assert np.array_equal(np.array(archive_image), np.array(created_image))
    

        



