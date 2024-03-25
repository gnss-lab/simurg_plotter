import numpy as np
from dataclasses import dataclass

@dataclass
class Series:
    """
    Represents a series of data related to satellite observations.

    :param site_lat: Latitude of the observation site.
    :type site_lat: float
    :param site_lon: Longitude of the observation site.
    :type site_lon: float
    :param sip_lon: Array of SIP (Slant Ionospheric Pierce) longitudes.
    :type sip_lon: numpy.ndarray
    :param sip_lat: Array of SIP (Slant Ionospheric Pierce) latitudes.
    :type sip_lat: numpy.ndarray
    :param sip_larc: Array of SIP (Slant Ionospheric Pierce) larc distances.
    :type sip_larc: numpy.ndarray
    :param elevation: Array of elevation angles.
    :type elevation: numpy.ndarray
    :param azimuth: Array of azimuth angles.
    :type azimuth: numpy.ndarray
    :param sat_name: Name of the satellite.
    :type sat_name: str
    """
    site_lat: float
    site_lon: float
    sip_lon: np.ndarray
    sip_lat: np.ndarray
    sip_larc: np.ndarray
    elevation: np.ndarray
    azimuth: np.ndarray
    sat_name: str

    def __init__(self, serie_list):
        """
        Initializes a Series object from a list of attributes.

        :param serie_list: List containing attributes in the order:
            site_lat (float): Latitude of the observation site.
            site_lon (float): Longitude of the observation site.
            sip_lon (numpy.ndarray): Array of SIP (Slant Ionospheric Pierce) longitudes.
            sip_lat (numpy.ndarray): Array of SIP (Slant Ionospheric Pierce) latitudes.
            sip_larc (numpy.ndarray): Array of SIP (Slant Ionospheric Pierce) larc distances.
            elevation (numpy.ndarray): Array of elevation angles.
            azimuth (numpy.ndarray): Array of azimuth angles.
            sat_name (str): Name of the satellite.
        :type serie_list: list
        """
        self.site_lat = serie_list[0]
        self.site_lon = serie_list[1]
        self.sip_lat = serie_list[2]
        self.sip_lon = serie_list[3]
        self.sip_larc = serie_list[4]
        self.elevation = serie_list[5]
        self.azimuth = serie_list[6]
        self.sat_name = serie_list[7]
    
    def __str__(self):
        """
        Returns a string representation of the Series object.

        :return: String representation of the Series object.
        :rtype: str
        """
        return f"Series Object:\n" \
               f"Site Latitude: {self.site_lat}\n" \
               f"Site Longitude: {self.site_lon}\n" \
               f"SIP Longitude: {self.sip_lon}\n" \
               f"SIP Latitude: {self.sip_lat}\n" \
               f"SIP Larc: {self.sip_larc}\n" \
               f"Elevation: {self.elevation}\n" \
               f"Azimuth: {self.azimuth}\n" \
               f"Satellite Name: {self.sat_name}"
