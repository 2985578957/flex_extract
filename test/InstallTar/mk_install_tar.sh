#!/bin/bash
#
# @Author: Anne Philipp
#
# @Date: November, 10 2018
#
# @Description: Makes a tar-ball for installation
#

# path to flex_extract base directory
path=../../

tarname='flex_extract_v7.1_local.tar'

tar -cvf ../../test/InstallTar/$tarname \
        ${path}source/python/classes/*py \
        ${path}source/python/mods/*py \
        ${path}source/python/*py \
        ${path}source/pythontest/*py \
        ${path}source/fortran/*.f \
        ${path}source/fortran/*.f90 \
        ${path}source/fortran/*.h \
        ${path}source/fortran/Makefile* \
        ${path}templates/convert.nl \
        ${path}templates/*.temp \
        ${path}templates/ecmwf_grib1_table_128 \
        ${path}run/run_local.sh \
        ${path}run/control/CONTROL* \
        ${path}run/jobscripts \
        ${path}LICENSE.md \
        ${path}CODE_OF_CONDUCT.md \
        ${path}README.md  \
        --exclude=*.ksh
                  
                  
                  
tarname='flex_extract_v7.1_ecgate.tar'

tar -cvf ../../test/InstallTar/$tarname \
        ${path}source/python/classes/*py \
        ${path}source/python/mods/*py \
        ${path}source/python/*py \
        ${path}source/pythontest/*py \
        ${path}source/fortran/*.f \
        ${path}source/fortran/*.f90 \
        ${path}source/fortran/*.h \
        ${path}source/fortran/Makefile* \
        ${path}templates/convert.nl \
        ${path}templates/*.temp \
        ${path}templates/ecmwf_grib1_table_128 \
        ${path}run/ECMWF_ENV \
        ${path}run/run.sh \
        ${path}run/control/CONTROL* \
        ${path}run/jobscripts \
        ${path}LICENSE.md \
        ${path}CODE_OF_CONDUCT.md \
        ${path}README.md \
        --exclude=*.ksh
                  
                 
                  
                  
                  
                  