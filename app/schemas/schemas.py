from pydantic import BaseModel
from typing import List, Union

class PlotBase(BaseModel):
    row: int = 0
    col: int = 0
    plot_type: str
    data_file: str = "./data/dtec_2_10_2017_001_-90_90_N_-180_180_E_3d57.h5"
    title: str
    timestamp: str = "2017-01-01T00:00:00"
    rowspan: int = 1
    colspan: int = 1
    colorbar: bool = True

class Map2DPlot(PlotBase):
    plot_type: str = "map2d"
    product_type: str = "dtec_2_10"
    min_lat: float = -90
    max_lat: float = 90
    min_lon: float = -180
    max_lon: float = 180

class GIMPlot(PlotBase):
    plot_type: str = "gim"

class IPPMercatorPlot(PlotBase):
    plot_type: str = "ipp_mercator"

class IPPPolarPlot(PlotBase):
    plot_type: str = "ipp_polar"

class DSTPlot(PlotBase):
    plot_type: str = "dst"
    delimiter: str = ','

class PlotRequest(BaseModel):
    height: int = 9
    dpi: int = 300
    file_name: str = "test"
    nrows: int = 1
    ncols: int = 1
    plots: List[Union[Map2DPlot, GIMPlot, IPPMercatorPlot, IPPPolarPlot, DSTPlot]]

class TimeIntervalRequest(BaseModel):
    start_time: str = "2017-01-01T00:00:00"
    end_time: str = "2017-01-01T01:00:00"
    interval_seconds: int
    plot_request: PlotRequest

class MAP2DRequest(BaseModel):
    email: str
    date: str = "2017-01-01"
    url: str = None

class GIMRequest(BaseModel):
    date: str = "2017-01-01"
    gim_type: str = "uqrg"