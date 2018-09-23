#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import pipes
import pytest

sys.path.append('../python')
import _config
from mods.tools import (get_cmdline_arguments, read_ecenv, clean_up, my_error,
                        normal_exit, product, silent_remove, init128,
                        to_param_id, get_list_as_string, make_dir,
                        put_file_to_ecserver, submit_job_to_ecserver)


class TestTools():
    '''
    '''

    def test_get_cmdline_arguments(self):
        cmd_dict_control = {'start_date':'20180101',
                            'end_date':'20180101',
                            'date_chunk':'3',
                            'basetime':'12',
                            'step':'1',
                            'levelist':'1/to/10',
                            'area':'50/10/60/20',
                            'inputdir':'../work',
                            'outputdir':'../work',
                            'flexpart_root_scripts':'../',
                            'ppid':'1234',
                            'job_template':'job.sh',
                            'queue':'ecgate',
                            'controlfile':'CONTROL.WORK',
                            'debug':'1',
                            'request':'0'}

        sys.argv = ['dummy.py',
                    '--start_date=20180101',
                    '--end_date=20180101',
                    '--date_chunk=3',
                    '--basetime=12',
                    '--step=1',
                    '--levelist=1/to/10',
                    '--area=50/10/60/20',
                    '--inputdir=../work',
                    '--outputdir=../work',
                    '--flexpart_root_scripts=../',
                    '--ppid=1234',
                    '--job_template=job.sh',
                    '--queue=ecgate',
                    '--controlfile=CONTROL.WORK',
                    '--debug=1',
                    '--request=0']

        results = get_cmdline_arguments()

        assert cmd_dict_control == vars(results)

    def test_init128(self):
        table128 = init128(_config.PATH_GRIBTABLE)
        expected = {'078': 'TCLW', '130': 'T', '034': 'SST'}
        # check a sample of parameters which must have been read in
        result = all((k in table128 and table128[k]==v) for k,v in expected.iteritems())
        assert result == True

    def test_to_param_id(self):
        table128 = init128(_config.PATH_GRIBTABLE)
        pars = to_param_id("T/SP/LSP/SSHF", table128)
        for par in pars:
            assert par in [130, 134, 142, 146]

    def test_my_error(self):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            my_error(['${USER}', 'anne.philipp@univie.ac.at'], 'Failed!')
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_read_ecenv(self):
        envs_ref = {'ECUID': 'km4a',
                    'ECGID': 'at',
                    'GATEWAY': 'srvx8.img.univie.ac.at',
                    'DESTINATION': 'annep@genericSftp'
                   }
        envs = read_ecenv(os.getcwd() + '/TestData/ECMWF_ENV')

        assert envs_ref == envs

    def test_clean_up(self):

        assert True

    def test_normal_exit(self):
        assert True

    def test_product(self):
        assert True

    def test_success_silent_remove(self, capfd):
        testfile = 'testfile.test'
        open(testfile, 'w').close()
        silent_remove(testfile)
        out, err = capfd.readouterr()
        assert os.path.isfile(testfile) == False
        assert out == ''

    def test_failnotexist_silent_remove(self, capfd):
        testfile = 'testfile.test'
        silent_remove(testfile)
        out, err = capfd.readouterr()
        assert os.path.isfile(testfile) == False
        assert out == ''

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_failany_silent_remove(self):
        testfile = 'testfileany.test'
        with pytest.raises(OSError) as pytest_wrapped_e:
            silent_remove(testfile)
        #out, err = capfd.readouterr()
        #assert os.path.isfile(testfile) == False
        #assert out == ''

    def test_success_get_list_as_string(self):
        list_object =  [1, 2, 3, '...', 'testlist']
        list_as_string = '1, 2, 3, ..., testlist'
        assert list_as_string == get_list_as_string(list_object)

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_fail_get_list_as_string(self):
        list_object =  [1, 2, 3, '...', 'testlist']
        list_as_string = '1, 2, 3, ..., testlist'
        with pytest.raises(Exception) as pytest_wrapped_e:
            result = get_list_as_string(list_object)
        assert result == list_as_string

    def test_warningexist_make_dir(self, capfd):
        testdir = 'TestData'
        make_dir(testdir)
        out, err = capfd.readouterr()
        assert out.strip() == 'WARNING: Directory {0} already exists!'.format(testdir)

    def test_failany_make_dir(self):
        testdir = '/test' # force a permission denied error
        with pytest.raises(OSError) as pytest_wrapped_e:
            make_dir(testdir)
        assert pytest_wrapped_e.type == OSError

    def test_success_make_dir(self):
        testdir = 'testing_mkdir'
        make_dir(testdir)
        assert os.path.exists(testdir) == True
        os.rmdir(testdir)

    def test_fail_put_file_to_ecserver(self):
        ecuid=os.environ['ECUID']
        ecgid=os.environ['ECGID']
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            put_file_to_ecserver('TestData/', 'testfil.txt',
                                 'ecgate', ecuid, ecgid)
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == '... ECACCESS-FILE-PUT FAILED!'

    def test_success_put_file_to_ecserver(self):
        ecuid=os.environ['ECUID']
        ecgid=os.environ['ECGID']
        result = put_file_to_ecserver('TestData/', 'testfile.txt',
                                      'ecgate', ecuid, ecgid)
        assert result == ''

    @pytest.mark.msuser_pw
    @pytest.mark.skip(reason="easier to ignore for now - implement in final version")
    def test_fullsuccess_put_file_to_ecserver(self):
        ecuid=os.environ['ECUID']
        ecgid=os.environ['ECGID']
        put_file_to_ecserver('TestData/', 'testfile.txt', 'ecgate', ecuid, ecgid)
        assert subprocess.call(['ssh', ecuid+'@ecaccess.ecmwf.int' ,
                                'test -e ' +
                                pipes.quote('/home/ms/'+ecgid+'/'+ecuid)]) == 0

    def test_fail_submit_job_to_ecserver(self):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            submit_job_to_ecserver('ecgate', 'job.ksh')
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == '... ECACCESS-JOB-SUBMIT FAILED!'

    def test_success_submit_job_to_ecserver(self):
        result = submit_job_to_ecserver('ecgate', 'TestData/testfile.txt')
        assert result.strip().isdigit() == True

