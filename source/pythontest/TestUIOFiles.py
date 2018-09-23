#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pytest

sys.path.append('../python')
from classes.UioFiles import UioFiles


class TestUioFiles():
    '''
    Test class to test the UIOFiles methods.
    '''

    def test_listFiles(self):
        '''
        @Description:
            Test the listFiles method from class UIOFiles.

        @Input:
            self: instance of TestClass
                Class to test the UIOFiles methods.

        @Return:
            <nothing>
        '''
        # set comparison information
        self.testpath = os.path.join(os.path.dirname(__file__), 'TestDir')
        self.expected = ['FCGG__SL.20160410.40429.16424.grb',
                             'FCOG__ML.20160410.40429.16424.grb',
                             'FCSH__ML.20160410.40429.16424.grb',
                             'OG_OROLSM__SL.20160410.40429.16424.grb',
                             'FCOG_acc_SL.20160409.40429.16424.grb',
                             'FCOG__SL.20160410.40429.16424.grb',
                             'FCSH__SL.20160410.40429.16424.grb']

        # Initialise and collect filenames
        files = UioFiles(self.testpath, '*.grb')
        # get the basename to just check for equality of filenames
        filelist = [os.path.basename(f) for f in files.files]
        # comparison of expected filenames against the collected ones
        assert sorted(self.expected) == sorted(filelist)

        return

