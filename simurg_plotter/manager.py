import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import cartopy.crs as ccrs
from mpl_toolkits.axes_grid1 import make_axes_locatable
from PIL import Image
import imageio.v2 as imageio
from enum import Enum
import tempfile
import os

# Импорт дополнительных модулей
from .global_ionospheric_map.visualization import plot as gim_plot
from .ionospheric_pierce_point.visualization import mercator_plot, polar_plot
from .map2d.map2d import plot_map
from .disturbance_storm_time.dst import plot_dst

DEFAULT_PARAMS = {
    'font.size': 20,
    'figure.dpi': 300,
    'font.family': 'serif',
    'font.style': 'normal',
    'font.weight': 'light',
    'legend.frameon': True,
    'font.variant': 'small-caps',
    'axes.titlesize': 20,
    'axes.labelsize': 20,
    'xtick.labelsize': 18,
    'xtick.major.pad': 5,
    'ytick.major.pad': 5,
    'xtick.major.width': 2.5,
    'ytick.major.width': 2.5,
    'xtick.minor.width': 2.5,
    'ytick.minor.width': 2.5,
    'ytick.labelsize': 20,
}

plt.rcParams.update(DEFAULT_PARAMS)

class Plots(Enum):
    """Enum class defining different types of plots."""
    GIM = 'gim'
    IPP_MERCATOR = 'ipp_merc'
    IPP_POLAR = 'ipp_pol'
    MAP2D = 'map2d'
    DST = 'dst'

class PlotManager:
    def __init__(self, nrows=3, ncols=3, height=18, dpi=300):
        self.nrows = nrows
        self.ncols = ncols
        self.figsize = (18, height)
        self.fig = plt.figure(figsize=self.figsize, dpi=dpi)
        self.gs = GridSpec(nrows, ncols, figure=self.fig)
        self.gs.update(wspace=0.5, hspace=0.45)
        self.axes = {}
        # self.width = width
        # self.height = height

    def add_subplot(self, row, col, rowspan=1, colspan=1, projection=None, title=None):
        ax = plt.subplot(self.gs[row:row+rowspan, col:col+colspan], projection=projection)
        self.axes[(row, col)] = ax
        if title:
            ax.set_title(title)
        return ax

    def add_legend(self, ax, labels, colors):
        handles = [plt.Line2D([0], [0], color=color, lw=4) for color in colors]
        ax.legend(handles, labels, loc='best')

    def add_colorbar(self, mappable, ax, orientation='vertical', fraction=0.007, pad=0.0035):
        # Create a new axis for the colorbar
        if orientation == 'vertical':
            position = ax.get_position()
            cax = self.fig.add_axes([position.x1 + pad, position.y0, fraction, position.height])
        elif orientation == 'horizontal':
            position = ax.get_position()
            cax = self.fig.add_axes([position.x0, position.y0 - pad - fraction, position.width, fraction])
        cbar = self.fig.colorbar(mappable, cax=cax, orientation=orientation)
        return cbar

    def save(self, filename):
        self.fig.tight_layout()
        self.fig.savefig(filename, bbox_inches='tight')

    def show(self):
        self.fig.tight_layout()
        plt.show()

    def plot_map2d(self, row, col, data, colspan=1, title=None, **kwargs):
        ax = self.add_subplot(row, col, projection=ccrs.PlateCarree(), title=title, colspan=colspan)
        mappable = plot_map(ax, data, **kwargs)
        return ax, mappable

    def plot_dst(self, row, col, data, colspan=1, title=None, **kwargs):
        ax = self.add_subplot(row, col, title=title, colspan=colspan)
        ax.set_xlim(data[0, 0], data[-1, 0])
        plot_dst(ax, data, **kwargs)
        return ax, None

    def plot_gim(self, row, col, data, colspan=1, title=None, **kwargs):
        ax = self.add_subplot(row, col, projection=ccrs.PlateCarree(), colspan=colspan)
        mappable = gim_plot(data, ax=ax, title=title, **kwargs)
        return ax, mappable

    def plot_ipp_merc(self, row, col, data, colspan=1, title=None, **kwargs):
        ax = self.add_subplot(row, col, projection=ccrs.Mercator(), title=title, colspan=colspan)
        mercator_plot(data, ax=ax, **kwargs)
        return ax, None

    def plot_ipp_pol(self, row, col, data, colspan=1, title=None, **kwargs):
        ax = self.add_subplot(row, col, projection='polar', title=title, colspan=colspan)
        polar_plot(data, ax=ax, **kwargs)
        return ax, None

    def animate_plots(self, plot_data, times, file_name="animation.gif", fig_path=None, fps=24):
        for i, time in enumerate(times):
            new_plot_data = {}
            for plot_type, (data, kwargs) in plot_data.items():
                if plot_type != Plots.IPP_POLAR and plot_type != Plots.IPP_MERCATOR:
                    kwargs['time'] = time
                    data = data[time] if plot_type == Plots.MAP2D or plot_type == Plots.GIM else data
                new_plot_data[plot_type] = (data, kwargs)
            self.draw_plots(new_plot_data, fig_path=f"{tempfile.gettempdir()}/frame_{i}.png")
        path = fig_path if fig_path is not None else "/"
        with imageio.get_writer(tempfile.gettempdir() + '/animation.gif', mode='I', fps=fps) as writer:
            for i in range(len(times)):
                filename = f"{tempfile.gettempdir()}/frame_{i}.png"
                image = imageio.imread(filename)
                writer.append_data(image)
                os.remove(filename)
        with Image.open(tempfile.gettempdir() + '/animation.gif') as im:
            im.info['loop'] = 0
            im.save(f"{path}{file_name}", 'GIF', save_all=True, dither="None")