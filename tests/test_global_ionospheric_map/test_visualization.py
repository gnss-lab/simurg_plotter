import os
import pytest
import requests
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from .test_geo_mag_processing import contours
from simurg_plotter.global_ionospheric_map.visualization import plot

MODULE_PATH = os.path.dirname(__file__)

TEST_IMAGE_PATH = os.path.join(MODULE_PATH, "test_images")

BASE_URL = "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz/download?path=%2F&files="
IMAGE_NAMES = [f"GIM_dat_{i}.png" for i in range(12)]
IMAGE_URLS = [BASE_URL + image_name for image_name in IMAGE_NAMES]

@pytest.fixture(scope="function")
def get_maps():
    url = "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz/download?path=%2F&files=maps.npy"
    response = requests.get(url)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        arrays = np.load(temp_file_path, allow_pickle=True)
        return arrays
    else:
        pytest.fail(f"Failed to download file from {url}. Status code: {response.status_code}")

@pytest.fixture(scope="module")
def downloaded_images(request):
    """Скачивание изображений и предоставление их путей."""
    image_paths = []
    os.makedirs(TEST_IMAGE_PATH, exist_ok=True)
    for i, url in enumerate(IMAGE_URLS):
        response = requests.get(url)
        if response.status_code == 200:
            image_path = os.path.join(TEST_IMAGE_PATH, f"downloaded_image_{i}.png")
            with open(image_path, "wb") as f:
                f.write(response.content)
            image_paths.append(image_path)
    yield image_paths

    for image_path in image_paths:
        os.remove(image_path)

    os.rmdir(TEST_IMAGE_PATH)

def get_titles():
    start_time = datetime(2016, 4, 9, 0, 0, 0)
    end_time = datetime(2016, 4, 9, 22, 0, 0)
    interval = timedelta(hours=2)

    timestamps = []

    current_time = start_time
    while current_time <= end_time:
        timestamps.append(f'IRI(2016) {current_time.strftime("%Y-%m-%d %H:%M:%S")}')
        current_time += interval
    return timestamps

def test_plot(request, downloaded_images, contours):
    maps = contours
    titles = get_titles()
    fig_paths = [os.path.join(TEST_IMAGE_PATH, f"test_image_{i}.png") for i in range(len(maps))]

    plot(maps, fig_paths, titles=titles)

    saved_images = [plt.imread(fig_path) for fig_path in fig_paths]

    downloaded_images = [plt.imread(image_path) for image_path in downloaded_images]

    saved_images = sorted(saved_images, key=lambda img: img.shape)
    downloaded_images = sorted(downloaded_images, key=lambda img: img.shape)

    assert len(saved_images) == len(downloaded_images)

    for saved_image, downloaded_image in zip(saved_images, downloaded_images):
        assert np.array_equal(saved_image, downloaded_image)
