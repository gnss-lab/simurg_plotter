#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
 
from .annotations import get_parallels_patch
from .annotations import plot_gridlines, plot_terminator, plot_geo_borders
from typing import Tuple, Dict, Any
# from simurg_core import PRODUCT_TYPES

# from . import font, WATER_MARK, DTYPE, PLOT_PROP

"""
Created on Thu Jul 20 12:36:56 2017

@author: Artem Vesnin
"""

# font: dict = {'family': 'sans-serif',
#               "sans-serif": "DejaVu Sans",
#               'size': 14}

# matplotlib.rc('font', **font)

WATER_MARK: str = "Created by SIMuRG"

PLOT_PROP: dict = {"alpha": 1,
                   "vmax": None,
                   "vmin": None}

DTYPE = [('lat', 'float'), ('lon', 'float'), ('vals', 'float')]

PLOT_PROP.update({"s": None,
                  "cmap": "jet",
                  "marker": "s"})

PRODUCT_TYPES: dict = {"dtec_2_10":
                           {"name": "2-10 minute TEC variations", "unit": "TECu"},
                       "dtec_10_20":
                           {"name": "10-20 minute TEC variations", "unit": "TECu"},
                       "dtec_20_60":
                           {"name": "20-60 minute TEC variations", "unit": "TECu"},
                       "roti":
                           {"name": "ROTI", "unit": "TECu/min"},
                       "tec_adjusted":
                           {"name": "Adjusted TEC", "unit": "TECu"}
                       }

LAYOUT_PROP: dict = {"fig_size": (18, 9),
                      "projection": ccrs.PlateCarree(),
                      "transform": ccrs.PlateCarree(),
                      "polar": False,
                      "xmarg": 0.,
                      "ymarg": 0.,
                      "mageq": False,
                      "subsolar": False,
                      "min_lat": -90,
                      "max_lat": 90,
                      "min_lon": -180,
                      "max_lon": 180,
                      "show_on_screen": False,
                      "aspect": "auto",
                      "grid": "subionospheric points"}

REF_TEXT: dict = {"var_type": "",
                  "title": "",
                  "vlabel": ""}

class Map2D(object):
    """
    Class for plotting 2D maps of data.
    
    :param dims: Dimensions of the map in terms of latitude and longitude (lat, lon)
    :type dims: tuple
    """

    def __init__(self, dims: Tuple[int, int]):
        self.data = None
        self.dims = (dims[0], dims[1])  # lat, lon
        self.steps = self._check_dims()
        self.grid_data = None
        # self.fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
        # self.plot_ax = plot_ax
        self.cbar = None
        self.prop = LAYOUT_PROP.copy()
        self.plot_prop = None
        self.ref_text = REF_TEXT.copy()
        self._first_plot = True
        self.closed = False

    def _check_dims(self) -> Tuple[int, int]:
        if self.dims[0] % 2 != 1:
            raise ValueError("Latitude dimension must be odd")
        if self.dims[1] % 2 != 0:
            raise ValueError("Longitude dimension must be even")
        lat_step = 180. / (self.dims[0] - 1)
        lon_step = 360. / self.dims[1]
        if lat_step != int(lat_step):
            raise ValueError("Latitude step must be integer")
        if lon_step != int(lon_step):
            raise ValueError("Longitude step must be integer")
        return (lat_step, lon_step)

    def _update_layout_props(self, **kwargs):
        self.prop = {k: v for k, v in LAYOUT_PROP.items()}
        for k, v in kwargs.items():
            if k not in self.prop:
                continue
                # raise ValueError("Unhandeled property {}".format(k))
            self.prop[k] = v

    @staticmethod
    def get_vmin_vmax(average, sd, **kwargs):
        lim = round(abs(average) + abs(2 * sd), 1)
        llim, rlim = -lim, lim
        if 'min' in kwargs and 'max' in kwargs:
            if kwargs['min'] >= 0:
                llim = 0
            if kwargs['max'] <= 0:
                rlim = 0
        return llim, rlim

    def _update_plot_props(self, **kwargs):
        self.plot_prop = {k: v for k, v in PLOT_PROP.items()}
        if kwargs.get('mpl') is not None:
            for k in self.plot_prop:
                if k in kwargs['mpl']:
                    self.plot_prop[k] = kwargs['mpl'][k]

        if self.plot_prop["vmax"] is None or self.plot_prop["vmin"] is None:
            vals = self.data['vals']
            s = np.std(vals)
            a = np.average(vals)
            lims = self.get_vmin_vmax(a, s)
            if self.plot_prop["vmin"] is None:
                self.plot_prop["vmin"] = lims[0]
            if self.plot_prop["vmax"] is None:
                self.plot_prop["vmax"] = lims[1]

        if self.plot_prop["s"] is None:
            lat_range = np.abs(self.prop["min_lat"] - self.prop["max_lat"])
            lon_range = np.abs(self.prop["min_lon"] - self.prop["max_lon"])
            lat_range = 180 / lat_range
            lon_range = 360 / lon_range
            scale = min(lat_range, lon_range)
            self.plot_prop["s"] = 1 if int(scale) < 1 else int(scale)

    def _update_magnetic_equator(self, ax):
        if self.prop["mageq"] is True:
            ax.add_patch(get_parallels_patch())

    def _update_terminator(self, ax, map_time):
        if self.prop["subsolar"]:
            return plot_terminator(ax, time=map_time)

    def _update_margins_limits(self, ax):
        ax.set_xmargin(self.prop["xmarg"])
        ax.set_ymargin(self.prop["ymarg"])
        ax.set_xlim([self.prop["min_lon"], self.prop["max_lon"]])
        ax.set_ylim([self.prop["min_lat"], self.prop["max_lat"]])

    def _make_updatable_cbar(self,ax):
        if self.prop["show_on_screen"]:

            def resize_colobar(event):
                ax.figure.canvas.draw_idle()
                posn = ax.get_position()
                self.cbar_ax.set_position([posn.x0 + posn.width + 0.04,
                                           posn.y0,
                                           0.04,
                                           posn.height])

            ax.figure.canvas.mpl_connect('resize_event', resize_colobar)
            ax.figure.canvas.mpl_connect('draw_event', resize_colobar)

    def _make_text(self, ax, time):
        time_label = time.strftime("%Y-%m-%dT%H:%M:%SZ (DOY %j)")
        title = time_label + "\n" + self.ref_text["var_type"]
        if self.ref_text["title"].strip() != "":
            title = self.ref_text["title"] + "\n" + title
        ax.figure.suptitle(WATER_MARK, fontsize=8, x=0.85, alpha=0.3)
        ax.set_title(title)
        ax.figure.text(0.5, 0.12, WATER_MARK,
                      fontsize=12, color='gray',
                      ha='center', va='bottom', alpha=0.3)

    def _update_data(self, data: np.ndarray) -> None:
        """
        Update the map data.

        :param data: Structured array of data values
        :type data: numpy.ndarray
        """
        self.data = data
        self.grid_data = None

    def set_data(self, data):
        self._update_data(data)

    def update_text(self, **kwargs):
        """
        Updates text that must be on a map. See REF_TEXT
        product_type : string
        """
        product_type = kwargs.get("product_type", None)
        if product_type is not None:
            self.ref_text = {"var_type": PRODUCT_TYPES[product_type]["name"],
                             "title": "",
                             "vlabel": PRODUCT_TYPES[product_type]["unit"]}
        for k, v in kwargs.items():
            if k in self.ref_text:
                self.ref_text[k] = v

    def get_props(self):
        return self.prop

    def get_node(self, lat, lon):
        """
        Gives lat and lon nodes of regular grid assuming North pole 0 node for
        latitude and -180 longitude is 0 node for longitude
        """
        lat_node = round(-(lat - 90.) / self.steps[0])
        lon_node = round((lon + 180.) / self.steps[1])
        return int(lat_node), int(lon_node)

    def _regular_grid(self):
        """
        Calculcates data values on regular frid defined by steps or dims. Data
        are given by their coordinates (could be arbitrary).

        grid_data is 1d numpy array of dims[0]*dims[1] size, since it goes to
        matplotlib plotting. 2d array can be easily obtained using
        numpy.reshape()
        """
        dims = self.dims
        steps = self.steps
        grid_data = np.full((dims[0] * dims[1]), np.nan, dtype=np.float64)
        count = np.zeros((dims[0] * dims[1]), dtype=np.float64)
        for i in range(len(self.data["lat"])):
            lat = self.data["lat"][i]
            lon = self.data["lon"][i]
            lat_node, lon_node = self.get_node(lat, lon)
            node = lat_node * int(dims[1]) + lon_node
            if self.data["vals"][i] != 0:
                if np.isnan(grid_data[node]):
                    grid_data[node] = 0
                grid_data[node] += self.data["vals"][i]  # TODO add mapeights
                count[node] += 1
        for node in range(len(grid_data)):
            if count[node] != 0:
                grid_data[node] /= count[node]
        lon_grid = np.tile(np.arange(-180, 180, steps[1]), dims[0])
        lat_grid = np.repeat(np.arange(90, -90 - steps[0], -steps[0]), dims[1])
        self.grid_data = np.array(list(zip(lat_grid, lon_grid, grid_data)),
                                  dtype=DTYPE)

    def get_regular_grid(self, as_matrix=False, keep_nan=True):
        if self.grid_data is None:
            self._regular_grid()
        if as_matrix:
            result = self.grid_data['vals'].reshape(self.dims[0], self.dims[1])
        else:
            result = self.grid_data
            if not keep_nan:
                result = result[np.logical_not(np.isnan(result['vals']))]
        return result

    def prepare_layout(self, plot_ax: plt.Axes, **kwargs: Any) -> None:
        """
        Sets global settings and creates layout for the map.

        :param plot_ax: Axis object for plotting
        :type plot_ax: matplotlib.axes.Axes
        :param **kwargs: Additional keyword arguments for layout properties
        """
        if self.closed:
            raise RuntimeError('Figure is closed create new instance of Map2D')
        plot_ax.clear()
        self.cbar = None
        self._update_layout_props(**kwargs)
        # self.plot_ax = fig.add_subplot(0, projection=ccrs.PlateCarree())
        # self.plot_ax = plot_ax
        # self.plot_ax.clear()
        # plot_ax.set_aspect(self.prop["aspect"])
        plot_gridlines(plot_ax)
        plot_geo_borders(plot_ax)
        self._update_margins_limits(plot_ax)
        self._update_magnetic_equator(plot_ax)
        self.plot_prop = None
        self._first_plot = True
        # return plot_ax

    def plot(self, ax: plt.Axes, data: np.ndarray, **kwargs: Any) -> None:
        """
        Plots data on the map.

        :param ax: Axis object for plotting
        :type ax: matplotlib.axes.Axes
        :param data: Structured array of values to plot
        :type data: numpy.ndarray
        :param **kwargs: Additional keyword arguments
        """
        if self.closed:
            raise RuntimeError('Figure is closed create new instance of Map2D')
        if self.prop["polar"]:
            print("Polar plot is not implemented yet")
            return
        # matplotlib.rcParams.update({'font.size': font['size']})
        self.update_text(product_type=kwargs.get("product_type"),
                         **kwargs.get("text", {}))
        if self.plot_prop is None:
            self._update_plot_props(**kwargs)
        elif kwargs.get("mpl", None) is not None:
            pass
            # print("""Warning: ignore current properties {}. Previous {}
            # are used. Use prepare_layout to drop curent
            # ones""".format(kwargs["mpl"], self.plot_prop))

        self.terminator = self._update_terminator(ax, kwargs["time"])
        # print(terminator)

        # ax.scatter(data['lon'], data['lat'], c=data['vals'],
        #                            transform=self.prop["transform"],
        #                            zorder=2,
        #                            **self.plot_prop)
        self.sct = ax.scatter(data['lon'], data['lat'], c=data['vals'],
                                   transform=self.prop["transform"],
                                   zorder=2,
                                   **self.plot_prop)
        # if self.cbar is None:
        #     self.cbar = ax.figure.colorbar(self.sct, label=self.ref_text["vlabel"], fraction=0.046, pad=0.04)
        self._make_text(ax, kwargs["time"])
        # TODO redraw cbar if property are changed
        # self._make_plot(ax, kwargs["save_fig"])
        
        new_ax = self._make_plot(ax, kwargs["save_fig"])
        return new_ax

    def _make_plot(self, ax,fig_path=None):
        if fig_path is not None:
            matplotlib.use('Agg')
            ax.figure.savefig(fig_path, bbox_inches='tight', transparent=False)
        else:
            return ax

    def plot_scatter(self, ax: plt.Axes, data: np.ndarray, **kwargs: Any) -> None:
        """
        Plots scatter data on the map.

        :param ax: Axis object for plotting
        :type ax: matplotlib.axes.Axes
        :param data: Structured array of scatter data
        :type data: numpy.ndarray
        :param **kwargs: Additional keyword arguments
        """
        repeats = 1 if self._first_plot else 1
        for _ in range(repeats):
            self._update_data(data)
            if self.prop["grid"] == "subionospheric points":
                return self.plot(ax, self.data, **kwargs)
            elif self.prop["grid"] == "regular":
                self._regular_grid()
                return self.plot(ax, self.grid_data, **kwargs)
        self._first_plot = False

    def clear(self):
        """Clears the map."""
        self.sct.remove()
        if self.terminator:
            self.terminator.remove()

    def close(self, ax):
        """
        Closes the map.

        :param ax: Axis object for plotting
        :type ax: matplotlib.axes.Axes
        """
        plt.close(ax.figure)
        self.closed = True


def plot_map(_plot_ax: plt.Axes, data: Dict[str, np.ndarray],  **kwargs: Any):
    """
    Plots data as a function of latitude and longitude.

    :param _plot_ax: Axis object for plotting
    :type _plot_ax: matplotlib.axes.Axes
    :param data: Dictionary of numpy arrays
    :type data: dict
    """
    props = LAYOUT_PROP.copy()
    props.update(kwargs)
    dtec = Map2D((181, 360))
    dtec.prepare_layout( _plot_ax, **props)
    dtec._first_plot = False
    dtec.plot_scatter(_plot_ax, data, **kwargs)
    return dtec.sct
