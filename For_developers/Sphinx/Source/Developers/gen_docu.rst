**************************
Updating the documentation
**************************

UNDER CONSTRUCTION

Additional software
===================

Developers working on ``flex_extract`` should make extensive use of the prepared test cases and unit tests, and should also update the documentation. For this, some additional software is necessary:

.. code-block:: sh

  pip install pylint
  pip install pytest
  pip install mock
  pip install graphviz
  pip install sphinx
  pip install sphinxcontrib-exceltable
  pip install seqdiag
  pip install sphinxcontrib-seqdiag
  pip install sphinxcontrib-blockdiag
  pip install pycallgraph





On-line documentation with Sphinx
=================================

Use the script ``gen_docu.sh`` to generate an update of the on-line documentation of the Python component.

It uses ``pyreverse`` to generate class and package diagrams with ``graphviz`` and overwrites the old files in the developers directory. 
``pyreverse`` creates ``dot`` files, and with the ``dot`` program of the ``graphviz`` software, the ``png`` files are created. Everything happens in the Python source directory before moving them finally to the ``For_developers`` directory. The Sphinx source code has a ``_files`` directory which contains links to these ``png`` files and therefore they should not be renamed.  


Sequence diagramms
------------------

You might need to adapt the fonts path for the diagrams to a true-type font. Currently it is set to:

.. code-block:: bash

    # Fontpath for seqdiag (truetype font)
    seqdiag_fontpath = '/usr/share/fonts/dejavu/DejaVuSerif.ttf'


Block diagramms
------------------

You might need to adapt the fonts path for the diagrams to a true-type font. Currently it is set to:

.. code-block:: bash

     # Fontpath for blockdiag (truetype font)
     blockdiag_fontpath = '/usr/share/fonts/dejavu/DejaVuSerif.ttf'




.. toctree::
    :hidden:
    :maxdepth: 2
