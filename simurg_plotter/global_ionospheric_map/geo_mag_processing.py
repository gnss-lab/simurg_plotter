import numpy as np
import os

MAX_DELTA = 5  # degrees
WITH_MAP = -1  # this needed because of imshow()

def get_uniform_mag_net():
    path = os.path.join(os.path.dirname(__file__), "files/mag_grid_geo_grid_2010.dat")
    return np.loadtxt(path)

def get_gm_contours():
    path = os.path.join(os.path.dirname(__file__), "files/geo_mag_contours.dat")
    return np.loadtxt(path)

def prepare_contours(geo, contours):
    gm_contours = contours
    if geo:
        _lons = (180 + gm_contours[:, 0]) / 5
        _lats = WITH_MAP*(WITH_MAP * 90 + gm_contours[:, 1]) / 2.5
        _lonslons = gm_contours[:, 0:2]
    else:
        _lons = (180 + gm_contours[:, 2]) / 5
        _lats = WITH_MAP * (WITH_MAP*90 + gm_contours[:, 3]) / 2.5
        _lonslons = gm_contours[:, 2:4]
    lonlat = np.zeros((len(gm_contours)*2, 2))
    num = 0
    last = 0
    for i in range(1, len(_lonslons[:, 0])):
        if (np.abs(_lonslons[i, 0] - _lonslons[i-1, 0]) > MAX_DELTA or
                np.abs(_lonslons[i, 1] - _lonslons[i-1, 1]) > MAX_DELTA):
            lonlat[last + num:i + num, 0] = _lons[last:i]
            lonlat[last + num:i + num, 1] = _lats[last:i]
            lonlat[i+num, 0:2] = None
            num += 1
            last = i
    return lonlat

def gims_limits(arrs):
    std = 0
    aver = 0
    sigma = 3
    for arr in arrs:
        std = max(np.std(arr), std)
        aver += np.average(arr)
    aver /= len(arrs)

    lims = [round(aver - sigma * std, 1), round(aver + sigma * std, 1)]
    lims[0] = max(0, lims[0])
    return lims