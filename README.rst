SIMuRG plotter
==============

The collection of the tools to bild global and regional distribution of any 
parameter that can be plotted over the globe (latitude-longitude section) 
or versus height (for example latitude-height and latitude-height section).
The plots include important features such as terminator line, subsolar point,
geomagnetic equator etc.

Features
--------

* Global data plot

.. |Global map with sparse data| image:: docs/img/global_sparse.png
    :width: 600

* Global map plot

.. |Global map on regular grid| image:: docs/img/global_regular.png
    :width: 600

* Regional data plot

.. |Regional map with sparse data| image:: docs/img/regional_sparse.png
    :width: 600

* Distance-time plot (under development)

.. |Distance time plot| image:: docs/img/distance_time.png
    :width: 600

* Round Earth projection (under development)    
* Animation plots (under development)

Installation
------------

Make virtual environment with conda (optional):

    conda create -n simurg_plotter python=3.10
    conda deactivate
    conda activate simurg_plotter

Install `poetry`:

    pip install poetry

Install project:

    poetry install

Support
-------

If you are having issues, please let us know.
We have a mailing list located at: artemvesnin@gmail.com

License
-------

The project is licensed under the MIT license.
