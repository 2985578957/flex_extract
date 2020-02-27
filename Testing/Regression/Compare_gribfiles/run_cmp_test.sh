#!/bin/bash
#
# @Author: Anne Philipp
#
# @Date: November, 20 2019
#
# @Description: Starts the comparison script for all cases found in the new 
#               version directory. Results are written to a log file placed
#               in the Log directory.
#
# @Call command:  ./run_cmp_test.sh <reference version> <new version>
#    
# @ChangeHistory: 
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
# @Example: 
#         ./run_cmp_test.sh 7.0.4 7.1
#

if [ $# -eq 0 ]; then
  echo "No arguments passed"
  exit
fi

if [ $# -eq 1 ]; then
  echo "Second argument is missing"
  exit
fi

old_version=$1
new_version=$2

current_time=$(date "+%Y-%m-%d_%H-%M-%S")
testcases=`ls ${new_version}/`

echo 'Test to compare GRIB files between two versions'
echo 'Compare GRIB files between version ' + old_version + ' and version ' + new_version + ' : \n' > Log/log_$current_time

for case in $testcases; do

  if [[ "$case" == "Controls" ]]; then 
    continue
  fi 
  echo "Compare $case ..."
  python test_cmp_grib_file.py -r 7.0.4/${case}/ -n 7.1/${case}/ -p '*' >> Log/log_$current_time 2>&1

  echo "===================================================================================================" >> Log/log_$current_time

done

