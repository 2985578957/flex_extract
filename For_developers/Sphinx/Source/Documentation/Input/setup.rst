**************************************
The installation script - ``setup.sh``
**************************************

The installation of ``flex_extract`` is done by the shell script ``setup.sh`` located in the root directory of ``flex_extract``.
It calls the top-level Python script ``install.py`` which does all the necessary operations to prepare the  application environment selected. This includes:

- preparing the file ``ECMWF_ENV`` with the user credentials for member-state access to ECMWF servers (in **remote** and **gateway** mode)
- preparation of a compilation Korn-shell script (in **remote** and **gateway** mode)
- preparation of a job template with user credentials (in **remote** and **gateway** mode)
- create a tarball of all necessary files
- copying the tarball to the target location (depending on application mode and installation path)
- submit the compilation script to the batch queue at ECMWF servers (in **remote** and **gateway** mode) or just untar the tarball at target location (**local mode**)
- compilation of the Fortran program ``calc_etadot``


The Python installation script ``install.py`` has several command line arguments defined in ``setup.sh``, in the section labelled "*AVAILABLE COMMANDLINE ARGUMENTS TO SET*". The user has to adapt these parameters according to his/her personal needs. The parameters are listed and described in :ref:`ref-instparams`. The script also does some checks to guarantee that the necessary parameters were set.
   
After the installation process, some tests can be conducted. They are described in section :ref:`ref-testinstallfe`.

The following diagram sketches the files and scripts involved in the installation process:

.. _ref-install-blockdiag:

.. blockdiag::

   blockdiag {
   
     default_fontsize = 24; 
     
     // Set node metrix
     node_width = 300; // default is 128
   
     // Set span metrix
     span_width = 80;  // default value is 64
     
     ECMWF_ENV.template [shape = flowchart.input];
     compilejob.template [shape = flowchart.input];
     job.template [shape = flowchart.input];
     
     compilejob.ksh [shape = roundedbox];
    // tarball
    // ECMWF_ENV
    // job.temp
     
     "CONTROL file" [shape = flowchart.input];
     
     setup.sh [shape = roundedbox];
     install.py [shape = roundedbox];
     
     "ECMWF server"  [shape = flowchart.terminator];
     
     //beginpoint [shape = beginpoint];
     
     orientation = landscape;
     
     //beginpoint -> setup.sh;
     setup.sh -> install.py;
     
     install.py <- "CONTROL file";
                 
     install.py -> ECMWF_ENV, job.temp, compilejob.ksh, tarball;   

     ECMWF_ENV.template, job.template, compilejob.template  -> install.py; 
     
     tarball, compilejob.ksh -> "ECMWF server";
     
          
     group exec {
       // set backgound color
       color = "#FF6633";
       
       orientation = portrait;
       setup.sh;
       install.py;
     }
     
     group out {
       color = "#FFFFFF";
       group output {
         color = "#99FF99";
         ECMWF_ENV;
         job.temp; 
         compilejob.ksh; 
       }
        
       group ECMWF {
         color = "#006600";
         tarball;
         
       }
     }
 
     group input {
       
       color = "#FFFFFF";
       
       group temps {
         color = "#66CCFF";
                  
         ECMWF_ENV.template;
         job.template;
         compilejob.template;
       }
       
       group in {
         color = "#3366FF";
         "CONTROL file";
       }
     }
     
   }


.. blockdiag::
   :caption: Diagram of data flow during the installation process. Trapezoids are input files with the light blue area being the template files. Round-edge orange boxes are executable files which start the installation process and read the input files. Rectangular green boxes are  output files. Light green files are  needed only in the remota and gateway mode.

   blockdiag {
   
     group{
       orientation = portrait;
       label = "Legend";
       fontsize = 28;
       color = "#FFFFFF";
       'executable scripts' [shape = roundedbox];
       'input files' [shape = flowchart.input];
       'output files';
        server [shape = flowchart.terminator];
     }
   }

.. _ref-instparams:

Installation parameters
-----------------------
   
.. exceltable:: Parameter for Installation
    :file:  ../../_files/InstallationParameter.xls
    :header: 1  
   


Content of ``setup.sh``
-----------------------
  
.. literalinclude:: ../../../../../setup.sh 
   :language: bash
   :caption: setup.sh
       
       
.. _ref-install-script:
       
Usage of ``install.py`` (optional)
----------------------------------

It is also possible to start the installation process of ``flex_extract`` directly from the command line by using the ``install.py`` script instead of the wrapper shell script ``setup.sh``.  This top-level script is located in 
``flex_extract_vX.X/Source/Python`` and is executable. With the ``--help`` parameter, 
we see again all possible command line parameters. 

.. code-block:: bash
 
    install.py --help
    
    usage: install.py [-h] [--target INSTALL_TARGET] [--makefile MAKEFILE]
                  [--ecuid ECUID] [--ecgid ECGID] [--gateway GATEWAY]
                  [--destination DESTINATION] [--installdir INSTALLDIR]
                  [--job_template JOB_TEMPLATE] [--controlfile CONTROLFILE]

    Install flex_extract software locally or on ECMWF machines

    optional arguments:
      -h, --help            show this help message and exit
      --target INSTALL_TARGET
                            Valid targets: local | ecgate | cca , the latter two
                            are at ECMWF (default: None)
      --makefile MAKEFILE   Name of makefile to compile the Fortran
                            code. (default depends on `target`: local - makefile_local_gfortran,
                            ecgate - makefile_ecgate, cca - makefile_cray)
      --ecuid ECUID         The user id at ECMWF. (default: None)
      --ecgid ECGID         The group id at ECMWF. (default: None)
      --gateway GATEWAY     The IP name (or IP address) of the local gateway server. (default: None)
      --destination DESTINATION
                            The ecaccess association, e.g. myUser@genericSftp
                            (default: None)
      --installdir INSTALLDIR
                            Root directory where flex_extract will be installed
                            to. (default: None)
      --job_template JOB_TEMPLATE
                            The rudimentary template file to create a batch job
                            template for submission to ECMWF servers. (default:
                            job.template)
      --controlfile CONTROLFILE
                            The file with all CONTROL parameters. (default:
                            CONTROL_EA5)





.. toctree::
    :hidden:
    :maxdepth: 2
