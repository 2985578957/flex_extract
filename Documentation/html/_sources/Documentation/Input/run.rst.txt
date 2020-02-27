**********************************
The executable Script - ``run.sh``
**********************************

The execution of ``flex_extract`` is done by the ``run.sh`` Shell script, which is a wrapping script for the top-level Python script ``submit.py``. 
The Python script constitutes the entry point to ECMWF data retrievals with ``flex_extract`` and controls the program flow. 

``submit.py`` has two (three) sources for input parameters with information about program flow and ECMWF data selection, the so-called ``CONTROL`` file,  
the command line parameters and the so-called ``ECMWF_ENV`` file. Whereby, the command line parameters will override the ``CONTROL`` file parameters. 

Based on these input information ``flex_extract`` applies one of the application modes to either retrieve the ECMWF data via a Web API on a local maschine or submit a jobscript to ECMWF servers and retrieve the data there with sending the files to the local system eventually.



PUT IN HERE A BLOCKDIAGRAM OF RAW PROGRAM FLOW



Submission Parameter
--------------------


.. exceltable:: Parameter for Submission
    :file:  ../../_files/SubmitParameters.xls
    :header: 1  
    :sheet: 0
   
   
   

Content of ``run.sh``
---------------------
  
.. literalinclude:: ../../../../../Run/run.sh 
   :language: bash
   :caption: run.sh


.. _ref-install-script:
       
Usage of ``submit.py`` (optional)
---------------------------------

It is also possible to start ``flex_extract`` directly from command line by using the ``submit.py`` script instead of the wrapping Shell script ``run.sh``.  This top-level script is located in 
``flex_extract_vX.X/source/python`` and is executable. With the ``help`` parameter we see again all possible 
command line parameter. 

.. code-block:: bash

   submit.py --help

   usage: submit.py [-h] [--start_date START_DATE] [--end_date END_DATE]
                 [--date_chunk DATE_CHUNK] [--job_chunk JOB_CHUNK]
                 [--controlfile CONTROLFILE] [--basetime BASETIME]
                 [--step STEP] [--levelist LEVELIST] [--area AREA]
                 [--debug DEBUG] [--oper OPER] [--request REQUEST]
                 [--public PUBLIC] [--rrint RRINT] [--inputdir INPUTDIR]
                 [--outputdir OUTPUTDIR] [--ppid PPID]
                 [--job_template JOB_TEMPLATE] [--queue QUEUE]

    Retrieve FLEXPART input from ECMWF MARS archive

    optional arguments:
      -h, --help            show this help message and exit
      --start_date START_DATE
                            start date YYYYMMDD (default: None)
      --end_date END_DATE   end_date YYYYMMDD (default: None)
      --date_chunk DATE_CHUNK
                            # of days to be retrieved at once (default: None)
      --job_chunk JOB_CHUNK
                            # of days to be retrieved within a single job
                            (default: None)
      --controlfile CONTROLFILE
                            The file with all CONTROL parameters. (default:
                            CONTROL_EA5)
      --basetime BASETIME   base such as 0 or 12 (for half day retrievals)
                            (default: None)
      --step STEP           Forecast steps such as 00/to/48 (default: None)
      --levelist LEVELIST   Vertical levels to be retrieved, e.g. 30/to/60
                            (default: None)
      --area AREA           area defined as north/west/south/east (default: None)
      --debug DEBUG         debug mode - leave temporary files intact (default:
                            None)
      --oper OPER           operational mode - prepares dates with environment
                            variables (default: None)
      --request REQUEST     list all mars requests in file mars_requests.dat
                            (default: None)
      --public PUBLIC       public mode - retrieves the public datasets (default:
                            None)
      --rrint RRINT         Selection of old or new precipitation interpolation: 0
                            - old method 1 - new method (additional subgrid
                            points) (default: None)
      --inputdir INPUTDIR   Path to the temporary directory for the retrieval grib
                            files and other processing files. (default: None)
      --outputdir OUTPUTDIR
                            Path to the final directory where the final FLEXPART
                            ready input files are stored. (default: None)
      --ppid PPID           This is the specify parent process id of a single
                            flex_extract run to identify the files. It is the
                            second number in the GRIB files. (default: None)
      --job_template JOB_TEMPLATE
                            The job template file which are adapted to be
                            submitted to the batch system on ECMWF server.
                            (default: job.temp)
      --queue QUEUE         The ECMWF server name for submission of the job script
                            to the batch system (e.g. ecgate | cca | ccb)
                            (default: None)







.. toctree::
    :hidden:
    :maxdepth: 2
