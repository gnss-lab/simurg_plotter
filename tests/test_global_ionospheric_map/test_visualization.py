import os
import pytest
import requests
import tempfile
import numpy as np
import pickle
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from simurg_plotter.global_ionospheric_map.visualization import plot

MODULE_PATH = os.path.dirname(__file__)
TEST_IMAGE_PATH = os.path.join(MODULE_PATH, "test_images")
BASE_URL = "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz/download?path=%2F&files="
IMAGE_NAMES = [f"GIM_dat_{i}.png" for i in range(12)]
IMAGE_NAMES2 = [f"GIM{i}.png" for i in range(12)]
IMAGE_URLS = [BASE_URL + image_name for image_name in IMAGE_NAMES]
IMAGE_URLS2 = [BASE_URL + image_name for image_name in IMAGE_NAMES2]


@pytest.fixture(scope="function")
def get_maps(request):
    return download_and_load_pickle(
        "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz/download?path=%2F&files=arrs.pkl"
    )


@pytest.fixture(scope="function")
def get_maps2(request):
    return download_and_load_pickle(
        "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz/download?path=%2F&files=arrs4.pkl"
    )


@pytest.fixture(scope="function")
def downloaded_images(request):
    return download_images(IMAGE_URLS, "downloaded_image", TEST_IMAGE_PATH)


@pytest.fixture(scope="function")
def downloaded_images2(request):
    return download_images(IMAGE_URLS2, "downloaded_image2", TEST_IMAGE_PATH)


def download_and_load_pickle(url):
    response = requests.get(url)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        with open(temp_file_path, "rb") as f:
            arrays = pickle.load(f)
        os.remove(temp_file_path)
        return arrays
    else:
        pytest.fail(
            f"Failed to download file from {url}. Status code: {response.status_code}"
        )


def download_images(image_urls, prefix, destination_path):
    image_paths = []
    os.makedirs(destination_path, exist_ok=True)
    for i, url in enumerate(image_urls):
        response = requests.get(url)
        if response.status_code == 200:
            image_path = os.path.join(destination_path, f"{prefix}_{i}.png")
            with open(image_path, "wb") as f:
                f.write(response.content)
            image_paths.append(image_path)
    return image_paths


def get_titles():
    start_time = datetime(2016, 4, 9, 0, 0, 0)
    end_time = datetime(2016, 4, 9, 22, 0, 0)
    interval = timedelta(hours=2)
    timestamps = []
    current_time = start_time
    while current_time <= end_time:
        timestamps.append(
            f'IRI(2016) {current_time.strftime("%Y-%m-%d %H:%M:%S")}'
        )
        current_time += interval
    return timestamps


def test_git_dat_world_plot(request, downloaded_images, get_maps):
    maps = get_maps
    titles = get_titles()
    fig_paths = [
        os.path.join(TEST_IMAGE_PATH, f"test_image_{i}.png")
        for i in range(len(maps))
    ]
    images_paths = downloaded_images
    plot(maps, fig_paths, titles=titles)
    saved_images = [plt.imread(fig_path) for fig_path in fig_paths]
    downloaded_images = [plt.imread(image_path) for image_path in images_paths]

    for fig_path, image_path in zip(fig_paths, images_paths):
        os.remove(fig_path)
        os.remove(image_path)
    assert len(saved_images) == len(downloaded_images)

    for saved_image, downloaded_image in zip(saved_images, downloaded_images):
        assert (
            np.corrcoef(saved_image.flatten(), downloaded_image.flatten())[
                0, 1
            ]
            >= 0.98
        )


def test_git_world_plot(request, downloaded_images2, get_maps2):
    maps = get_maps2
    fig_paths = [
        os.path.join(TEST_IMAGE_PATH, f"test_image2_{i}.png")
        for i in range(len(maps))
    ]
    images_paths = downloaded_images2
    plot(maps, fig_paths)
    saved_images = [plt.imread(fig_path) for fig_path in fig_paths]
    downloaded_images2 = [
        plt.imread(image_path) for image_path in images_paths
    ]

    for fig_path, image_path in zip(fig_paths, images_paths):
        os.remove(fig_path)
        os.remove(image_path)
    assert len(saved_images) == len(downloaded_images2)

    for saved_image, downloaded_image in zip(saved_images, downloaded_images2):
        assert (
            np.corrcoef(saved_image.flatten(), downloaded_image.flatten())[
                0, 1
            ]
            >= 0.98
        )
