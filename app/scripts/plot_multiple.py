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

_UTC = tz.gettz('UTC')

def parse_timestamp(ts):
    return ts.replace(tzinfo=ts.tzinfo or _UTC) if ts else None

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

def generate_plots(request_id, height, dpi, plot_data_path, output_file, timestamp):
    try:
        with open(plot_data_path, 'r') as f:
            plot_request = json.load(f)

        nrows = plot_request['nrows']
        ncols = plot_request['ncols']
        plots = plot_request['plots']
        height_ratios = plot_request.get('height_ratios', None)

        plot_manager = PlotManager(nrows=nrows, ncols=ncols, height=int(height), dpi=int(dpi), height_ratios=height_ratios)
        timestamp = parse_timestamp(timestamp)
        total_plots = len(plots) + 1
        for i, plot in enumerate(plots):
            plot_type = Plots(plot['plot_type'])
            row = plot['row']
            col = plot['col']
            rowspan = plot.get('rowspan', 1)
            colspan = plot.get('colspan', 1)
            data_file = plot['data_file']
            title = plot.get('title', '')
            product_type = plot.get('product_type')

            if plot_type == Plots.MAP2D:
                data = retrieve_data(data_file, times=[timestamp])[timestamp]
                plot_manager.plot_map2d(row, col, data, title=title, colspan=colspan, rowspan=rowspan, time=timestamp, product_type=product_type, polar=False, subsolar=True, min_lat=plot.get('min_lat', None), max_lat=plot.get('max_lat', None), min_lon=plot.get('min_lon', None), max_lon=plot.get('max_lon', None), colorbar=plot.get('colorbar', False))
            elif plot_type == Plots.GIM:
                gim_data = load_gim_data(data_file)
                plot_manager.plot_gim(row, col, gim_data[timestamp], title=f"GIM {timestamp}", colspan=colspan, rowspan=rowspan, time=timestamp, colorbar=plot.get('colorbar', False))
            elif plot_type == Plots.IPP_MERCATOR:
                ipp_data = extract_series_data(data_file)
                plot_manager.plot_ipp_merc(row, col, ipp_data, title=title, colspan=colspan, rowspan=rowspan)
            elif plot_type == Plots.IPP_POLAR:
                ipp_data = extract_series_data(data_file)
                plot_manager.plot_ipp_pol(row, col, ipp_data, title=title, colspan=colspan, rowspan=rowspan)
            elif plot_type == Plots.DST:
                dst_data = np.loadtxt(data_file, delimiter=plot.get('delimiter', ','))
                plot_manager.plot_dst(row, col, dst_data, title=title, colspan=colspan, rowspan=rowspan, time=timestamp)

        plot_manager.save(f"./data/{output_file}")

    except Exception as e:
        raise e

if __name__ == "__main__":
    if len(sys.argv) != 8:
        print("Usage: python plot_multiple.py <height> <dpi> <request_id> <plot_data_path> <start_time> <end_time> <interval_seconds>")
        sys.exit(1)

    height, dpi, request_id, plot_data_path, start_time, end_time, interval_seconds = sys.argv[1:8]

    interval_start = datetime.datetime.fromisoformat(start_time)
    interval_end = datetime.datetime.fromisoformat(end_time)

    current_time = interval_start
    while current_time < interval_end:
        subinterval_end = current_time + datetime.timedelta(seconds=int(interval_seconds))

        if subinterval_end > interval_end:
            subinterval_end = interval_end

        output_file = f"{request_id}_data/{current_time.strftime('%H%M%S')}.png"

        generate_plots(request_id, height, dpi, plot_data_path, output_file, current_time)

        current_time = subinterval_end
