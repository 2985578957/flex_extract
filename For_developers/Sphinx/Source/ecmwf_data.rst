**********
ECMWF Data
**********
    
.. _ECMWF: http://www.ecmwf.int
.. _Member States: https://www.ecmwf.int/en/about/who-we-are/member-states


The European Centre for Medium-Range Weather Forecasts (`ECMWF`_), based in Reading, UK, is an independent intergovernmental organisation supported by 34 states. It is both a research institute and a 24 h / 7 d operational service. It produces global numerical weather predictions and some other data which are fully available to the national meteorological services in the `Member States`_, Co-operating States, and to some extend to the broader community. Specifically, re-analysis data sets are made available to the public, however, with some limitations for specific data sets.

There is vast amount and of data with a complex structure available from ECMWF. The operational data undergo changes with respect to temporal and spatial resolution, model physics and parameters available. This has to be taken into account carefully and every user should have a clear idea of the data set intended to be used before retrieving it with ``flex_extract``.
Each re-analysis data set is homogeneous with respect to resolution etc., but the different re-analyses alll have specific properties which requires a corresponding treatment with ``flex_extract``. For example, the starting times of the forecasts may be different, or the availability of parameters (model output variables) may vary. They also differ in their temporal and spatial resolution, and - most importantly for ``flex_extract`` - there are differences in the way how the vertical wind component may be accessed. 

As there is much to learn about ECMWF and its data sets and data handling, it might be confusing at first. Therefore, we have here collected the information which is most important for ``flex_extract`` users. Study the following sections to learn how ``flex_extract`` is best used, and to select the right parameters in the ``CONTROL`` files. 


:doc:`Ecmwf/access`
    Description of available  methods to access the ECMWF data.

:doc:`Ecmwf/msdata`
    Information about available data and parameters for member-state users which can be retrieved with ``flex_extract``

:doc:`Ecmwf/pubdata`
    Information about available data and parameters for the public data sets which can be retrieved with ``flex_extract``

:doc:`Ecmwf/hintsecmwf`
    Collection of hints to best find information to define the data set for retrieval, and
    to define the content of the ``CONTROL`` files.

:doc:`Ecmwf/ec-links`
    Link collection for additional and useful information as well as references to publications on specific data sets.


.. toctree::
    :hidden:
    :maxdepth: 2

    Ecmwf/access
    Ecmwf/msdata
    Ecmwf/pubdata
    Ecmwf/hintsecmwf
    Ecmwf/ec-links
    
