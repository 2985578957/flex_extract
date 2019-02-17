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
  module load eccodes
  module unload emos
  module load emos/455-r64
  export PATH=${PATH}:${HOME}/flex_extract_v7.1/source/python
  ;;
  *cca*)
  module switch PrgEnv-cray PrgEnv-intel
  module load eccodes
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
acctime 00/12
acctype FC
accuracy 24
addpar /186/187/188/235/139/39
area 61.2/-10.0/36.0/32.0
basetime None
controlfile CONTROL_OD.fastnet
cwc 0
dataset None
date_chunk 3
debug 0
destination annep@genericSftp
dpdeta 1
dtime 1
ecapi None
ecfsdir ectmp:/${USER}/econdemand/
ecgid at
ecstorage 0
ectrans 1
ecuid km4a
end_date 20190212
eta 1
etadiff 0
etapar 77
expver 1
format GRIB2
gateway srvx8.img.univie.ac.at
gauss 0
gaussian 
grib2flexpart 0
grid 0.1/0.1
inputdir /raid60/nas/tmc/Anne/Interpolation/flexextract/flex_extract_v7.1/run/workspace
install_target None
job_chunk 1
job_template job.temp
left -10.0
level 137
levelist 1/to/137
logicals gauss omega omegadiff eta etadiff dpdeta cwc wrf grib2flexpart ecstorage ectrans debug oper request public purefc rrint 
lower 36.0
mailfail ${USER} 
mailops ${USER} 
makefile Makefile.gfortran
marsclass OD
maxstep 11
number OFF
omega 0
omegadiff 0
oper 0
outputdir /raid60/nas/tmc/Anne/Interpolation/flexextract/flex_extract_v7.1/run/workspace
prefix EN
public 0
purefc 0
queue ecgate
request 2
resol 1279
right 32.0
rrint 0
smooth 0
start_date 20190212
step 00 01 02 03 04 05 06 07 08 09 10 11 00 01 02 03 04 05 06 07 08 09 10 11 
stream OPER
time 00 00 00 00 00 00 00 00 00 00 00 00 12 12 12 12 12 12 12 12 12 12 12 12 
type AN FC FC FC FC FC FC FC FC FC FC FC AN FC FC FC FC FC FC FC FC FC FC FC 
upper 61.2
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

