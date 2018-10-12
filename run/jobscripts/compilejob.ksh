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
##PBS -q ns
##PBS -S /usr/bin/ksh
##PBS -o /scratch/ms/at/km4a/flex_ecmwf.${Jobname}.${Job_ID}.out
# job output is in .ecaccess_DO_NOT_REMOVE
##PBS -j oe
##PBS -V
##PBS -l EC_threads_per_task=1
##PBS -l EC_memory_per_task=3200MB

set -x
export VERSION=7.1
case ${HOST} in
  *ecg*)
  module unload eccodes
#  module load python
  module unload grib_api
  module unload emos
  module load grib_api/1.27.0
  module load emos/457-r64
  export FLEXPART_ROOT_SCRIPTS=${HOME}
  export MAKEFILE=Makefile.gfortran
  ;;
  *cca*)
  module switch PrgEnv-cray PrgEnv-intel
  module load grib_api
  module load emos
  module load python
  echo ${GROUP}
  echo ${HOME}
  echo ${HOME} | awk -F / '{print $1, $2, $3, $4}'
  export GROUP=`echo ${HOME} | awk -F / '{print $4}'`
  export SCRATCH=/scratch/ms/${GROUP}/${USER}
  export FLEXPART_ROOT_SCRIPTS=${HOME}
  export MAKEFILE=Makefile.gfortran
  ;;
esac

mkdir -p ${FLEXPART_ROOT_SCRIPTS}/flex_extract_v${VERSION}
cd ${FLEXPART_ROOT_SCRIPTS}/flex_extract_v${VERSION}   # if FLEXPART_ROOT is not set this means cd to the home directory
tar -xvf ${HOME}/flex_extract_v${VERSION}.tar
cd source/fortran
\rm *.o *.mod CONVERT2 
make -f ${MAKEFILE} >flexcompile 2>flexcompile

ls -l CONVERT2 >>flexcompile
if [ $? -eq 0 ]; then
  echo 'SUCCESS!' >>flexcompile
  mail -s flexcompile.${HOST}.$$ ${USER} <flexcompile
else
  echo Environment: >>flexcompile
  env >> flexcompile
  mail -s "ERROR! flexcompile.${HOST}.$$" ${USER} <flexcompile
fi
