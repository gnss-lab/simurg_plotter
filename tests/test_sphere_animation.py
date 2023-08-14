import cartopy
import cartopy.crs as ccrs
import h5py
import matplotlib.pyplot as plt
import pandas as pd
import pytest

from sphere_animation.utils import plot_sphere, get_all_data


@pytest.fixture
def sample_dataframe():
    data = {
        'lon': [0, 45, 90],
        'lat': [30, 60, 90],
        'vals': [1, 2, 3]
    }
    return pd.DataFrame(data)


# noinspection PyUnresolvedReferences
def test_plot_sphere_with_geoaxes_subplot(sample_dataframe):
    # Test if the function works with GeoAxesSubplot
    fig = plt.figure()
    projection = ccrs.Orthographic(central_longitude=0, central_latitude=0)
    ax = fig.add_subplot(1, 1, 1, projection=projection)

    scatter = plot_sphere(0, 0, sample_dataframe, ax=ax)
    assert scatter is not None
    assert isinstance(ax, cartopy.mpl.geoaxes.GeoAxesSubplot)


def test_get_all_data(tmpdir):
    # Create a sample HDF5 file with multiple groups
    test_file = tmpdir.join('test_file.h5')
    with h5py.File(test_file, 'w') as file:
        group1 = file.create_group('data1')
        dataset1 = group1.create_dataset('test_dataset1', data=[1, 2, 3])

        group2 = file.create_group('data2')
        dataset2 = group2.create_dataset('test_dataset2', data=[4, 5, 6])

    # Test if the function retrieves data from the HDF5 file
    data = get_all_data(str(test_file))

    for key in data.keys():
        assert 'data' in key  # Check for the presence of 'data' in each key



def test_get_all_data_no_data_group(tmpdir):
    # Create an HDF5 file without a 'data' group
    test_file = tmpdir.join('test_file.h5')
    with h5py.File(test_file, 'w') as file:
        dataset = file.create_dataset('test_dataset', data=[1, 2, 3])

    # Test if the function handles missing 'data' group gracefully
    data = get_all_data(str(test_file))
    assert data == {}


def test_get_all_data_empty_file(tmpdir):
    # Create an empty HDF5 file
    test_file = tmpdir.join('test_file.h5')
    with h5py.File(test_file, 'w') as file:
        pass

    # Test if the function handles empty file gracefully
    data = get_all_data(str(test_file))
    assert not data


if __name__ == '__main__':
    pytest.main()
