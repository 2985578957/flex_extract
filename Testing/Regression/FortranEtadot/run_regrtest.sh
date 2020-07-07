#!/bin/bash

# Do the regression tests
# can be called without arguments, then will test all cases
# or with argument "omithigh" then high-resolution cases are omitted

# Copyright Petra Seibert, 2019
# SPDX-License-Identifier: MIT-0 

export OMP_NUM_THREADS=4 # you may want to change this
export OMP_PLACES=cores
export OMP_DISPLAY_ENV=verbose
testhome=`pwd`
path1=../../../Source/Fortran/
path=../${path1}
exedebug=calc_etadot_debug.out
exefast=calc_etadot_fast.out
hash=$(git log --abbrev-commit --pretty=oneline -n 1  --pretty=format:'%h')
csvfile='runtimes_'${HOST}'.csv'
exitonfail=true
numtest=0
numpassed=0

rm -f log.run_regr failed

# loop over all reference runs

if [ "$1" = omithigh ]; then # for fast testing, not for production
  inputs=`ls Inputs |  grep -v high`
else
  inputs=`ls Inputs |grep etadothigh`
fi
for ref in $inputs; do

  echo 'Working on test case =' $ref | tee -a ../log.run_regr

  # loop over debug and fast runs
  for exe in 'debug' 'fast'; do
  
    numtest=$((numtest + 1))
    failed=false

    rm -f Work/* # make shure that Work is empty
    cd Work
    echo '  Run code version "'${exe}'"' | tee -a ../log.run_regr

    thisexe=calc_etadot_${exe}.out
    ln ../Inputs/${ref}/fort.* .
    ( time ${path}${thisexe} ) >& log
    
    # check whether runs completeted properly
    grep -q CONGRATULATIONS log
    if [ $? = "0" ]; then
      echo '    CONGRATULATIONS found' | tee -a ../log.run_regr
    else
      echo '    missing CONGRATULATIONS. Test failed.' | tee -a ../log.run_regr
      echo $ref $exe 'FAILED' >> ${testhome}/failed
      if [ "${exitonfail}" = true ]; then exit; else failed=true; fi
    fi
    for outfile in 'fort.15' 'VERTICAL.EC'; do
      if [ -e $outfile ]; then
        # compare reference and current version
        # omega case also produces fort.25 - need to add this
        outref='../Outputs/Output_ref_'${ref}'_'${exe}'/'$outfile
        if cmp -s $outfile $outref >/dev/null; then
          echo '    '$outfile '    test passed' | tee -a ../log.run_regr
        else
          echo 'WARNING:' $outfile '     test failed' | tee -a ../log.run_regr
          echo $ref $exe 'FAILED' >> ${testhome}/failed
          if [ "${exitonfail}" = true ]; then exit; else failed=true; fi
        fi

      else
        echo '    missing '${outfile}' Test failed.' | tee -a ../log.run_regr
        echo $ref $exe 'FAILED' >> ${testhome}/failed
        if [ "${exitonfail}" = true ]; then exit; else failed=true; fi
      fi
    done # end loop outfiles
    if [ "${failed}" = false ]; then numpassed=$((numpassed + 1)); fi

  # save and show runtimes
    log='log'
    times=$(tail -3 ${log})
    real=$(echo $times | grep real | awk '{print $2}')
    user=$(echo $times | grep user | awk '{print $4}')
    sys=$( echo $times | grep sys  | awk '{print $6}')
    echo $hash, "'"reference"'", "'"${ref}'_'${exe}"'", ${real}, ${user}, ${sys} >> ../${csvfile}
    tail -1 ../${csvfile} >> log.run_regr

    cd ..
    rm -f Work/* # this is for being more safe

  done # end of exe loop
  
  echo # go to next reference run
done # end of ref loop

echo  
echo ' Regression test: ' $numpassed 'out of' $numtest 'tests passed'. \
  | tee -a ../log.run_regr
echo ' More information may be found in log.run_regr' 
echo ' Runtimes were added to '${csvfile}' under '$hash | tee -a ../log.run_regr

# the following code is executed only if exitonfail is not set to 'true'.
if [ -e failed ]; then 
  echo
  echo Some tests failed, see file "failed":
  echo
  cat failed|sort -u
fi
