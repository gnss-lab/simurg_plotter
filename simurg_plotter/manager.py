import matplotlib.animation
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.gridspec import GridSpec
import matplotlib
# matplotlib.use('agg')

from cartopy.mpl.geoaxes import GeoAxes
import cartopy.crs as ccrs
from mpl_toolkits.axes_grid1 import AxesGrid
from .global_ionospheric_map.visualization import plot as gim_plot
from .ionospheric_pierce_point import Series
from .ionospheric_pierce_point.visualization import mercator_plot, polar_plot
from .map2d.map2d import plot_map
from .disturbance_storm_time.dst import plot_dst
from enum import Enum
import imageio.v2 as imageio
from time import sleep
import os




class Plots(Enum):
    """Enum class defining different types of plots."""
    GIM = 'gim'
    IPP_MERCATOR = 'ipp_merc'
    IPP_POLAR = 'ipp_pol'
    MAP2D = 'map2d'
    DST = 'dst'



class PlotManager:
    """
    Class to manage plotting of different types of data.

    :param plots: List of plot types to be included, defaults to [Plots.MAP2D]
    :type plots: list, optional
    :param width: Width of the plot in pixels, defaults to 1280
    :type width: int, optional
    :param height: Height of the plot in pixels, defaults to 720
    :type height: int, optional
    :param dpi: Dots per inch for the plot resolution, defaults to 150
    :type dpi: int, optional
    """
    def __init__(self, plots=[Plots.MAP2D], width=1280, height=720, dpi=150):
        self.plots = plots
        self.width = width
        self.height = height
        self.dpi = dpi
        # self.fig, self.axs = self._create_subplots(len(plots), width, height, dpi)
        # self.map2d_prepared = False
        

    def _create_subplots(self, num_plots, width, height, dpi, plots):
        """Create subplots based on the number and types of plots specified."""
        axs = {}
        if Plots.MAP2D not in plots:
            if num_plots == 1:
                fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
                ax = fig.add_subplot(111, projection="polar" if Plots.IPP_POLAR in plots else None)
                # fig, ax = plt.subplots(1, 1, figsize=(width / dpi, height / dpi), dpi=dpi)
                axs[plots[0]] = ax if plots else None
                return fig, axs
            elif num_plots == 2:
                gs = GridSpec(2, 1, height_ratios=[1, 1])
                fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
                ax1 = fig.add_subplot(gs[0], projection="polar" if Plots.IPP_POLAR in plots else None) 
                ax2 = fig.add_subplot(gs[1])
                axs[plots[0]] = ax1 if Plots.MAP2D in plots else ax2
                axs[plots[1]] = ax2 if Plots.MAP2D in plots else ax1
                return fig, axs
            elif num_plots == 4:
                fig, axs = plt.subplots(2, 2, figsize=(width / dpi, height / dpi), dpi=dpi)
                for i in range(2):
                    for j in range(2):
                        axs[i][j] = axs[i][j] if plots else None
                return fig, axs
            else:
                raise ValueError("Unsupported number of plots")
        else:
            if num_plots == 1:
                fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
                ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
                axs[plots[0]] = ax if plots else None
                return fig, axs
            elif num_plots == 2:
                gs = GridSpec(2, 1, height_ratios=[5, 1])
                fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
                axs[Plots.MAP2D] = fig.add_subplot(gs[0], projection=ccrs.PlateCarree()) if Plots.MAP2D in plots else None
                plot_type = plots[1] if Plots.MAP2D in plots else plots[0]
                axs[plot_type] = fig.add_subplot(gs[1]) if plot_type != Plots.MAP2D else None
                
                return fig, axs

            elif num_plots == 4:
                gs = GridSpec(2, 2, height_ratios=[3,3])
                fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
                axs[Plots.MAP2D] = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
                other_plot_types = [plot_type for plot_type in plots if plot_type != Plots.MAP2D]
                for i, plot_type in enumerate(other_plot_types, start=1):
                    axs[plot_type] = fig.add_subplot(gs[i // 2, i % 2])
                
                return fig, axs
            else:
                raise ValueError("Unsupported number of plots")

             
    def plot_map2d(self, ax, data, **kwargs):
        """
        Plot 2D map data on a given axis.

        :param ax: Axis object for plotting
        :type ax: matplotlib.axes.Axes
        :param data: 2D map data to be plotted
        :type data: array-like
        :param **kwargs: Additional keyword arguments for plotting
        """
        plot_map(ax, data, **kwargs)

    def plot_dst(self, ax, data, **kwargs):
        """
        Plot DST (Disturbance Storm Time) data on a given axis.

        :param ax: Axis object for plotting
        :type ax: matplotlib.axes.Axes
        :param data: DST data to be plotted
        :type data: array-like
        :param **kwargs: Additional keyword arguments for plotting
        """
        ax.set_xlim(data[0, 0], data[-1, 0])
        plot_dst(ax, data, **kwargs)

    def plot_gim(self, ax, data, **kwargs):
        gim_plot(data, ax=ax, **kwargs)

    def plot_ipp_merc(self, ax, data, **kwargs):
        mercator_plot(data, ax=ax, **kwargs)

    def plot_ipp_pol(self, ax, data, **kwargs):
        polar_plot(data, ax=ax, **kwargs)

    def make_plot(self, fig, fig_path=None):
        """
        Save or display the generated plot.

        :param fig: Figure object containing the plot
        :type fig: matplotlib.figure.Figure
        :param fig_path: File path to save the plot, defaults to None
        :type fig_path: str, optional
        """
        if fig_path is not None:
            matplotlib.use('Agg')
            fig.savefig(fig_path, bbox_inches='tight', transparent=False)
        else:
            plt.show()

    def plot(self, ax, data, plot_type, **kwargs):
        """
        Plot data of a specified type on a given axis.

        :param ax: Axis object for plotting
        :type ax: matplotlib.axes.Axes
        :param data: Data to be plotted
        :type data: array-like
        :param plot_type: Type of plot to be generated (enum from Plots)
        :type plot_type: Plots
        :param **kwargs: Additional keyword arguments for plotting
        """
        if plot_type == Plots.MAP2D:
            self.plot_map2d(ax, data, **kwargs)
        elif plot_type == Plots.DST:
            self.plot_dst(ax, data, **kwargs)
        elif plot_type == Plots.GIM:
            self.plot_gim(ax, data, **kwargs)
        elif plot_type == Plots.IPP_POLAR:
            self.plot_ipp_pol(ax, data, **kwargs)
        elif plot_type == Plots.IPP_MERCATOR:
            self.plot_ipp_merc(ax, data, **kwargs)
        else:
            raise ValueError("Unsupported plot type")
        
    def draw_plots(self, plot_data, fig_path=None):
        """
        Draw plots based on the provided data.

        :param plot_data: Dictionary containing data for different plot types
        :type plot_data: dict
        :param fig_path: File path to save the plot, defaults to None
        :type fig_path: str, optional
        """
        fig, axs = self._create_subplots(len(self.plots), self.width, self.height, self.dpi, self.plots)

        for plot_type, ax in axs.items():
            data, kwargs = plot_data.get(plot_type, (None, {}))
            self.plot(ax, data, plot_type, **kwargs)
        
        self.make_plot(fig, fig_path=fig_path)
        plt.close(fig)

        

    def animate_plots(self, plot_data, times, fig_path=None, fps=24):
        """
        Generate an animation from the provided plot data.

        :param plot_data: Dictionary containing data for different plot types
        :type plot_data: dict
        :param times: List of time points for animation frames
        :type times: list
        :param fps: Frames per second for the animation, defaults to 24
        :type fps: int, optional
        """
        for i, time in enumerate(times):
            new_plot_data = {}
            for plot_type, (data, kwargs) in plot_data.items():
                if plot_type != Plots.IPP_POLAR and plot_type != Plots.IPP_MERCATOR:
                    kwargs['time'] = time
                    data = data[time] if plot_type == Plots.MAP2D or plot_type == Plots.GIM else data
                    # print(data)
                new_plot_data[plot_type]=([data, kwargs])
            self.draw_plots(new_plot_data, fig_path=f"frame_{i}.png")
        path = fig_path if fig_path is not None else ""     
        with imageio.get_writer(path+'/animation.gif', mode='I', fps=fps, loop=True) as writer:
            for i in range(len(times)):
                filename = f"tmp/frame_{i}.png"
                image = imageio.imread(filename)
                writer.append_data(image)
                os.remove(filename)



