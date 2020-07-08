**************************
The job script ``job.ksh``
**************************

The job script is a Korn-shell script which will be created at runtime for each ``flex_extract`` execution in the application modes **remote** and **gateway**.

It is based on the ``submitscript.template`` template file stored in the ``Templates`` directory.
This template is generated in the installation process from a ``jobscript.template`` template file.

``Flex_extract`` uses the Python package `genshi <https://genshi.edgewall.org/>`_ to generate
the Korn-shell script from the template files by substituting the individual parameters. 
These individual parameters are marked by ``$$`` in ``jobscript.template``. 

The job script has a number of settings for the batch system which are fixed, and differentiates between the *ecgate* and the *cca/ccb* 
server system to load the necessary modules for the environment when submitted to the batch queue.

The submission is done by the ``ECaccess`` tool from within ``flex_extract`` with the command ``ecaccess-job-submit``.



What does the job script do?
----------------------------

 #. It sets necessary batch system parameters.
 #. It prepares the job environment at the ECMWF servers by loading the necessary library modules.
 #. It sets some environment variables for the single session.
 #. It creates the directory structure in the user's ``$SCRATCH`` file system.
 #. It creates a CONTROL file on the ECMWF servers whith the parameters set before creating the ``job.ksh``. ``Flex_extract`` has a set of parameters which are passed to the job script with their default or the user-defined values. It also sets ``CONTROL`` as an environment variable.
 #. ``Flex_extract`` is started from within the ``work`` directory of the new directory structure by calling the ``submit.py`` script. It sets new paths for input and output directories and the recently generated ``CONTROL`` file.
 #. At the end, it checks whether the script has returned an error or not, and emails the log file to the user.




Example ``job.ksh``
-------------------------
  
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
      module unload grib_api
      module unload emos
      module load python3
      module load eccodes
      module load emos/455-r64
      export PATH=${PATH}:${HOME}/flex_extract_v7.1/Source/Python
      ;;
      *cca*)
      module switch PrgEnv-cray PrgEnv-intel
      module load python3
      module load eccodes
      module load emos/455-r64
      export SCRATCH=${TMPDIR}
      export PATH=${PATH}:${HOME}/flex_extract_v7.1/Source/Python
      ;;
    esac

    cd ${SCRATCH}
    mkdir -p python$$
    cd python$$

    export CONTROL=CONTROL

    cat >${CONTROL}<<EOF
    accmaxstep 24
    acctime 18
    acctype FC
    accuracy 24
    addpar None
    area 74.0/-24.0/10.0/60.0
    basetime None
    cds_api None
    controlfile CONTROL_CERA
    cwc 1
    dataset None
    date_chunk 3
    debug 1
    destination <specificname>@genericSftp
    doubleelda 0
    dpdeta 1
    dtime 3
    ec_api None
    ecfsdir ectmp:/${USER}/econdemand/
    ecgid at
    ecstorage 0
    ectrans 1
    ecuid km4a
    end_date 20000809
    eta 1
    etadiff 0
    etapar 77
    expver 1
    format GRIB1
    gateway srvx8.img.univie.ac.at
    gauss 0
    gaussian 
    grib2flexpart 0
    grid 1.0/1.0
    inputdir <path-to-flex_extract>/flex_extract_v7.1/run/workspace
    install_target None
    job_chunk 1
    job_template job.temp
    left -24.
    level 91
    levelist 1/to/91
    logicals gauss omega omegadiff eta etadiff dpdeta cwc wrf grib2flexpart ecstorage ectrans debug oper request public purefc rrint doubleelda 
    lower 10.
    mailfail ${USER} 
    mailops ${USER} 
    marsclass EP
    maxstep 0
    number 000
    omega 0
    omegadiff 0
    oper 0
    outputdir <path-to-flex_extract>/flex_extract_v7.1/run/workspace
    prefix CE
    public 0
    purefc 0
    queue ecgate
    request 2
    resol 159
    right 60.
    rrint 0
    smooth 0
    start_date 20000809
    step 00 00 00 00 00 00 00 00 
    stream ENDA
    time 00 03 06 09 12 15 18 21 
    type AN AN AN AN AN AN AN AN 
    upper 74.
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


   

.. toctree::
    :hidden:
    :maxdepth: 2
