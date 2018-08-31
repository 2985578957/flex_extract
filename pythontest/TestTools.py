#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import os
sys.path.append('../python')
from tools import init128, to_param_id, my_error, read_ecenv


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


    def test_to_param_id(self):
        '''
        '''
        table128 = init128('../grib_templates/ecmwf_grib1_table_128')
        pars = to_param_id("T/SP/LSP/SSHF", table128)
        for par in pars:
            self.assertIn(par, [130, 134, 142, 146])

    def test_error_notifcation(self):
        '''
        '''
        with self.assertRaises(SystemExit) as re:
            my_error(['${USER}', 'anne.philipp@univie.ac.at'], 'Failed!')
        self.assertEqual(re.exception.code, 1)

    def test_read_ecenv(self):

        envs_ref = {'ECUID': 'km4a',
                    'ECGID': 'at',
                    'GATEWAY': 'srvx8.img.univie.ac.at',
                    'DESTINATION': 'annep@genericSftp'
                   }
        envs = read_ecenv(os.getcwd() + '/TestData/ECMWF_ENV')

        self.assertDictEqual(envs_ref, envs)





if __name__ == "__main__":
    unittest.main()