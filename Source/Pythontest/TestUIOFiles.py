#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pytest
from mock import patch

from . import _config_test
sys.path.append('../Python')

from Classes.UioFiles import UioFiles


class TestUioFiles():
    """Test class to test the UIOFiles methods."""

    @classmethod
    def setup_class(self):
        """Setup status"""
        self.testpath = os.path.join(_config_test.PATH_TEST_DIR, 'Dir')
        # Initialise and collect filenames
        self.files = UioFiles(self.testpath, '*.grb')

    def test_listFiles(self):
        """Test the listFiles method from class UIOFiles."""
        # set comparison information
        self.expected = ['FCGG__SL.20160410.40429.16424.grb',
                         'FCOG__ML.20160410.40429.16424.grb',
                         'FCSH__ML.20160410.40429.16424.grb',
                         'OG_OROLSM__SL.20160410.40429.16424.grb',
                         'FCOG_acc_SL.20160409.40429.16424.grb',
                         'FCOG__SL.20160410.40429.16424.grb',
                         'FCSH__SL.20160410.40429.16424.grb']

        # get the basename to just check for equality of filenames
        filelist = [os.path.basename(f) for f in self.files.files]
        # comparison of expected filenames against the collected ones
        assert sorted(self.expected) == sorted(filelist)


    def test_delete_files(self):
        """Test if a file is deleted."""
        testfile = os.path.join(self.testpath, 'test.test')
        open(testfile, 'w').close()
        iofile = UioFiles(self.testpath, 'test.test')
        iofile.delete_files()
        assert [] == UioFiles(self.testpath, 'test.test').files


    def test_str_(self):
        """Test if list of file is correctly converted to string."""
        self.expected = "FCOG__ML.20160410.40429.16424.grb, "\
                        "FCOG__SL.20160410.40429.16424.grb, "\
                        "FCSH__ML.20160410.40429.16424.grb, "\
                        "FCSH__SL.20160410.40429.16424.grb, "\
                        "OG_OROLSM__SL.20160410.40429.16424.grb, "\
                        "FCGG__SL.20160410.40429.16424.grb, "\
                        "FCOG_acc_SL.20160409.40429.16424.grb"
        assert self.expected == self.files.__str__()
