#!/bin/bash
#
# @Author: Anne Philipp
#
# @Date: June, 21 2020
#
# @Description: Makes a tarball for uploading on flexpart.eu
#

tarname='flex_extract_v7.1.2.tar.gz'

tar -zcvf ${tarname} flex_extract --exclude=flex_extract/.git --exclude=flex_extract/.gitignore

