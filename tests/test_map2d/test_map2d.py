import pytest
import datetime as dt
import os
import numpy as np
import requests
import tempfile
import pickle
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from simurg_plotter.map2d.map2d import Map2D

matplotlib.use("Agg")

MODULE_PATH = os.path.dirname(__file__)
TEST_IMAGE_PATH = os.path.join(MODULE_PATH, "test_images")
BASE_URL = "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz/download?path=%2F&files="

TEXT = {"var_type": "2-20 min TEC variations",
        "title": "",
        "vlabel" : "dI, TECu"}

@pytest.fixture(scope="function")
def get_map2d_data(request):
    return download_and_load_pickle(
        "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz/download?path=%2F&files=map2d_data.pkl"
    )

@pytest.fixture(scope="function")
def get_map2d_data_dtec(request):
    return download_and_load_pickle(
        "https://cloud.iszf.irk.ru/index.php/s/tCLs3QNiQb8VGDz/download?path=%2F&files=map2d_data_dtec.pkl"
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

dtec = Map2D(dims=(181, 360))

time = dt.datetime(2017, 1, 1, 0, 0, 0)
width=1280 
height=720
dpi=150
fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
def test_scatter_region(get_map2d_data):
    
    mpl_kwargs = {"marker": "s", "s": None, "alpha": 1, "cmap": "jet"}
    plot_data = get_map2d_data
    regions = ["north_america", "us", "europe", "japan"]
    downloaded_images_urls=[BASE_URL+f"scatter_"+region+".png" for region in regions]
    downloaded_images_paths = [download_image(
            url, f"test_scatter_{region}", TEST_IMAGE_PATH
        ) for region, url in zip(regions,downloaded_images_urls)]
    test_images_paths = [TEST_IMAGE_PATH+f"/scatter_"+region+".png" for region in regions]
    #america
    plot_ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    dtec.prepare_layout(plot_ax, min_lat=0, max_lat=80,
                        min_lon=-180, max_lon=-40, aspect = 'equal')

    dtec.plot_scatter(plot_data, save_fig=TEST_IMAGE_PATH+"/scatter_north_america.png", time=time,
                    product_type="dtec_2_10", mpl=mpl_kwargs)
    fig.clf()
    # us
    plot_ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    dtec.prepare_layout(plot_ax, min_lat=30, max_lat=50,
                        min_lon=-140, max_lon=-40, aspect = 'equal')

    dtec.plot_scatter(plot_data, save_fig=TEST_IMAGE_PATH+"/scatter_us.png", time=time,
                    text = TEXT, mpl=mpl_kwargs)
    fig.clf()
    #europe
    plot_ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    dtec.prepare_layout(plot_ax, min_lat=20, max_lat=70,
                        min_lon=-30, max_lon=60, aspect = 'equal')

    dtec.plot_scatter(plot_data, save_fig=TEST_IMAGE_PATH+"/scatter_europe.png", time=time,
                    text = TEXT, mpl=mpl_kwargs)
    fig.clf()
    #japan
    plot_ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    dtec.prepare_layout(plot_ax, min_lat=20, max_lat=60,
                        min_lon=125, max_lon=150, aspect = 'equal')

    dtec.plot_scatter(plot_data, save_fig=TEST_IMAGE_PATH+"/scatter_japan.png", time=time,
                    text = TEXT, mpl=mpl_kwargs)
    #with vlimits
    dtec.update_text(title="Bla Bla Title")
    dtec.plot_scatter(plot_data, save_fig=TEST_IMAGE_PATH+"/scatter_region_with_vlimits.png", 
                  time=time,
                  mpl={'vmin': -0.5, 'vmax': 0.5})
    fig.clf()
    for test, downloaded in zip(test_images_paths, downloaded_images_paths):
        result = plt.imread(test)
        downloaded_image = plt.imread(downloaded)
        assert (
            np.corrcoef(result.flatten(), downloaded_image.flatten())[0, 1]
            >= 0.95
        )
    result = plt.imread(TEST_IMAGE_PATH+"/scatter_region_with_vlimits.png")
    url = BASE_URL+f"scatter_region_with_vlimits.png"
    downloaded_image = plt.imread(download_image(
            url, f"test_scatter_region_with_vlimits", TEST_IMAGE_PATH
        ))
    assert (
            np.corrcoef(result.flatten(), downloaded_image.flatten())[0, 1]
            >= 0.95
        )
    
def test_scatter_entire_maqeq(get_map2d_data_dtec):
    plot_ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    plot_data = get_map2d_data_dtec
    dtec.update_text(**TEXT)
    dtec.prepare_layout(plot_ax, color_lbl="dTEC", mageq=True)
    dtec.plot_scatter(plot_data, save_fig=TEST_IMAGE_PATH+"/scatter_entire_mageq.png",
                        time=time, mpl=None)
    dtec.plot_scatter(plot_data, save_fig=TEST_IMAGE_PATH+"/scatter_entire_mageq2.png",
                        time=time, mpl=None)
    fig.clf()
    result1 = plt.imread(TEST_IMAGE_PATH+"/scatter_entire_mageq.png")
    result2 = plt.imread(TEST_IMAGE_PATH+"/scatter_entire_mageq2.png")
    url1 = BASE_URL+f"scatter_entire_mageq.png"
    url2 = BASE_URL+f"scatter_entire_mageq2.png"
    downloaded_image1 = plt.imread(download_image(
            url1, f"test_scatter_entire_mageq", TEST_IMAGE_PATH
        ))
    downloaded_image2 = plt.imread(download_image(
            url2, f"test_scatter_entire_mageq2", TEST_IMAGE_PATH
        ))
    assert (
            np.corrcoef(result1.flatten(), downloaded_image1.flatten())[0, 1]
            >= 0.95
        )
    assert (
            np.corrcoef(result2.flatten(), downloaded_image2.flatten())[0, 1]
            >= 0.95
        )

def test_marker_changed(get_map2d_data_dtec):
    plot_ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    plot_data = get_map2d_data_dtec
    mpl_kwargs = {"marker": "s", "s": 10, "alpha": 1, "cmap": "jet"}
    dtec.prepare_layout(plot_ax, color_lbl="dTEC")
    dtec.plot_scatter(plot_data, mpl=mpl_kwargs,
                  save_fig=TEST_IMAGE_PATH+"/marker_changed.png",
                  time=time)
    fig.clf()
    result = plt.imread(TEST_IMAGE_PATH+"/marker_changed.png")
    url = BASE_URL+f"marker_changed.png"
    downloaded_image = plt.imread(download_image(
            url, f"test_marker_changed", TEST_IMAGE_PATH
        ))
    assert (
            np.corrcoef(result.flatten(), downloaded_image.flatten())[0, 1]
            >= 0.95
        )
    
def test_grided_entire(get_map2d_data_dtec):
    plot_ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    plot_data = get_map2d_data_dtec
    dtec.prepare_layout(plot_ax, polar=False, subsolar=True,
                    projection=ccrs.PlateCarree(), color_lbl="dTEC", grid="regular")
    dtec.plot_scatter(plot_data, time=time,
               save_fig=TEST_IMAGE_PATH+"/grided_entire.png",
               mpl=None)
    fig.clf()
    result = plt.imread(TEST_IMAGE_PATH+"/grided_entire.png")
    url = BASE_URL+f"grided_entire.png"
    downloaded_image = plt.imread(download_image(
            url, f"test_grided_entire", TEST_IMAGE_PATH
        ))
    assert (
            np.corrcoef(result.flatten(), downloaded_image.flatten())[0, 1]
            >= 0.95
        )
    

    


