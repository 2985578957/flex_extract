**********************
CONTROL file changes
**********************

Changes from version 7.0.4 to version 7.1 
    - removed ``M_`` (but is still available for downward compatibility)
    - grid resolution not in 1/1000 degress anymore (but is still available for downward compatibility)
    - comments available with ``#``
    - only parameters which are needed to override the default values are necessary 
    - number of type/step/time elements does not have to be 24 anymore. Just provide what you need. 
    - the ``dtime`` parameter needs to be consistent with ``type/step/time``, for example, ``dtime`` can be coarser than the ``time`` intervals available, but not finer.

 

    
.. toctree::
    :hidden:
    :maxdepth: 2
