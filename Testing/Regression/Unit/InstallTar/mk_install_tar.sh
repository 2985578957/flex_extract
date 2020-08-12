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

tarname='flex_extract_v7.1.2_local.tar'
pwd
tar -zcvf ../../Testing/Regression/Unit/InstallTar/$tarname  \
        ${path}Source/Python/Classes/*py \
        ${path}Source/Python/Mods/*py \
        ${path}Source/Python/*py \
        ${path}Source/Pythontest/*py \
        ${path}Source/Fortran/*.f90 \
        ${path}Source/Fortran/*.h \
        ${path}Source/Fortran/makefile* \
        ${path}Templates/* \
        ${path}Run/run_local.sh \
        ${path}Run/Control/CONTROL* \
        ${path}Run/Jobscripts/*.md \
        ${path}*.md \
        ${path}Testing/Installation/*.sh \
        ${path}Testing/Installation/Api_testscripts/* \
        ${path}Testing/Installation/Calc_etadot/* \
        ${path}Testing/Installation/First_extraction/* \
        --exclude=*.ksh  \
        --exclude=flex_extract_v7.1_*.tar

tarname='flex_extract_v7.1.2_ecgate.tar'

tar -zcvf ../../Testing/Regression/Unit/InstallTar/$tarname \
        ${path}Source/Python/Classes/*py \
        ${path}Source/Python/Mods/*py \
        ${path}Source/Python/*py \
        ${path}Source/Pythontest/*py \
        ${path}Source/Fortran/*.f90 \
        ${path}Source/Fortran/*.h \
        ${path}Source/Fortran/makefile* \
        ${path}Templates/* \
        ${path}Run/ECMWF_ENV \
        ${path}Run/run.sh \
        ${path}Run/Control/CONTROL* \
        ${path}Run/Jobscripts/*.md \
        ${path}LICENSE.md \
        ${path}CODE_OF_CONDUCT.md \
        ${path}README.md \
        ${path}Testing/Installation/*.sh \
        ${path}Testing/Installation/Api_testscripts/* \
        ${path}Testing/Installation/Calc_etadot/* \
        ${path}Testing/Installation/First_extraction/* \
        --exclude=*.ksh  \
        --exclude=flex_extract_v7.1_*.tar
