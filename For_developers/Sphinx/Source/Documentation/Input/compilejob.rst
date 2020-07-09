*************************************************
The compilation job script ``compilejob.ksh``
*************************************************

The compile job is a Korn-shell script which will be created during the installation process for the application modes **remote** and **gateway** from a template called ``installscript.template`` in the template directory.

``Flex_extract`` uses the Python package `genshi <https://genshi.edgewall.org/>`_ to generate
the Korn-shell script from the template files by substituting the individual parameters. 
These individual parameters are marked by a doubled ``$`` sign in ``installscript.template``. 

The compilation script has a number of settings for the batch system which are fixed, and it differentiates between the *ecgate* and the *cca/ccb* 
server system to load the necessary modules for the environment when submitted to the batch queue.

The submission is done by the ``ECaccess`` tool from within ``flex_extract`` with the command ``ecaccess-job-submit``.



What does the compilation script do?
------------------------------------

 #. It sets the necessary batch-system parameters
 #. It prepares the job environment at the ECMWF servers by loading the necessary library modules
 #. It sets some environment variables for the single session
 #. It creates the ``flex_extract`` root directory in the ``$HOME`` path of the user
 #. It untars the tarball into the root directory.
 #. It compiles the Fortran program using ``makefile``.
 #. At the end, it checks whether the script has returned an error or not, and emails the log file to the user.





Example ``compilejob.ksh``
--------------------------
  
.. code-block::  bash
   
       
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
      module unload grib_api
      module unload emos
      module load python3
      module load eccodes
      module load emos/455-r64
      export FLEXPART_ROOT_SCRIPTS=${HOME}
      export MAKEFILE=makefile_ecgate
      ;;
      *cca*)
      module switch PrgEnv-cray PrgEnv-intel
      module load python3
      module load eccodes
      module load emos/455-r64
      echo ${GROUP}
      echo ${HOME}
      echo ${HOME} | awk -F / '{print $1, $2, $3, $4}'
      export GROUP=`echo ${HOME} | awk -F / '{print $4}'`
      export SCRATCH=/scratch/ms/${GROUP}/${USER}
      export FLEXPART_ROOT_SCRIPTS=${HOME}
      export MAKEFILE=makefile_ecgate
      ;;
    esac

    mkdir -p ${FLEXPART_ROOT_SCRIPTS}/flex_extract_v${VERSION}
    cd ${FLEXPART_ROOT_SCRIPTS}/flex_extract_v${VERSION}   # if FLEXPART_ROOT is not set this means cd to the home directory
    tar -xvf ${HOME}/flex_extract_v${VERSION}.tar
    cd Source/Fortran
    \rm *.o *.mod calc_etadot 
    make -f ${MAKEFILE} >flexcompile 2>flexcompile

    ls -l calc_etadot >>flexcompile
    if [ $? -eq 0 ]; then
      echo 'SUCCESS!' >>flexcompile
      mail -s flexcompile.${HOST}.$$ ${USER} <flexcompile
    else
      echo Environment: >>flexcompile
      env >> flexcompile
      mail -s "ERROR! flexcompile.${HOST}.$$" ${USER} <flexcompile
    fi


   

.. toctree::
    :hidden:
    :maxdepth: 2
