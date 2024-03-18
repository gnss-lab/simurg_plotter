import os
import requests
import tempfile
import pickle
import pytest
import matplotlib.pyplot as plt
import numpy as np

from simurg_plotter.ionospheric_pierce_point.visualization import mercator_plot, polar_plot

MODULE_PATH = os.path.dirname(__file__)
TEST_IMAGE_PATH = os.path.join(MODULE_PATH, "test_images")
BASE_URL = "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz/download?path=%2F&files="

@pytest.fixture(scope="function")
def get_series(request):
    return download_and_load_pickle(
        "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz/download?path=%2F&files=test_series.pkl"
    )

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

def download_image(image_url, prefix, destination_path):
    os.makedirs(destination_path, exist_ok=True)
    response = requests.get(image_url)
    if response.status_code == 200:
        image_path = os.path.join(destination_path, f"{prefix}.png")
        with open(image_path, "wb") as f:
            f.write(response.content)
    return image_path

def test_mercator_plot(request, get_series):
    for deg, cutoff in zip([0, 10, 30], ["no", "10deg", "30deg"]):
        url = BASE_URL+f"ipp_mercator_{cutoff}_cutoff.png"
        downloaded_image_path = download_image(url, f"test_mercator_{cutoff}", TEST_IMAGE_PATH)
        filename = TEST_IMAGE_PATH+f"ipp_mercator_{cutoff}_cutoff.png"
        if cutoff == "no":
            mercator_plot(get_series, filename=filename)
        else:
            mercator_plot(get_series, filename=filename, elevation_cutoff=deg)
        result = plt.imread(filename)
        downloaded_image = plt.imread(downloaded_image_path)
        assert (
            np.corrcoef(result.flatten(), downloaded_image.flatten())[
                0, 1
            ]
            >= 0.98
        )
        

def test_polar_plot(request, get_series):
     for deg, cutoff in zip([0, 10, 30], ["no", "10deg", "30deg"]):
        url = BASE_URL+f"ipp_polar_{cutoff}_cutoff.png"
        downloaded_image_path = download_image(url, f"test_polar_{cutoff}", TEST_IMAGE_PATH)
        filename = TEST_IMAGE_PATH+f"ipp_polar_{cutoff}_cutoff.png"
        if cutoff == "no":
            polar_plot(get_series, filename=filename)
        else:
            polar_plot(get_series, filename=filename, elevation_cutoff=deg)
        result = plt.imread(filename)
        downloaded_image = plt.imread(downloaded_image_path)
        assert (
            np.corrcoef(result.flatten(), downloaded_image.flatten())[
                0, 1
            ]
            >= 0.98
        )