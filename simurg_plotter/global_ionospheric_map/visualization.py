from geo_mag_processing import prepare_contours, gims_limits
from geo_mag_processing import get_uniform_mag_net
from geo_mag_processing import get_gm_contours

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Optional

WITH_MAP = -1  # this needed because of imshow()

font = {'family': 'sans-serif',
        "sans-serif": "DejaVu Sans",
        'size': 14}

matplotlib.rc('font', **font)

def plot(gims: List[np.ndarray], fig_path: Optional[List[str]] = [], geo: bool = True, **kwargs: Optional[dict]):
    """Plot Geo-Magnetic maps.

    :param gims: List of maps to plot
    :type gims: List[np.ndarray]
    :param fig_path: List of paths to save figures, defaults to []
    :type fig_path: Optional[List[str]], optional
    :param geo: Indicates whether the maps are in geo format, defaults to True
    :type geo: bool, optional
    :param **kwargs: Additional keyword arguments:
        - width: Width of the figure in pixels, defaults to 3000
        - height: Height of the figure in pixels, defaults to 1500
        - dpi: Dots per inch of the figure, defaults to 300
        - gm_contours: Geo-magnetic contours, defaults to get_gm_contours()
        - only_contours: Flag to plot only contours, defaults to False
        - titles: List of titles for each map, defaults to None
        - cmin: Minimum color value for plot, defaults to None
        - cmax: Maximum color value for plot, defaults to None
        - vmin: Minimum value for color limit, defaults to None
        - vmax: Maximum value for color limit, defaults to None
    :type **kwargs: Optional[dict]
    """
    if len(fig_path) != 0 and len(gims) != len(fig_path):
        msg = f'Path to figures must be provide for each of {len(gims)} maps'
        raise ValueError(msg)
    width = kwargs.get('width', 3000)
    height = kwargs.get('width', 1500)
    dpi = kwargs.get('dpi', 300)
    lonlat = prepare_contours(geo, kwargs.get('gm_contours', get_gm_contours()))
    mag_geo_net = get_uniform_mag_net()
    lims = gims_limits(gims)
    for igim, arr in enumerate(gims):
        fig = plt.figure(figsize=(width/dpi, height/dpi), dpi=dpi)
        plot_ax = fig.add_subplot(111)
        plot_ax.plot(lonlat[:, 0], lonlat[:, 1], color='black', alpha=0.5)
        im = None
        if WITH_MAP == -1:
            if kwargs.get('only_contours', False) == True:
                arr[:, :] = None
            if arr.shape[1] % 2 != 0:
                im = plot_ax.imshow(arr, aspect=0.5)
            else:
                arr1 = np.zeros((arr.shape[0], arr.shape[1] + 1))
                arr1[:, : arr1.shape[1] - 1] = arr
                arr1[:, -1] = arr[:, 0]
                im = plot_ax.imshow(arr1, aspect=0.5)
        if 'titles' in kwargs:
            if len(kwargs['titles']) < igim:
                pass
            else:
                fig.suptitle(kwargs['titles'][igim])
        else:
            plot_ax.axis('off')
        fig.tight_layout()
        yt = [0] + list(range(5, 70, 6)) + [70]
        yl = [87.5] + list(range(75, -76, -15)) + [-87.5]
        xt = [0] + list(range(6, 72, 6)) + [72]
        xl = [-180] + list(range(-150, 151, 30)) + [180]
        plot_ax.set_yticks(yt)
        plot_ax.set_yticklabels(yl)
        plot_ax.set_xticks(xt)
        plot_ax.set_xticklabels(xl)
        if im:
            im.set_clim(vmin=lims[0], vmax=lims[1])
        fig.colorbar(im, label='TEC, TECu', fraction=0.07, pad=0.035)
        if 'cmin' in kwargs and 'cmax'in kwargs:
            plot_ax.set_clim(kwargs['cmin'], kwargs['cmax'])
        if 'vmin' in kwargs and 'vmax' in kwargs:
            plot_ax.set_clim(vmin=kwargs['vmin'], vmax=kwargs['vmax'])
        if len(fig_path) != len(gims):
            mng = plt.get_current_fig_manager()
            mng.full_screen_toggle()
            plt.show()
        else:
            fig.savefig(fig_path[igim])
            plt.close(fig)