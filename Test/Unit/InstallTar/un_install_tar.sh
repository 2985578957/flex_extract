#!/bin/bash
#
# @Author: Anne Philipp
#
# @Date: November, 10 2018
#
# @Description: Untar a tar-ball for installation
#

tarname='flex_extract_v7.1_local.tar'
dirname='flex_extract_v7.1_local'
path=../../test/Unit/InstallTar/
mkdir $path$dirname
cd $path$dirname
tar xvf ../$tarname 
cd ../../../../source/pythontest

tarname='flex_extract_v7.1_ecgate.tar'
dirname='flex_extract_v7.1_ecgate'
path=../../test/Unit/InstallTar/
mkdir $path$dirname
cd $path$dirname
tar xvf ../$tarname 
cd ../../../../source/pythontest