#!/bin/bash
#
# @Author: Anne Philipp
#
# @Date: June, 7 2018
#
# @Description: Makes a tarball for installation
#

tarname='flex_extract_v7.1.tar.gz'
path='/nas/tmc/Anne/Interpolation/flexextract/flexextract/python/../'

tar -cvf $tarname ${path}python/*py ${path}python/CONTROL* ${path}python/*ksh ${path}python/*temp ${path}python/ECMWF_ENV ${path}python/*json ${path}grib_templates ${path}src/*.f ${path}src/*.f90 ${path}src/*.h ${path}src/Makefile*  


