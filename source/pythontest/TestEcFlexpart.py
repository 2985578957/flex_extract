#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import pytest

sys.path.append('../python')
from classes.EcFlexpart import EcFlexpart

class TestEcFlexpart():
    '''
    '''

    def test_init(self):
        # create an instance of EcFlexpart and get a dictionary of the
        # class attributes, compare this dict with an expected dict!
        assert True == True

    def test_write_namelist(self):
        # simple
        assert True == True

    def test_retrieve(self):
        # not sure how to check
        assert True == True


# these functions should test the output and compare the results with an output
# of the old version and check if there are no differences!!!
# also check for errors?! Or check if it works for alle datasets and private public etc

    #    - process_output
    #    - create
    #    - deacc_fluxes
