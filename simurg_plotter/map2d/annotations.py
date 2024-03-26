import cartopy.crs as ccrs
import matplotlib.patches as patches

from cartopy import feature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from matplotlib.path import Path
import pickle
import os

def get_lats_and_parallels():
    path = os.path.join(
        os.path.dirname(__file__), "files/lats_and_parallels.pkl"
    )
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data[0], data[1]
 
def get_parallels_patch(lat_limit=20):
    lats, parallels = get_lats_and_parallels()
    _poly = []
    _codes = []
    for i, lat in enumerate(lats):
        if abs(lat) > lat_limit:
            continue
        # _line = eq.get_parallel(lat)
        _line = parallels[i] if lat in lats else None #need test
        path_codes = [Path.LINETO] * len(_line)
        path_codes[0] = Path.MOVETO
        path_codes[-1] = Path.MOVETO
        _codes.extend(path_codes)
        _poly.extend(_line)
    path = Path(_poly, _codes)
    return patches.PathPatch(path, facecolor="none", lw=1,
                             transform=ccrs.Geodetic())


def plot_terminator(ax, lat, lon, color="black", alpha=0.5):
    """
    Plot a fill on the dark side of the planet (without refraction).

    Parameters
    ----------
        ax: axes of matplotlib.plt
            of matplotlib.plt to plot on
        time : datetime
            The time to calculate terminator for. Defaults to datetime.utcnow()
    """
    # ss = SubSolar()
    # lat, lon = ss.get_latlon(time)
    pole_lng = lon
    if lat > 0:
        pole_lat = -90 + lat
        central_rot_lng = 180
    else:
        pole_lat = 90 + lat
        central_rot_lng = 0

    rotated_pole = ccrs.RotatedPole(pole_latitude=pole_lat,
                                    pole_longitude=pole_lng,
                                    central_rotated_longitude=central_rot_lng)

    x = [-90] * 181 + [90] * 181 + [-90]
    y = list(range(-90, 91)) + list(range(90, -91, -1)) + [-90]
    terminator = ax.fill(x, y, transform=rotated_pole,
                         color="black", alpha=0.1, zorder=3)[0]
    return terminator


def plot_gridlines(ax):
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=1, color='gray', alpha=0.5, linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER


def plot_geo_borders(ax):
    ax.coastlines()
    # ax.add_feature(feature.LAND)
    # ax.add_feature(cartopy.feature.OCEAN)
    ax.add_feature(feature.COASTLINE)
    ax.add_feature(feature.BORDERS, linestyle=':')
    ax.add_feature(feature.LAKES, alpha=0.5)
    ax.add_feature(feature.RIVERS)
