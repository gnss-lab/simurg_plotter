import pytest
import numpy as np
import requests
import tempfile
from simurg_plotter.global_ionospheric_map.geo_mag_processing import get_gm_contours, get_uniform_mag_net, gims_limits, prepare_contours

@pytest.fixture(scope="function")
def arrays():
    url = "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz/download?path=%2F&files=gims.npy"
    response = requests.get(url)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        arrays = np.load(temp_file_path, allow_pickle=True)
        return arrays
    else:
        pytest.fail(f"Failed to download file from {url}. Status code: {response.status_code}")

@pytest.fixture(scope="function")
def contours():
    url = "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz/download?path=%2F&files=maps.npy"
    response = requests.get(url)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        contours = np.load(temp_file_path, allow_pickle=True)
        return contours
    else:
        pytest.fail(f"Failed to download file from {url}. Status code: {response.status_code}")

def test_get_uniform_mag_net():
    result = get_uniform_mag_net()

    assert isinstance(result, np.ndarray)
    assert result.shape != (0, 0)

def test_get_gm_contours():
    result = get_gm_contours()

    assert isinstance(result, np.ndarray)
    assert result.shape != (0, 0)

def test_gims_limits(arrays):
    result = gims_limits(arrays)
    assert isinstance(result, list)
    assert len(result) == 2


def test_prepare_contours():
    geo_result = prepare_contours(
        True, get_gm_contours())
    non_geo_result = prepare_contours( 
        False, get_gm_contours())
    
    assert isinstance(geo_result, np.ndarray)
    assert isinstance(non_geo_result, np.ndarray)
    assert geo_result.shape == (len(get_gm_contours()) * 2, 2)
    assert non_geo_result.shape == (len(get_gm_contours()) * 2, 2)


