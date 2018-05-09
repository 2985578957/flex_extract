#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
sys.path.append('../python')
import UIOFiles


class TestUIOFiles(unittest.TestCase):
    '''
    Test class to test the UIOFiles methods.
    '''

    def setUp(self):
        '''
        @Description:
            Prepare test case. Initialize comparing filelist and
            the test path.

        @Input:
            self: instance of TestUIOFiles
                Class to test the UIOFiles methods.

        @Return:
            <nothing>
        '''
        self.testpath = os.path.join(os.path.dirname(__file__), 'TestDir')
        self.expected = ['FCGG__SL.20160410.40429.16424.grb',
                         'FCOG__ML.20160410.40429.16424.grb',
                         'FCSH__ML.20160410.40429.16424.grb',
                         'OG_OROLSM__SL.20160410.40429.16424.grb',
                         'FCOG_acc_SL.20160409.40429.16424.grb',
                         'FCOG__SL.20160410.40429.16424.grb',
                         'FCSH__SL.20160410.40429.16424.grb']

        return

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

        # Initialise and collect filenames
        files = UIOFiles.UIOFiles(['.grb'])
        files.listFiles(self.testpath, '*')
        # get the basename to just check for equality of filenames
        filelist = [os.path.basename(f) for f in files.files]
        # comparison of expected filenames against the collected ones
        self.assertItemsEqual(self.expected, filelist)

        return

if __name__ == "__main__":
    unittest.main()