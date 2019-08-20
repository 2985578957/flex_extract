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

tarname='flex_extract_v7.1.tar.gz'
tardir='flex_extract_v7.1'

# go back to directory which is above flex_extract directory
cd ../.. 

# create tar-ball
tar -zcvf $tarname $tardir\
    --exclude=$tardir'/Source/Fortran/*.o' \
    --exclude=$tardir'/Source/Fortran/*.mod' \
    --exclude=$tardir'/Source/Fortran/CONVERT2*' \
    --exclude=$tardir'/Source/Python/*.pyc' \
    --exclude=$tardir'/Source/Pythontest/*.pyc' \
    --exclude=$tardir'/Source/Pythontest/__pycache__' \
    --exclude=$tardir'/Source/Pythontest/.pytest_cache' \
    --exclude=$tardir'/.git' \
    --exclude=$tardir'/.gitignore' \
    --exclude=$tardir'/Run/ECMWF_ENV' \
    --exclude=$tardir'/Run/Workspace' \
    --exclude=$tardir'/Run/Jobscripts/*' \
    --exclude=$tardir'/Testing/Testcases' \
    --exclude=$tardir'/Testing/Controls' \
    --exclude=$tardir'/Testing/Dir' \
    --exclude=$tardir'/Run/fontconfig' \
    --exclude=$tardir'/Run/run_local.sh' \
    --exclude=$tardir'/Run/Control/Testgrid' \
    --exclude=$tardir'/Run/Control/notPublic' \
    --exclude=$tardir'setup_local.sh' \
    --exclude=$tardir'/.empty' \
    
     
