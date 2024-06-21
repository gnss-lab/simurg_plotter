import sys
import json
import datetime
import numpy as np
import h5py
from pathlib import Path
from dateutil import tz
from simurg_plotter.manager import PlotManager, Plots
from simurg_plotter.ionospheric_pierce_point import Series
import ionex
import os

_UTC = tz.gettz('UTC')

def parse_timestamp(ts):
    return datetime.datetime.fromisoformat(ts).replace(tzinfo=datetime.datetime.fromisoformat(ts).tzinfo or _UTC) if ts else None

def retrieve_data(file: str | Path, times: list[datetime.datetime] | None = None) -> dict[datetime.datetime, np.ndarray]:
    if times is None:
        times = []
    f_in = h5py.File(file, 'r')
    data = {}
    for str_time in list(f_in['data'])[:]:
        time = datetime.datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S.%f')
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

def load_gim_data(file_path: str):
    gd = {}
    with open(file_path) as file:
        inx = ionex.reader(file)
        for ionex_map in inx:
            gd[ionex_map.epoch.replace(tzinfo=ionex_map.epoch.tzinfo or _UTC)] = [np.reshape(ionex_map.tec, (71, 73))]
    return gd

def update_progress(request_id, progress):
    progress_file = f"./data/{request_id}_progress.json"
    with open(progress_file, 'w') as f:
        json.dump({"progress": progress}, f)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python plot_single.py <height> <dpi> <output_file> <plot_data_path> <request_id>")
        sys.exit(1)
    
    height, dpi, output_file, plot_data_path, request_id = sys.argv[1:6]
    
    with open(plot_data_path, 'r') as f:
        plot_request = json.load(f)
    
    nrows = plot_request['nrows']
    ncols = plot_request['ncols']
    plots = plot_request['plots']
    height_ratios = plot_request.get('height_ratios', None)  # Получаем height_ratios из plot_request
    
    plot_manager = PlotManager(nrows=nrows, ncols=ncols, height=int(height), dpi=int(dpi), height_ratios=height_ratios)  # Передаем height_ratios в PlotManager

    total_plots = len(plots)+1
    for i, plot in enumerate(plots):
        plot_type = Plots(plot['plot_type'])
        row = plot['row']
        col = plot['col']
        rowspan = plot.get('rowspan', 1)
        colspan = plot.get('colspan', 1)
        data_file = plot['data_file']
        title = plot.get('title', '')
        timestamp = parse_timestamp(plot.get('timestamp'))
        product_type = plot.get('product_type')
        
        if plot_type == Plots.MAP2D:
            data = retrieve_data(data_file, times=[timestamp])[timestamp]
            plot_manager.plot_map2d(row, col, data, title=title, colspan=colspan, rowspan=rowspan, time=timestamp, product_type=product_type, polar=False, subsolar=True, min_lat=plot.get('min_lat', None), max_lat=plot.get('max_lat', None), min_lon=plot.get('min_lon', None), max_lon=plot.get('max_lon', None), colorbar=plot.get('colorbar', False))
        elif plot_type == Plots.GIM:
            gim_data = load_gim_data(data_file)
            plot_manager.plot_gim(row, col, gim_data[timestamp], title=title, colspan=colspan, rowspan=rowspan, time=timestamp, colorbar=plot.get('colorbar', False))
        elif plot_type == Plots.IPP_MERCATOR:
            ipp_data = extract_series_data(data_file)
            plot_manager.plot_ipp_merc(row, col, ipp_data, title=title, colspan=colspan, rowspan=rowspan)
        elif plot_type == Plots.IPP_POLAR:
            ipp_data = extract_series_data(data_file)
            plot_manager.plot_ipp_pol(row, col, ipp_data, title=title, colspan=colspan, rowspan=rowspan)
        elif plot_type == Plots.DST:
            dst_data = np.loadtxt(data_file, delimiter=plot.get('delimiter', ','))
            plot_manager.plot_dst(row, col, dst_data, title=title, colspan=colspan, rowspan=rowspan, time=timestamp)

        progress = (i + 1) / total_plots * 100
        update_progress(request_id, progress)

    plot_manager.save(f"./data/{output_file}")
    update_progress(request_id, 100)
