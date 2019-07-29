**********************
CONTROL file changes
**********************

Changes from version 7.0.4 to version 7.1 
    - removed ``M_`` (but is still available for downward compatibility)
    - grid resolution not in 1/1000 degress anymore (but is still available for downward compatibility)
    - comments available with ``#``
    - only parameters which are needed to override the default values are necessary 
    - number of type/step/time elements do not have to be 24 any more. Just select the interval you need. 
    - the ``dtime`` parameter needs to be consistent with ``type/step/time``. For example ``dtime`` can be coarser as ``time`` intervals are available, but not finer.

 

    
.. toctree::
    :hidden:
    :maxdepth: 2
