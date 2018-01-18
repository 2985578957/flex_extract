#!/bin/bash

# script to prepare CTBTO environment for
# ECMWFDATA7.0
# 
# Leo Haimberger 1.3.2016

export PATH=/dvl/atm/klinkl/software/local/bin:$PATH
export PYTHONPATH=/dvl/atm/klinkl/software/local/lib/python2.7/site-packages/grib_api
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/dvl/atm/klinkl/software/local/lib/
export GRIB_API_INCLUDE_DIR=/dvl/atm/klinkl/software/local/include/
export GRIB_API_LIB='-L/dvl/atm/klinkl/software/local/lib -Bstatic  -lgrib_api_f77 -lgrib_api_f90 -lgrib_api -lemosR64 -Bdynamic  -lm  -ljasper'
