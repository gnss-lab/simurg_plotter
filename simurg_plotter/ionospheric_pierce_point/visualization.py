import numpy as np
import matplotlib.pyplot as plt
import matplotlib

__dim = 16

font = {'family': 'sans-serif',
        "sans-serif": "DejaVu Sans",
        'size': 14}

matplotlib.rc('font', **font)


def mercator_plot(series, filename=None, elevation_cutoff=0,
                  width=1600, height=1200, dpi=100):
    fig, ax = plt.subplots(figsize=(width/dpi, height/dpi), dpi=dpi)
    lines = []
    ser = series[0]
    ax.plot(np.rad2deg(ser.site.lon), np.rad2deg(ser.site.lat), 's',
            label='Site')
    for ser in series:
        if 'sip_lon' not in ser.fields or 'sip_lat' not in ser.fields:
            ser.calc_pierce_point()
        inds = np.where(ser['elevation'] > np.deg2rad(elevation_cutoff))
        lines.append(None)
        lines[-1], = ax.plot(ser['sip_lon'][inds], ser['sip_lat'][inds], 'o',
                             label=ser.sat.name)

    ax.set_xlabel('Longitude, degrees')
    ax.set_ylabel('Latitude, degrees')
    fig.suptitle('Sounding geometry (Latitude vs Longitude)')
    ax.minorticks_on()
    ax.xaxis.grid(which='minor', alpha=0.2)
    ax.xaxis.grid(which='major', alpha=0.5)
    ax.legend(bbox_to_anchor=(1.12, 1.0))
    if filename is None:
        plt.show()
    else:
        fig.savefig(filename)
        plt.close(fig)


def polar_plot(series, filename=None, elevation_cutoff=0,
               radius=1600, dpi=100):
    fig = plt.figure(figsize=(radius/dpi+1, radius/dpi), dpi=dpi)
    ax = fig.add_subplot(111, projection='polar')
    lines = []
    p = ax.plot(0, 0, 's', label='Site')
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi/2.0)
    for ser in series:
        if 'sip_larc' not in ser.fields:
            ser.calc_pierce_larc()
        inds = np.where(ser['elevation'] > np.deg2rad(elevation_cutoff))
        azimuth = ser['azimuth'][inds]
        r = ser['sip_larc'][inds]
        lines.append(None)
        lines[-1], = ax.plot(azimuth, r, 'o', label=ser.sat.name)

    ax.set_xlabel('Azimuth, degrees')
    fig.suptitle('Sounding geometry (azimuth vs great_circle_distance)')
    ax.minorticks_on()
    ax.xaxis.grid(which='minor', alpha=0.2)
    ax.xaxis.grid(which='major', alpha=0.5)
    ax.legend(bbox_to_anchor=(1.15, 1.0))
    if filename is None:
        plt.show()
    else:
        fig.savefig(filename)
        plt.close(fig)
