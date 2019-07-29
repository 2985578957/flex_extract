#!/bin/bash
#
# @Author: Anne Philipp
#
# @Date: June, 7 2018
#
# @Description: Makes a tarball for uploading on flexpart.eu
#

tarname='flex_extract_v7.1.tar.gz'


tar --exclude='./src/*.o' --exclude='./src/*.mod' --exclude='./src/CONVERT2' --exclude='./python/*.pyc' --exclude='./python/*.ksh' --exclude='./python/ECMWF_ENV' --exclude='./python/*sh' --exclude='*sh' --exclude='*tar.gz' --exclude='work' --exclude='./python/job.temp' -zcvf $tarname . 
