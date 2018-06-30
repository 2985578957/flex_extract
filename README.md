# README #

This software retrieves ECMWF data and generates FLEXPART specific data files. 
For each time stamp the software combines all model level and surface level 
data fields which were modified to match FLEXPART's needs and were then 
stored in single files with the format prefixYYMMDDHH.


This directory contains the following sub-directories:

+ `python: It contains the python scripts which manage the extraction and 
           the generation of FLEXPART input data files. It also includes the 
           CONTROL files which contain the controlling parameters.
+ `src:    It contains the Fortran source code and Makefile templates 
           to create the CONVERT2 executable (used by the python scripts) to
           process the ECMWF grib fields, e.g. convert from reduced gaussian to 
           regular latitude-longitude grid.
+ `grib_templates: It contains a reference table for the ECMWF parameter.


For more detailed installation instructions and the user guide please read 
SIP.pdf and SUT.pdf.

Please report any problems via the ticket system at www.flexpart.eu.

