#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pytest

sys.path.append('../Python')
from Classes.ControlFile import ControlFile
from Mods.tools import get_cmdline_args


class TestInput():
    '''
    Test class to test the reading of commandline arguments and
    control file.
    '''
    # ToDo
    # create more tests for input
    # 1. nur controlfile reading
    # 2. check of parameter

    @classmethod
    def setup_class(self):
        # Default values for ArgumentParser
        self.args = {'start_date':None,
                     'end_date':None,
                     'date_chunk':None,
                     'basetime':None,
                     'step':None,
                     'levelist':None,
                     'area':None,
                     'inputdir':None,
                     'outputdir':None,
                     'flexpart_root_scripts':None,
                     'ppid':None,
                     'job_template':'job.temp',
                     'queue':None,
                     'controlfile':'CONTROL.test',
                     'debug':0,
                     }
        #sys.argv = ['dummy.py', '--start_date=20180101', '--debug=1',
        #            '--step=0/to/11/BY/3', '--area=20./20./0./90.']
        sys.argv = ['dummy.py', '--start_date=20180101']

        self.args = get_cmdline_args()

        self.c = ControlFile('../../Testing/Regression/Unit/Testfiles/CONTROL.test')

        self.c.assign_args_to_control(self.args)

        self.c.check_conditions()


    def test_args_reading(self):

        sys.argv = ['dummy.py', '--start_date=20180101', '--debug=1',
                    '--step=0/to/11/BY/3', '--area=20./20./0./90.']

        arguments = get_cmdline_args()

        args_exp = {'start_date':'20180101',
                    'end_date':None,
                    'date_chunk':None,
                    'basetime':None,
                    'step':'0/to/11/BY/3',
                    'levelist':None,
                    'area':'20./20./0./90.',
                    'inputdir':None,
                    'outputdir':None,
                    'flexpart_root_scripts':None,
                    'ppid':None,
                    'job_template':'job.temp',
                    'queue':None,
                    'controlfile':'CONTROL.test',
                    'debug':1,
                    }

        assert vars(arguments) == args_exp


    def test_args_assignment(self):

        import collections

        # expected parametervalue:
        exp_dict = {
                    'accuracy': '16',
                    'addpar': ['186', '187', '188', '235', '139', '39'],
                    'area': None,
                    'basetime': None,
                    'controlfile': 'CONTROL.test',
                    'cwc': 0,
                    'date_chunk': 3,
                    'debug': 0,
                    'destination': None,
                    'dpdeta': '1',
                    'dtime': '3',
                    'ecfsdir': 'ectmp:/${USER}/econdemand/',
                    'ecgid': None,
                    'ecmwfdatadir': '/raid60/nas/tmc/Anne/Interpolation/flexextract/flexextract/python/../',
                    'ecstorage': '0',
                    'ectrans': '1',
                    'ecuid': None,
                    'end_date': '20180101',
                    'eta': '0',
                    'etadiff': '0',
                    'etapar': 77,
                    'exedir': '/raid60/nas/tmc/Anne/Interpolation/flexextract/flexextract/python/../src/',
                    'expver': '1',
                    'flexpart_root_scripts': '/raid60/nas/tmc/Anne/Interpolation/flexextract/flexextract/python/../',
                    'format': 'GRIB1',
                    'gateway': None,
                    'gauss': '1',
                    'grib2flexpart': '0',
                    'grid': '5000',
                    'inputdir': '../work',
                    'job_template': 'job.temp',
                    'left': '-15000',
                    'level': '60',
                    'levelist': '55/to/60',
                    'lower': '30000',
                    'mailfail': ['${USER}'],
                    'mailops': ['${USER}'],
                    'makefile': None,
                    'marsclass': 'EI',
                    'maxstep': 11,
                    'number': 'OFF',
                    'omega': '0',
                    'omegadiff': '0',
                    'outputdir': '../work',
                    'prefix': 'EI',
                    'resol': '63',
                    'right': '45000',
                    'smooth': '0',
                    'start_date': '20180101',
                    'step': ['00', '01', '02', '03', '04', '05', '00', '07', '08', '09', '10', '11', '00', '01', '02', '03', '04', '05', '00', '07', '08', '09', '10', '11'],
                    'stream': 'OPER',
                    'target': None,
                    'time': ['00', '00', '00', '00', '00', '00', '06', '00', '00', '00', '00', '00', '12', '12', '12', '12', '12', '12', '18', '12', '12', '12', '12', '12'],
                    'type': ['AN', 'FC', 'FC', 'FC', 'FC', 'FC', 'AN', 'FC', 'FC', 'FC', 'FC', 'FC', 'AN', 'FC', 'FC', 'FC', 'FC', 'FC', 'AN', 'FC', 'FC', 'FC', 'FC', 'FC'],
                    'upper': '75000',
                    'wrf': 0}

        exp_dict = collections.OrderedDict(sorted(exp_dict.items()))
        cdict = collections.OrderedDict(sorted(vars(self.c).items()))

        # remove content which isn't comparable for different users
        # or different operating systems
        del cdict['ecfsdir_expanded']
        del cdict['mailops_expanded']
        del cdict['mailfail_expanded']

        #print 'cdict\n', cdict
        #print 'exp_dict\n', exp_dict

        #assert cdict == exp_dict
        assert cdict == exp_dict

        return

    @classmethod
    def teardown_class(self):
 
        return
