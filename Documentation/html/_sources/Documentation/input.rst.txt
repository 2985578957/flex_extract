********************
Control & input data
********************

Input data
    - :doc:`Input/control`
          ``Flex_extract`` needs a number of controlling parameters to decide on the behaviour and the actual data set to be retrieved. They are initialised by ``flex_extract`` with certain default values which can be overwritten with definitions set in the so-called :doc:`Input/control`. 

          For a successfull retrieval of data from the ECMWF MARS archive it is necessary to understand these parameters and to set them to proper and consistent values. They are described in :doc:`Input/control_params` section. 

          Furthermore, some :doc:`Input/examples` are provided, and in :doc:`Input/changes` changes to previous versions and downward compatibilities are described.
        
    - :doc:`Input/ecmwf_env` 
         ``flex_extract`` needs to be able to reach ECMWF servers in the **remote mode** and the **gateway mode**. Therefore a :doc:`Input/ecmwf_env` is created during the installation process.

    - :doc:`Input/templates` 
         A number of files which are created by ``flex_extract`` are taken from templates. This makes it easy to adapt, for example, the job scripts with regard to the settings for the batch jobs.         



.. _setup : Input/setup.html
.. _run : Input/run.html
.. _install : Input/setup.html#ref-install-script
.. _submit : Input/submit.html#ref-submit-script

.. _ref-controlling:

Controlling
    The main tasks and the behaviour of ``flex_extract`` are controlled by the Python scripts. There are two top-level scripts, one for installation called install_, and one for execution called submit_. 
    They interpret a number of command-line arguments which can be seen by typing ``--help`` after the script call. Go to the root directory of ``flex_extract`` to type:

    .. code-block:: bash

       cd flex_extract_vX.X
       python3 Source/Python/install.py --help
       python3 Source/Python/submit.py --help
   
    
    With version 7.1, we provide also wrapper shell scripts setup_ and run_ which set the command-line parameters, do some checks, and execute the corresponing Python scripts ``install.py`` and ``submit.py``, respectively. It might be faster and easier for beginners if they are used. See :doc:`../quick_start` for information on how to use them.

    ``flex_extract`` also creates the Korn shell scripts :doc:`Input/compilejob` and :doc:`Input/jobscript` which will be sent to the ECMWF servers in the **remote mode** and the **gateway mode** for starting batch jobs.

    The Fortran program is compiled during the installation process using the :doc:`Input/fortran_makefile`. 
    
    To sum up, the following scripts control ``flex_extract``:

    Installation 
       - :doc:`Input/setup` 
       - :doc:`Input/compilejob`
       - :doc:`Input/fortran_makefile`    

    Execution 
      - :doc:`Input/run` 
      - :doc:`Input/jobscript` 
             
             
    


                 

          
        
        
.. toctree::
    :hidden:
    :maxdepth: 2
    
    Input/setup
    Input/compilejob
    Input/fortran_makefile   
    Input/run
    Input/jobscript
    Input/control
    Input/control_params  
    Input/examples
    Input/changes 
    Input/ecmwf_env
    Input/templates
