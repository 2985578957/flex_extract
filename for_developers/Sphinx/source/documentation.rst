=============
Documentation
=============
        
    Overview
      - What is ``flex_extract``?
      
        - general overview
        - motivation, aim
        - directory structure
        
      - Software components
        complete component structure (table or diagram)
        
        - Python package
        
          - Package diagram
          - Files and modules as table with information about unit tests
          - Api
          
        - Fortran program - CONVERT2
        
          - Package diagram
          - Api
          
        - Wrapping shell-scripts
        
      - Dependencies
      - General context (for who?, Usecases, work tree)
      - Access to ECMWF
      - Application modes
      - Call tree
      - Sequence diagram
    
    Control & Input Data
      - Controlling files
      
        - setup.sh (explain input parameters)            
        - job scripts
        - compile job
        - run[_local].sh
        
      - Input Data
      
        - CONTROL files
        
          - The CONTROL file
          - CONTROL parameters
          - Examples
          - Changes and its downward compatibilities (eg M _ /grid)
          
        - ECMWF_ENV file
        - Templates
        
    Output Data
      - mars request file
      - Mars grib files
      - flux files
      - index.idx
      - CONTROL (neu)
      - fort files
      - EN* files
      
        - Usual  output
        - Output for pure forecast
        - Output for ensemble members
        - Output for new precipitation disaggregation
    
    Disaggregation
      - What is disaggregation?
      - Why do we need it/ which fields?
      - Method for precipitation
      
        - Old method
        - New method
        - Differences in resulting Gribfiles
        
      - Method for rest fields
    
    Vertical Coordinate
      - Methods (GAUSS, ETA, OMEGA)
      - CONVERT (Petra)
    
    Auto Generated Documentation
      - Python
      - Fortran

    
.. toctree::
    :hidden:
    :maxdepth: 2
    
    Documentation/overview
    Documentation/input
    Documentation/output
    Documentation/disagg
    Documentation/vertco
    Documentation/api
  
