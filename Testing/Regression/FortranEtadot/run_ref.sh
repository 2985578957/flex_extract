#!/bin/bash

# Do the reference runs and compare output of fast and debug

# Copyright Petra Seibert, 2019
# SPDX-License-Identifier: MIT-0 

export OMP_NUM_THREADS=4  # you may want to change this
export OMP_PLACES=sockets
testhome=`pwd`
path1=../../../Source/Fortran/
path=../${path1}
exedebug=calc_etadot_debug.out
exefast=calc_etadot_fast.out
hash=$(git log --abbrev-commit --pretty=oneline -n 1  --pretty=format:'%h')
csvfile='runtimes_'${HOST}'.csv'
exitonfail=true
rm -f log.run_ref failed

# loop over all reference runs
rm -f log.run_ref
rm -f Work/*

if [ "$1" = omithigh ]; then # for fast testing, not for production
                             # requires > 16 GB 
  inputs=`ls Inputs |  grep -v high`
else
  inputs=`ls Inputs`
fi
for ref in $inputs; do

  echo 'Working on test case =' $ref

  # loop over debug and fast runs
  for exe in 'debug' 'fast'; do

    cd Work
    echo '  Run code version "'${exe}'"'

    thisexe=calc_etadot_${exe}.out
    ln ../Inputs/${ref}/fort.* .
    ( time ${path}${thisexe} ) >& log
    
    # check whether runs completeted properly
    outdir='Outputs/Output_ref_'${ref}'_'${exe}
    grep -q CONGRATULATIONS log
    if [ $? = "0" ]; then
      echo '    CONGRATULATIONS found' >> ../log.run_ref
      mv log ../${outdir}
    else
      echo '    missing CONGRATULATIONS. Test failed.'
      echo $ref $exe 'FAILED' >> ${testhome}/failed
      if [ "${exitonfail}" = true ]; then exit; fi
    fi
    for outfile in 'fort.15' ; do
      if [ -e $outfile ]; then
        mv ${outfile} ../${outdir}
      else
        echo '    missing '${outfile}' Test failed.'
        echo $ref $exe 'FAILED' >> ${testhome}/failed
      if [ "${exitonfail}" = true ]; then exit; fi
      fi
    done

    cd ..
    rm Work/* # this is for being more safe
    
  done # end of exe loop
  
  # compare debug and fast
  # omega case also produces fort.25 - need to add this
  for outfile in 'fort.15' ; do
    outdebug='Outputs/Output_ref_'${ref}'_debug/'$outfile
    outfast='Outputs/Output_ref_'${ref}'_fast/'$outfile
    test=$()
    if cmp -s $outdebug $outfast >/dev/null; then
      echo $outfile '    equal for debug and fast' >> log.run_ref
    else
      echo 'WARNING:' $outfile '    not equal for debug and fast, test failed'
      echo $ref $exe 'FAILED' >> ${testhome}/failed
       if [ "${exitonfail}" = true ]; then exit; fi
    fi
  done

  # save and show runtimes
  for exe in 'debug' 'fast'; do
    log='Outputs/Output_ref_'${ref}'_'${exe}'/log'
    times=$(tail -3 ${log})
    real=$(echo $times | grep real | awk '{print $2}')
    user=$(echo $times | grep user | awk '{print $4}')
    sys=$( echo $times | grep sys  | awk '{print $6}')
    echo $hash, "'"reference"'", "'"${ref}'_'${exe}"'", ${real}, ${user}, ${sys} >> ${csvfile}
    tail -1 runtimes.csv >> log.run_ref
  done
  
  echo # go to next reference run
  
done
echo 
echo More information in log.run_ref

# the following code is executed only if exitonfail is not set to 'true'.
if [ -e failed ]; then 
  echo
  echo Some tests failed, see file "failed":
  echo
  cat failed|sort -u
fi
