#!/bin/bash
#
# @Author: Anne Philipp
#
# @Date: March, 1 2019
#
# @Description: Makes a tarball for uploading and distributing on flexpart.eu
#
# @Licence: 
#    (C) Copyright 2014-2019.
#
#    SPDX-License-Identifier: CC-BY-4.0
#
#    This work is licensed under the Creative Commons Attribution 4.0
#    International License. To view a copy of this license, visit
#    http://creativecommons.org/licenses/by/4.0/ or send a letter to
#    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

tarname='flex_extract_v7.1.2.tar.gz'
tardir='flex_extract_v7.1.2'

# go back to directory which is above flex_extract directory
cd ../.. 

# create tar-ball
tar -zcvf $tarname $tardir\
    --exclude=$tardir'/Source/Fortran/*.o' \
    --exclude=$tardir'/Source/Fortran/*.mod' \
    --exclude=$tardir'/Source/Fortran/calc_etadot' \
    --exclude=$tardir'/Source/Python/*.pyc' \
    --exclude=$tardir'/Source/Pythontest/*.pyc' \
    --exclude=$tardir'/Source/Pythontest/__pycache__' \
    --exclude=$tardir'/Source/Pythontest/.pytest_cache' \
    --exclude=$tardir'/.git' \
    --exclude=$tardir'/.gitignore' \
    --exclude=$tardir'/Run/ECMWF_ENV' \
    --exclude=$tardir'/Run/Workspace' \
    --exclude=$tardir'/Run/Jobscripts/*sh' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.0.4/BASETIME' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.0.4/CERA' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.0.4/EA5' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.0.4/EI' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.0.4/ETAOD' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.0.4/GAUSSOD' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.0.4/PUREFC' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.1/BASETIME' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.1/CERA' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.1/EA5' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.1/EI' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.1/ETAOD' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.1/GAUSSOD' \
    --exclude=$tardir'/Testing/Regression/Compare_gribfiles/7.1/PUREFC' \
    --exclude=$tardir'/setup_local.sh' \
    --exclude=$tardir'/.empty' \
    
     
