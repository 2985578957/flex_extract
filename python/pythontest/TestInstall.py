#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import os
import inspect
sys.path.append('../python')
import install


class TestTools(unittest.TestCase):
    '''
    '''

    def setUp(self):
        pass


    def test_mk_tarball(self):
        ecd = os.path.dirname(os.path.abspath(inspect.getfile(
            inspect.currentframe()))) + '/../'
        #print ecd
        install.mk_tarball(ecd)



if __name__ == "__main__":
    unittest.main()