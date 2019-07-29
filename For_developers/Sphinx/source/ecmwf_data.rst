**********
ECMWF Data
**********
    
.. _ECMWF: http://www.ecmwf.int
.. _Member States: https://www.ecmwf.int/en/about/who-we-are/member-states


The European Centre for Medium-Range Weather Forecasts (`ECMWF`_), based in Reading, UK, is an independent intergovernmental organisation supported by 34 states. It is both a research institute and a full time operational service. It produces global numerical weather predictions and some other data which is fully available to the national meteorological services in the `Member States`_, Co-operating States and the broader community. Especially, the published re-analysis datasets are made available to the public with some limits in specific datasets.

The amount and structure of the available data from ECMWF is very complex. The operational data changes regularly in time and spatial resolution, physics and parameter. This has to be taken into account carefully and each user has to investigate his dataset of interest carefully before selecting and retrieving it with ``flex_extract``.
The re-analysis datasets are consistent in all the above mentioned topics over their whole period but they have each their own specialities which makes treatment with ``flex_extract`` special in some way. For example, they have different starting times for their forecasts or different parameter availability. They also have differences in time and spatial resolution and most importantly for ``flex_extract`` they are different in the way of providing the vertical coordinate. 

There is much to learn from ECMWF and their datasets and data handling and this might be confusing at first. We therefore collected the most important information for ``flex_extract`` users. In the following sections the user can use them to get to know enough to understand how ``flex_extract`` is best used and to select the parameters of the ``CONTROL`` files. 


:doc:`Ecmwf/access`
    Description of available access methods to the ECMWF data.

:doc:`Ecmwf/msdata`
    Information about available data and parameters for member state users which can be retrieved with ``flex_extract``

:doc:`Ecmwf/pubdata`
    Information about available data and parameters for the public datasets which can be retrieved with ``flex_extract``

:doc:`Ecmwf/hintsecmwf`
    Collection of hints to best find information to define the dataset for retrievement and
    to define the ``CONTROL`` files.

:doc:`Ecmwf/ec-links`
    Link collection for additional and useful information as well as references to specific dataset publications.


.. toctree::
    :hidden:
    :maxdepth: 2

    Ecmwf/access
    Ecmwf/msdata
    Ecmwf/pubdata
    Ecmwf/hintsecmwf
    Ecmwf/ec-links
    
