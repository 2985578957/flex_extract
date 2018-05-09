#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../python')
from Tools import init128, toparamId


class TestTools(unittest.TestCase):
    '''
    '''

    def setUp(self):
        pass

    def test_init128(self):
        '''
        '''
        table128 = init128('../grib_templates/ecmwf_grib1_table_128')
        expected = {'078': 'TCLW', '130': 'T', '034': 'SST'}
        # check a sample of parameters which must have been read in
        result = all((k in table128 and table128[k]==v) for k,v in expected.iteritems())
        self.assertEqual(result, True)


    def test_toparamId(self):
        '''
        '''
        table128 = init128('../grib_templates/ecmwf_grib1_table_128')
        pars = toparamId("T/SP/LSP/SSHF", table128)
        for par in pars:
            self.assertIn(par, [130, 134, 142, 146])


if __name__ == "__main__":
    unittest.main()