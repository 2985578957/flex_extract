#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import inspect
import pytest

sys.path.append('../python')
import _config
from classes.EcFlexpart import EcFlexpart
from classes.ControlFile import ControlFile
from mods.tools import silent_remove

class TestEcFlexpart():
    '''
    '''

    def test_write_namelist(self):
        import filecmp

        control_file = os.path.join(_config.PATH_TEST_DIR,
                                        'TestData',
                                        'CONTROL.temp')
        c = ControlFile(control_file)
        flexpart = EcFlexpart(c)

        c.inputdir = 'TestData'

        # comparison file
        testfile = os.path.join(_config.PATH_TEST_DIR,
                                'TestData',
                                'convert.nl.test')

        # create
        flexpart.write_namelist(c)

        finalfile = os.path.join(c.inputdir, _config.FILE_NAMELIST)
        assert filecmp.cmp(testfile, finalfile, shallow=False)

        # delete test file
        silent_remove(finalfile)




# these functions should test the output and compare the results with an output
# of the old version and check if there are no differences!!!
# also check for errors?! Or check if it works for alle datasets and private public etc

    #    - process_output
    #    - create
    #    - deacc_fluxes
    #    - retrieve

