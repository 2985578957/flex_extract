********************
Control & Input Data
********************

Input Data
    - :doc:`Input/control`
          ``Flex_extract`` needs a number of controlling parameters to decide on the behaviour and the actual dataset to be retrieved. They are initialized by ``flex_extract`` with their default values and can be overwritten with definitions set in the so called :doc:`Input/control`. 

          To be able to successfully retrieve data from the ECMWF Mars archive it is necessary to understand these parameters and set them to proper and consistent values. They are described in :doc:`Input/control_params` section. 

          We also have some :doc:`Input/examples` and description of :doc:`Input/changes` changes to previous versions and downward compatibilities.
        
    - :doc:`Input/ecmwf_env` 
         For ``flex_extract`` it is necessary to be able to reach ECMWF servers in the **remote mode** and the **gateway mode**. Therefore a :doc:`Input/ecmwf_env` is created during the installation process.

    - :doc:`Input/templates` 
         A number of files which are created by ``flex_extract`` are taken from templates. This makes it easy to adapt for example the jobscripts regarding its settings for the batch jobs.         





.. _setup : Input/setup.html
.. _run : Input/run.html
.. _install : Input/setup.html#ref-install-script
.. _submit : Input/submit.html#ref-submit-script

.. _ref-controlling:

Controlling
    The main tasks and behaviour of ``flex_extract`` are controlled by its Python scripts. There are two top-level scripts, one for installation called install_ and one for execution called submit_. 
    They can interpret a number of command line arguments which can be seen by typing ``--help`` after the script call. Go to the root directory of ``flex_extract`` to type:

    .. code-block:: bash

       cd flex_extract_vX.X
       python3 source/python/install.py --help
       python3 source/python/submit.py --help
   
    In this new version we provide also the wrapping Shell scripts setup_ and run_, which sets the command line parameters, do some checks and execute the corresponing Python scripts ``install.py`` and ``submit.py`` respectivley. 
     
    It might be faster and easier for beginners. See :doc:`../quick_start` for information on how to use them.

    Additionally, ``flex_extract`` creates the Korn Shell scripts :doc:`Input/compilejob` and :doc:`Input/jobscript` which will be send to the ECMWF serves in the **remote mode** and the **gateway mode** for starting batch jobs.

    The Fortran program will be compiled during the installation process by the :doc:`Input/fortran_makefile`. 
    
    To sum up, the following scripts controls ``flex_extract``:

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
