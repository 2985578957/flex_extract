#!/bin/ksh

# ON ECGB:
# start with ecaccess-job-submit -queueName ecgb NAME_OF_THIS_FILE  on gateway server
# start with sbatch NAME_OF_THIS_FILE directly on machine

#SBATCH --workdir=/scratch/ms/at/km4a
#SBATCH --qos=normal
#SBATCH --job-name=flex_ecmwf
#SBATCH --output=flex_ecmwf.%j.out
#SBATCH --error=flex_ecmwf.%j.out
#SBATCH --mail-type=FAIL
#SBATCH --time=12:00:00

## CRAY specific batch requests
##PBS -N flex_ecmwf
##PBS -q np
##PBS -S /usr/bin/ksh
## -o /scratch/ms/spatlh00/lh0/flex_ecmwf.$PBS_JOBID.out
## job output is in .ecaccess_DO_NOT_REMOVE
##PBS -j oe
##PBS -V
##PBS -l EC_threads_per_task=24
##PBS -l EC_memory_per_task=32000MB

set -x
export VERSION=7.1
case $HOST in
  *ecg*)
  module load python
  module unload grib_api
  module unload emos
  module load grib_api/1.14.5
  module load emos/437-r64
  export PATH=${PATH}:${HOME}/flex_extract_v7.1/python
  ;;
  *cca*)
  module switch PrgEnv-cray PrgEnv-intel
  module load grib_api
  module load emos
  module load python
  export SCRATCH=$TMPDIR
  export PATH=${PATH}:${HOME}/flex_extract_v7.1/python
  ;;
esac

cd $SCRATCH
mkdir -p python$$
cd python$$

export CONTROL=CONTROL

cat >$CONTROL<<EOF
accuracy 24
addpar 186 187 188 235 139 39 
area 
basetime None
controlfile CONTROL.test
cwc 0
date_chunk 3
debug 1
destination annep@genericSftp
dpdeta 1
dtime 3
ecfsdir ectmp:/${USER}/econdemand/
ecgid at
ecstorage 0
ectrans 1
ecuid km4a
end_date 20160606
eta 0
etadiff 0
etapar 77
expver 1
format GRIB1
gateway srvx8.img.univie.ac.at
gauss 1
grib2flexpart 0
grid 5000
inputdir ../work
install_target None
job_template job.temp
left -10000
level 60
levelist 59/to/60
logicals gauss omega omegadiff eta etadiff dpdeta cwc wrf grib2flexpart ecstorage ectrans debug request 
lower 30000
mailfail ${USER} 
mailops ${USER} 
makefile Makefile.gfortran
marsclass EI
maxstep 11
number OFF
omega 0
omegadiff 0
outputdir ../work
prefix EItest_
queue ecgate
request 0
resol 63
right 10000
smooth 0
start_date 20160606
step 00 01 02 03 04 05 00 07 08 09 10 11 00 01 02 03 04 05 00 07 08 09 10 11 
stream OPER
time 00 00 00 00 00 00 06 00 00 00 00 00 12 12 12 12 12 12 18 12 12 12 12 12 
type AN FC FC FC FC FC AN FC FC FC FC FC AN FC FC FC FC FC AN FC FC FC FC FC 
upper 40000
wrf 0
EOF


submit.py --controlfile=$CONTROL --inputdir=./work --outputdir=./work 1> prot 2>&1

if [ $? -eq 0 ] ; then
  l=0
  for muser in `grep -i MAILOPS $CONTROL`; do
      if [ $l -gt 0 ] ; then 
         mail -s flex.${HOST}.$$ $muser <prot
      fi
      l=$(($l+1))
  done
else
  l=0
  for muser in `grep -i MAILFAIL $CONTROL`; do
      if [ $l -gt 0 ] ; then 
         mail -s "ERROR! flex.${HOST}.$$" $muser <prot
      fi
      l=$(($l+1))
  done
fi

