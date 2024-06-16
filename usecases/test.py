from simurg_plotter.manager import PlotManager, Plots
from simurg_plotter.ionospheric_pierce_point import Series
import warnings
from pathlib import Path
from numpy.typing import NDArray
import datetime
import h5py
from dateutil import tz
import numpy as np
import ionex

# Ignore all warnings
warnings.filterwarnings("ignore")

TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
_UTC = tz.gettz('UTC')

def retrieve_data(file: str | Path, times: list[datetime.datetime] | None = None) -> dict[datetime.datetime, NDArray]:
    if times is None:
        times = []
    f_in = h5py.File(file, 'r')
    data = {}
    for str_time in list(f_in['data'])[:]:
        time = datetime.datetime.strptime(str_time, TIME_FORMAT)
        time = time.replace(tzinfo=time.tzinfo or _UTC)
        if times and not time in times:
            continue
        data[time] = f_in['data'][str_time][:]
    return data

def extract_series_data(file_path: str):
    series_dict = []
    with h5py.File(file_path, "r") as f:
        for sat_key in f["irkj"].keys():
            data = f["irkj"][sat_key]
            series = Series([
                None,
                None,
                data["sip_lon"][:],
                data["sip_lat"][:],
                data["sip_larc"][:],
                data["elevation"][:],
                data["azimuth"][:],
                sat_key]
            )
            series_dict.append(series)
    return series_dict

times = [(datetime.datetime(2024, 4, 19) + datetime.timedelta(minutes=i)).replace(tzinfo=(datetime.datetime(2024, 4, 19) + datetime.timedelta(minutes=i)).tzinfo or _UTC) for i in range(30)]
data = retrieve_data("files/dtec_2_10_2024_110_50_56_N_100_110_E_b4aa.h5", times=times)

# Map2D plot
# plotter = PlotManager(nrows=1, ncols=1)
# plotter.plot_map2d(0, 0, data[times[0]], title="Map2D", product_type="dtec_2_10", time=times[0], save_fig=None, polar=False, subsolar=True, min_lat=50, max_lat=55, min_lon=100, max_lon=110)
# plotter.save("map2d_plot.png")

# DST plot
start_date = datetime.datetime(2024, 4, 1)
time_interval = datetime.timedelta(hours=1)
timestamps = [start_date + i * time_interval for i in range(24*30)]
dst_values = np.random.uniform(low=-100, high=100, size=len(timestamps))
dst_data = np.column_stack((timestamps, dst_values))

# plotter = PlotManager(nrows=1, ncols=1)
# plotter.plot_dst(0, 0, dst_data, time=times[10])
# plotter.save("dst_plot.png")

# GIM plot
gd = {}
with open('files/uqrg0010.17i') as file:
    inx = ionex.reader(file)
    for ionex_map in inx:
        gd[ionex_map.epoch.replace(tzinfo=ionex_map.epoch.tzinfo or _UTC)] = [np.reshape(ionex_map.tec, (71, 73))]

time = datetime.datetime(2017, 1, 1, 0, 0, 0).replace(tzinfo=datetime.datetime(2017, 1, 1, 0, 0, 0).tzinfo or _UTC)
time2 = datetime.datetime(2017, 1, 1, 5, 0, 0).replace(tzinfo=datetime.datetime(2017, 1, 1, 0, 0, 0).tzinfo or _UTC)
# plotter = PlotManager(nrows=1, ncols=1)
# plotter.plot_gim(0, 0, gd[time], title=f'IRI(2017) {time.strftime("%Y-%m-%d %H:%M:%S")}', time=time)
# plotter.save("gim_plot.png")

# IPP Mercator plot
ipp_data = extract_series_data("files/dtec_2_10_2021_308_7140.h5")
# plotter = PlotManager(nrows=1, ncols=1)
# plotter.plot_ipp_merc(0, 0, ipp_data)
# plotter.save("ipp_mercator_plot.png")

# IPP Polar plot
# plotter = PlotManager(nrows=1, ncols=1)
# plotter.plot_ipp_pol(0, 0, ipp_data)
# plotter.save("ipp_polar_plot.png")

plotter = PlotManager(nrows=3, ncols=2, height=12)
plotter.plot_map2d(0, 0, data[times[0]], title="Map2D", product_type="dtec_2_10", time=times[0], save_fig=None, polar=False, subsolar=True, min_lat=50, max_lat=55, min_lon=100, max_lon=110)
plotter.plot_map2d(0, 1, data[times[0]], title="Map2D", colorbar=True, product_type="dtec_2_10", time=times[0], save_fig=None, polar=False, subsolar=True, min_lat=50, max_lat=55, min_lon=100, max_lon=110)
start_date = datetime.datetime(2024, 4, 1)
time_interval = datetime.timedelta(hours=1)
timestamps = [start_date + i * time_interval for i in range(24*30)]
dst_values = np.random.uniform(low=-100, high=100, size=len(timestamps))
dst_data = np.column_stack((timestamps, dst_values))
plotter.plot_gim(1, 0, gd[time], title=f'IRI(2017) {time.strftime("%Y-%m-%d %H:%M:%S")}', colorbar=True, time=time)
plotter.plot_gim(1, 1, gd[time2], title=f'IRI(2017) {time2.strftime("%Y-%m-%d %H:%M:%S")}', colorbar=True, time=time2)


plotter.plot_dst(2, 0, dst_data, time=times[10], colspan=2)
plotter.save("combined_plot.png")

for i in range(6):
    plotter = PlotManager(nrows=1, ncols=3, height=3, dpi=72)
    plotter.plot_map2d(0, 0, data[times[i]], title="Map2D", product_type="dtec_2_10", time=times[i], save_fig=None, polar=False, subsolar=True, min_lat=50, max_lat=55, min_lon=100, max_lon=110)
    plotter.plot_map2d(0, 1, data[times[i+1]], title="Map2D", product_type="dtec_2_10", time=times[i+1], save_fig=None, polar=False, subsolar=True, min_lat=50, max_lat=55, min_lon=100, max_lon=110)
    plotter.plot_map2d(0, 2, data[times[i+2]], title="Map2D", product_type="dtec_2_10", time=times[i+2], save_fig=None, polar=False, subsolar=True, min_lat=50, max_lat=55, min_lon=100, max_lon=110)
    plotter.save(f"combined_plot_{i}.png")
