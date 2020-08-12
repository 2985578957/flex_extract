*********
Templates
*********

In ``flex_extract``, the Python package `genshi <https://genshi.edgewall.org/>`_ is used to create specific files from templates. It is the most efficient way to be able to quickly adapt, e. g., the job scripts sent to the ECMWF batch queue system, or the namelist file für the Fortran program, without the need to change the program code. 

.. note::
   Do not change anything in these files unless you understand the effects!
   
Each template file has its content framework and keeps so-called placeholder variables in the positions where the values need to be substituted at run time. These placeholders are marked by a leading ``$`` sign. In case of the Korn shell job scripts, where (environment) variables are used, the ``$`` sign needs to be doubled for `escaping`.
   
The following templates are used; they can be found in the directory ``flex_extract_vX.X/Templates``:

calc_etadot_nml.template
-------------------------

    This is the template for a Fortran namelist file called ``fort.4`` read by ``calc_etadot``.
    It contains all the parameters ``calc_etadot`` needs. 
    
    .. code-block:: fortran
 
        &NAMGEN
          maxl = $maxl,
          maxb = $maxb,
          mlevel = $mlevel,
          mlevelist = "$mlevelist",
          mnauf = $mnauf,
          metapar = $metapar,
          rlo0 = $rlo0,
          rlo1 = $rlo1,
          rla0 = $rla0,
          rla1 = $rla1,
          momega = $momega,
          momegadiff = $momegadiff,
          mgauss = $mgauss,
          msmooth = $msmooth,
          meta = $meta,
          metadiff = $metadiff,
          mdpdeta = $mdpdeta
        /

ECMWF_ENV.template
------------------

    This template is used to create the ``ECMWF_ENV`` file in the application modes **gateway** and **remote**. It contains the user credentials and gateway server settings for the file transfers.

    .. code-block:: bash
    
        ECUID $user_name
        ECGID $user_group
        GATEWAY $gateway_name
        DESTINATION $destination_name

installscript.template
----------------------

    This template is used to create the job script file called ``compilejob.ksh`` during the installation process for the application modes **remote** and **gateway**. 

    At the beginning, some directives for the batch system are set. 
    On the **ecgate** server, the ``SBATCH`` comments are the directives for the SLURM workload manager. A description of the single lines can be found at `SLURM directives <https://confluence.ecmwf.int/display/UDOC/Writing+SLURM+jobs>`_.
    For the high-performance computers **cca** and **ccb**, the ``PBS`` comments are necessary;  for details see `PBS directives <https://confluence.ecmwf.int/display/UDOC/Batch+environment%3A++PBS>`_.

    The software environment requirements mentioned in :ref:`ref-requirements` are prepared by loading the corresponding modules depending on the ``HOST``. It should not be changed without testing.
    
    Afterwards, the installation steps as such are done. They included the generation of the root directory, putting files in place, compiling the Fortran program, and sending a log file by email.

    .. code-block:: ksh
    
        #!/bin/ksh

        # ON ECGB:
        # start with ecaccess-job-submit -queueName ecgb NAME_OF_THIS_FILE  on gateway server
        # start with sbatch NAME_OF_THIS_FILE directly on machine

        #SBATCH --workdir=/scratch/ms/$usergroup/$username
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
        ##PBS -o /scratch/ms/$usergroup/$username/flex_ecmwf.$${Jobname}.$${Job_ID}.out
        # job output is in .ecaccess_DO_NOT_REMOVE
        ##PBS -j oe
        ##PBS -V
        ##PBS -l EC_threads_per_task=1
        ##PBS -l EC_memory_per_task=3200MB

        set -x
        export VERSION=$version_number
        case $${HOST} in
          *ecg*)
          module unload grib_api
          module unload emos
          module load python3
          module load eccodes
          module load emos/455-r64
          export FLEXPART_ROOT_SCRIPTS=$fp_root_scripts
          export MAKEFILE=$makefile
          ;;
          *cca*)
          module switch PrgEnv-cray PrgEnv-intel
          module load python3
          module load eccodes
          module load emos/455-r64
          echo $${GROUP}
          echo $${HOME}
          echo $${HOME} | awk -F / '{print $1, $2, $3, $4}'
          export GROUP=`echo $${HOME} | awk -F / '{print $4}'`
          export SCRATCH=/scratch/ms/$${GROUP}/$${USER}
          export FLEXPART_ROOT_SCRIPTS=$fp_root_scripts
          export MAKEFILE=$makefile
          ;;
        esac

        mkdir -p $${FLEXPART_ROOT_SCRIPTS}/flex_extract_v$${VERSION}
        cd $${FLEXPART_ROOT_SCRIPTS}/flex_extract_v$${VERSION}   # if FLEXPART_ROOT is not set this means cd to the home directory
        tar -xvf $${HOME}/flex_extract_v$${VERSION}.tar
        cd Source/Fortran
        \rm *.o *.mod $fortran_program 
        make -f $${MAKEFILE} >flexcompile 2>flexcompile

        ls -l $fortran_program >>flexcompile
        if [ $$? -eq 0 ]; then
          echo 'SUCCESS!' >>flexcompile
          mail -s flexcompile.$${HOST}.$$$$ $${USER} <flexcompile
        else
          echo Environment: >>flexcompile
          env >> flexcompile
          mail -s "ERROR! flexcompile.$${HOST}.$$$$" $${USER} <flexcompile
        fi


submitscript.template
---------------------

    This template is used to create the actual job script file called ``job.ksh`` for the execution of ``flex_extract`` in the application modes **remote** and **gateway**. 

    At the beginning, some directives for the batch system are set. 
    On the **ecgate** server, the ``SBATCH`` comments are the directives for the SLURM workload manager. A description of the single lines can be found at `SLURM directives <https://confluence.ecmwf.int/display/UDOC/Writing+SLURM+jobs>`_.
    For the high performance computers **cca** and **ccb**, the ``PBS`` comments are necessary; 
    for details see `PBS directives <https://confluence.ecmwf.int/display/UDOC/Batch+environment%3A++PBS>`_.

    The software environment requirements mentioned in :ref:`ref-requirements` are prepared by loading the corresponding modules depending on the ``HOST``. It should not be changed without testing.
    
    Afterwards, the run directory and the ``CONTROL`` file are created and ``flex_extract`` is executed. In the end, a log file is send by email.
    
    .. code-block:: ksh
    
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
        ## -o /scratch/ms/at/km4a/flex_ecmwf.$${PBS_JOBID}.out
        ## job output is in .ecaccess_DO_NOT_REMOVE
        ##PBS -j oe
        ##PBS -V
        ##PBS -l EC_threads_per_task=24
        ##PBS -l EC_memory_per_task=32000MB

        set -x
        export VERSION=7.1
        case $${HOST} in
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

        cd $${SCRATCH}
        mkdir -p python$$$$
        cd python$$$$

        export CONTROL=CONTROL

        cat >$${CONTROL}<<EOF
        $control_content
        EOF


        submit.py --controlfile=$${CONTROL} --inputdir=./work --outputdir=./work 1> prot 2>&1

        if [ $? -eq 0 ] ; then
          l=0
          for muser in `grep -i MAILOPS $${CONTROL}`; do
              if [ $${l} -gt 0 ] ; then 
                 mail -s flex.$${HOST}.$$$$ $${muser} <prot
              fi
              l=$(($${l}+1))
          done
        else
          l=0
          for muser in `grep -i MAILFAIL $${CONTROL}`; do
              if [ $${l} -gt 0 ] ; then 
                 mail -s "ERROR! flex.$${HOST}.$$$$" $${muser} <prot
              fi
              l=$(($${l}+1))
          done
        fi
        

jobscript.template
------------------

    This template is used to create the template for the execution job script ``submitscript.template`` for ``flex_extract`` in the installation process. A description of the file can be found under ``submitscript.template``. Several parameters are set in this process, such as the user credentials and the ``flex_extract`` version number.
        
    .. code-block:: ksh
    
        #!/bin/ksh

        # ON ECGB:
        # start with ecaccess-job-submit -queueName ecgb NAME_OF_THIS_FILE  on gateway server
        # start with sbatch NAME_OF_THIS_FILE directly on machine

        #SBATCH --workdir=/scratch/ms/$usergroup/$username
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
        ## -o /scratch/ms/$usergroup/$username/flex_ecmwf.$$$${PBS_JOBID}.out
        ## job output is in .ecaccess_DO_NOT_REMOVE
        ##PBS -j oe
        ##PBS -V
        ##PBS -l EC_threads_per_task=24
        ##PBS -l EC_memory_per_task=32000MB

        set -x
        export VERSION=$version_number
        case $$$${HOST} in
          *ecg*)
          module unload grib_api
          module unload emos
          module load python3
          module load eccodes
          module load emos/455-r64
          export PATH=$$$${PATH}:$fp_root_path
          ;;
          *cca*)
          module switch PrgEnv-cray PrgEnv-intel
          module load python3
          module load eccodes
          module load emos/455-r64
          export SCRATCH=$$$${TMPDIR}
          export PATH=$$$${PATH}:$fp_root_path
          ;;
        esac

        cd $$$${SCRATCH}
        mkdir -p python$$$$$$$$
        cd python$$$$$$$$

        export CONTROL=CONTROL

        cat >$$$${CONTROL}<<EOF
        $$control_content
        EOF


        submit.py --controlfile=$$$${CONTROL} --inputdir=./work --outputdir=./work 1> prot 2>&1

        if [ $? -eq 0 ] ; then
          l=0
          for muser in `grep -i MAILOPS $$$${CONTROL}`; do
              if [ $$$${l} -gt 0 ] ; then 
                 mail -s flex.$$$${HOST}.$$$$$$$$ $$$${muser} <prot
              fi
              l=$(($$$${l}+1))
          done
        else
          l=0
          for muser in `grep -i MAILFAIL $$$${CONTROL}`; do
              if [ $$$${l} -gt 0 ] ; then 
                 mail -s "ERROR! flex.$$$${HOST}.$$$$$$$$" $$$${muser} <prot
              fi
              l=$(($$$${l}+1))
          done
        fi



   

.. toctree::
    :hidden:
    :maxdepth: 2
