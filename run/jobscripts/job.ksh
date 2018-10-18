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
## -o /scratch/ms/at/km4a/flex_ecmwf.${PBS_JOBID}.out
## job output is in .ecaccess_DO_NOT_REMOVE
##PBS -j oe
##PBS -V
##PBS -l EC_threads_per_task=24
##PBS -l EC_memory_per_task=32000MB

set -x
export VERSION=7.1
case ${HOST} in
  *ecg*)
  module load python
  module unload grib_api
  module unload eccodes
  module unload emos
#  module load grib_api/1.27.0
  module load grib_api/1.14.5
  module load emos/457-r64
  export PATH=${PATH}:${HOME}/flex_extract_v7.1/source/python
  ;;
  *cca*)
  module switch PrgEnv-cray PrgEnv-intel
  module load grib_api
  module load emos
  module load python
  export SCRATCH=${TMPDIR}
  export PATH=${PATH}:${HOME}/flex_extract_v7.1/source/python
  ;;
esac

cd ${SCRATCH}
mkdir -p python$$
cd python$$

export CONTROL=CONTROL

cat >${CONTROL}<<EOF
accmaxstep 12
acctime 06/18
acctype FC
accuracy 24
addpar 186 187 188 235 139 39 
area 
basetime None
controlfile CONTROL_EA5.testgrid
cwc 0
dataset None
date_chunk 3
debug 1
destination annep@genericSftp
dpdeta 1
dtime 1
ecfsdir ectmp:/${USER}/econdemand/
ecgid at
ecstorage 0
ectrans 1
ecuid km4a
end_date 20090108
eta 1
etadiff 0
etapar 77
expver 1
format GRIB1
gateway srvx8.img.univie.ac.at
gauss 0
gaussian 
grib2flexpart 0
grid 1000
inputdir /raid60/nas/tmc/Anne/Interpolation/flexextract/flex_extract_v7.1/run/workspace
install_target None
job_template job.temp
left -5000
level 137
levelist 100/to/137
logicals gauss omega omegadiff eta etadiff dpdeta cwc wrf grib2flexpart ecstorage ectrans debug request public 
lower 10000
mailfail ${USER} 
mailops ${USER} 
makefile Makefile.gfortran
marsclass EA
maxstep 0
number OFF
omega 0
omegadiff 0
outputdir /raid60/nas/tmc/Anne/Interpolation/flexextract/flex_extract_v7.1/run/workspace
prefix EA
public 0
queue ecgate
request 2
resol 159
right 5000
smooth 0
start_date 20090108
step 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
stream OPER
time 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 
type AN AN AN AN AN AN AN AN AN AN AN AN AN AN AN AN AN AN AN AN AN AN AN AN 
upper 20000
wrf 0
EOF


submit.py --controlfile=${CONTROL} --inputdir=./work --outputdir=./work 1> prot 2>&1

if [ $? -eq 0 ] ; then
  l=0
  for muser in `grep -i MAILOPS ${CONTROL}`; do
      if [ ${l} -gt 0 ] ; then 
         mail -s flex.${HOST}.$$ ${muser} <prot
      fi
      l=$((${l}+1))
  done
else
  l=0
  for muser in `grep -i MAILFAIL ${CONTROL}`; do
      if [ ${l} -gt 0 ] ; then 
         mail -s "ERROR! flex.${HOST}.$$" ${muser} <prot
      fi
      l=$((${l}+1))
  done
fi

