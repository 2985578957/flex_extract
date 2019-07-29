================
The CONTROL file
================
    
  

.. MARS user documentation				https://confluence.ecmwf.int/display/UDOC/MARS+user+documentation
.. MARS keywords and explanation				https://confluence.ecmwf.int/display/UDOC/MARS+keywords
 
 
This file is an input file for :literal:`flex_extract's` main script :literal:`submit.py`.
It contains the controlling parameters :literal:`flex_extract` needs to decide on dataset specifications,
handling of the retrieved data and general bahaviour. The naming convention is usually (but not necessary):

   :literal:`CONTROL_<Dataset>[.optionalIndications]`

The tested datasets are the operational dataset and the re-analysis datasets CERA-20C, ERA5 and ERA-Interim.
The optional extra indications for the re-analysis datasets mark the files for *public users* 
and *global* domain. For the operational datasets (*OD*) the file names contain also information of
the stream, the field type for forecasts, the method for extracting the vertical coordinate and other things like time or horizontal resolution.


Format of CONTROL files
----------------------------------
The first string of each line is the parameter name, the following string(s) (separated by spaces) is (are) the parameter values.
The parameters can be sorted in any order with one parameter per line. 
Comments are started with a '#' - sign. Some of these parameters can be overruled by the command line
parameters given to the :literal:`submit.py` script. 
All parameters have default values. Only those parameters which have to be changed
must be listed in the :literal:`CONTROL` files. 


Example CONTROL files
--------------------------------

A number of example files can be found in the directory :literal:`flex_extract_vX.X/run/control/`.
They can be used as a template for adaptations and understand what's possible to 
retrieve from ECMWF's archive.
For each main dataset there is an example and additionally some variances in resolution, type of field or type of retrieving the vertical coordinate. 


 
 
CONTROL file
------------
The file :literal:`CONTROL.documentation` documents the available parameters
in grouped sections with their default values. In :doc:`control_params` you can find a more
detailed description with additional hints, possible values and some useful information about
the setting of these parameters.

.. literalinclude:: ../../../../../Run/Control/CONTROL.documentation 
   :language: bash
   :caption: CONTROL.documentation
    



    
.. toctree::
    :hidden:
    :maxdepth: 2
    
