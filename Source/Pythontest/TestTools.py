#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# for the gateway tests, the env vars of ECUID and ECGID have to be set upfront

import os
import sys
import errno
#from exceptions import OSError
import subprocess
import pipes

try:
    import exceptions
except ImportError:
    import builtins

import pytest
from mock import patch, call
#from mock import PropertyMock


import _config
from . import _config_test
from Classes.ControlFile import ControlFile
from Mods.tools import (none_or_str, none_or_int, get_cmdline_args,
                        read_ecenv, clean_up, my_error, send_mail,
                        normal_exit, product, silent_remove,
                        init128, to_param_id, get_list_as_string, make_dir,
                        put_file_to_ecserver, submit_job_to_ecserver)

class TestTools(object):
    """Test the tools module."""

    def setup_method(self):
        self.testdir = _config_test.PATH_TEST_DIR
        self.testfilesdir = _config_test.PATH_TESTFILES_DIR
        self.c = ControlFile(self.testdir+'/Controls/CONTROL.test')

    def test_nonestr_none_or_int(self):
        assert None == none_or_int('None')

    def test_intstr_none_or_int(self):
        assert 42 == none_or_int('42')

    def test_nonestr_none_or_str(self):
        assert None == none_or_str('None')

    def test_anystr_none_or_str(self):
        assert 'test' == none_or_str('test')

    def test_fail_get_cmdline_arguments(self):
        sys.argv = ['dummy.py', '--wrong=1']
        with pytest.raises(SystemExit):
            results = get_cmdline_args()

    def test_default_get_cmdline_arguments(self):
        cmd_dict_control = {'start_date': None,
                            'end_date': None,
                            'date_chunk': None,
                            'basetime': None,
                            'step': None,
                            'levelist': None,
                            'area': None,
                            'inputdir': None,
                            'outputdir': None,
                            'job_template': None,
                            'job_chunk': None,
                            'ppid': None,
                            'job_template': 'job.temp',
                            'queue': None,
                            'controlfile': 'CONTROL_EA5',
                            'debug': None,
                            'public': None,
                            'request': None,
                            'oper': None,
                            'rrint': None}

        sys.argv = ['dummy.py']

        results = get_cmdline_args()

        assert cmd_dict_control == vars(results)

    def test_input_get_cmdline_arguments(self):
        cmd_dict_control = {'start_date': '20180101',
                            'end_date': '20180101',
                            'date_chunk': 3,
                            'basetime': 12,
                            'step': '1',
                            'levelist': '1/to/10',
                            'area': '50/10/60/20',
                            'inputdir': '../work',
                            'outputdir': None,
                            'ppid': '1234',
                            'job_template': 'job.sh',
                            'queue': 'ecgate',
                            'controlfile': 'CONTROL.WORK',
                            'debug': 1,
                            'public': None,
                            'request': 0,
                            'rrint': 0,
                            'job_chunk': None,
                            'oper': 0}

        sys.argv = ['dummy.py',
                    '--start_date=20180101',
                    '--end_date=20180101',
                    '--date_chunk=3',
                    '--basetime=12',
                    '--step=1',
                    '--levelist=1/to/10',
                    '--area=50/10/60/20',
                    '--inputdir=../work',
                    '--outputdir=None',
                    '--ppid=1234',
                    '--job_template=job.sh',
                    '--queue=ecgate',
                    '--controlfile=CONTROL.WORK',
                    '--debug=1',
                    '--public=None',
                    '--request=0',
                    '--rrint=0',
                    '--job_chunk=None',
                    '--oper=0']

        results = get_cmdline_args()

        assert cmd_dict_control == vars(results)

    def test_success_init128(self):
        table128 = init128(_config.PATH_GRIBTABLE)
        expected_sample = {'078': 'TCLW', '130': 'T', '034': 'SST'}
        # check a sample of parameters which must have been read in
        assert all((k in table128 and table128[k] == v)
                   for k, v in expected_sample.items())

    @patch('builtins.open', side_effect=[OSError(errno.EEXIST)])
    def test_fail_open_init128(self, mock_openfile):
        with pytest.raises(SystemExit):
            table128 = init128(_config.PATH_GRIBTABLE)

    @pytest.mark.parametrize(
        'ipar_str, opar_listint',
        [('SP/LSP/SSHF', [134, 142, 146]),
         ('T', [130]),
         ('', []),
         (None, []),
         ('testtest', []),
         ('130/142', [130, 142]),
         (130, [130]),
         (50.56, [])])
    def test_to_param_id(self, ipar_str, opar_listint):
        table128 = init128(_config.PATH_GRIBTABLE)
        ipars = to_param_id(ipar_str, table128)
        assert sorted(ipars) == sorted(opar_listint)

    @patch('traceback.format_stack', return_value='empty trace')
    @patch('Mods.tools.send_mail', return_value=0)
    def test_success_my_error(self, mock_mail, mock_trace, capfd):
        with pytest.raises(SystemExit):
            my_error('Failed!')
            out, err = capfd.readouterr()
            assert out == "Failed!\n\nempty_trace\n"

    @patch('subprocess.Popen')
    @patch('os.getenv', return_value='user')
    @patch('os.path.expandvars', return_value='user')
    def test_success_userenv_twouser_send_mail(self, mock_os, mock_env, mock_popen, capfd):
        mock_popen.return_value = subprocess.Popen(["echo", "Hello Test!"],
                                                   stdout=subprocess.PIPE)
        send_mail(['${USER}', 'any_user'], 'ERROR', message='error mail')
        out, err = capfd.readouterr()
        assert out == 'Email sent to user\nEmail sent to user\n'

    @patch('subprocess.Popen')
    @patch('os.path.expandvars', return_value='any_user')
    def test_success_send_mail(self, mock_os,  mock_popen, capfd):
        mock_popen.return_value = subprocess.Popen(["echo", "Hello Test!"],
                                                   stdout=subprocess.PIPE)
        send_mail(['any-user'], 'ERROR', message='error mail')
        out, err = capfd.readouterr()
        assert out == 'Email sent to any_user\n'

    @patch('subprocess.Popen', side_effect=[ValueError, OSError])
    @patch('os.path.expandvars', return_value='any_user')
    def test_fail_valueerror_send_mail(self, mock_osvar, mock_popen):
        with pytest.raises(SystemExit): # ValueError
            send_mail(['any-user'], 'ERROR', message='error mail')
        with pytest.raises(SystemExit): # OSError
            send_mail(['any-user'], 'ERROR', message='error mail')

    def test_success_read_ecenv(self):
        envs_ref = {'ECUID': 'testuser',
                    'ECGID': 'testgroup',
                    'GATEWAY': 'gateway.test.ac.at',
                    'DESTINATION': 'user@destination'
                   }
        envs = read_ecenv(self.testfilesdir + '/ECMWF_ENV.test')

        assert envs_ref == envs

    @patch('builtins.open', side_effect=[OSError(errno.EPERM)])
    def test_fail_read_ecenv(self, mock_open):
        with pytest.raises(SystemExit):
            read_ecenv('any_file')

    @patch('glob.glob', return_value=[])
    @patch('Mods.tools.silent_remove')
    def test_empty_clean_up(self, mock_rm, mock_clean):
        clean_up(self.c)
        mock_rm.assert_not_called()

    @patch('glob.glob', return_value=['any_file','EIfile'])
    @patch('os.remove', return_value=0)
    def test_success_clean_up(self, mock_rm, mock_glob):

        self.c.prefix = 'EI'
        self.c.ecapi = False
        clean_up(self.c)
        mock_rm.assert_has_calls([call('any_file')])
        mock_rm.reset_mock()


    def test_default_normal_exit(self, capfd):
        normal_exit()
        out, err = capfd.readouterr()
        assert out == 'Done!\n'

    def test_message_normal_exit(self, capfd):
        normal_exit('Hi there!')
        out, err = capfd.readouterr()
        assert out == 'Hi there!\n'

    def test_int_normal_exit(self, capfd):
        normal_exit(42)
        out, err = capfd.readouterr()
        assert out == '42\n'

    @pytest.mark.parametrize(
        'input1, input2, output_list',
        [('ABC','xy',[('A','x'),('A','y'),('B','x'),('B','y'),('C','x'),('C','y')]),
         (range(1), range(1), [(0,0),(0,1),(1,0),(1,1)])])
    def test_success_product(self, input1, input2, output_list):
        index = 0
        for prod in product(input1, input2):
            assert isinstance(prod, tuple)
            assert prod == output_list[index]
            index += 1

    @pytest.mark.parametrize(
        'input1, input2, output_list',
        [(1,1,(1,1))])
    def test_fail_product(self, input1, input2, output_list):
        index = 0
        with pytest.raises(SystemExit):
            for prod in product(input1, input2):
                assert isinstance(prod, tuple)
                assert prod == output_list[index]
                index += 1

    def test_success_silent_remove(self):
        testfile = self.testfilesdir + 'test.txt'
        open(testfile, 'w').close()
        silent_remove(testfile)
        assert os.path.isfile(testfile) == False

    @patch('os.remove', side_effect=OSError(errno.ENOENT))
    def test_fail_notexist_silent_remove(self, mock_rm):
        with pytest.raises(OSError) as pytest_wrapped_e:
            silent_remove('any_dir')
            assert pytest_wrapped_e.e.errno == errno.ENOENT

    @patch('os.remove', side_effect=OSError(errno.EEXIST))
    def test_fail_any_silent_remove(self, mock_rm):
        with pytest.raises(OSError):
            silent_remove('any_dir')

    @pytest.mark.parametrize(
        'input_list, output_list',
        [([],''),
         ([1, 2, 3.5, '...', 'testlist'], '1, 2, 3.5, ..., testlist'),
         ('2', '2')])
    def test_success_get_list_as_string(self, input_list, output_list):
        assert output_list == get_list_as_string(input_list)

    @patch('os.makedirs', side_effect=[OSError(errno.EEXIST)])
    def test_warning_exist_make_dir(self, mock_make):
        with pytest.raises(OSError) as pytest_wrapped_e:
            make_dir('existing_dir')
            assert pytest_wrapped_e.e.errno == errno.EEXIST

    @patch('os.makedirs', side_effect=OSError)
    def test_fail_any_make_dir(self, mock_makedir):
        with pytest.raises(OSError):
            make_dir('any_dir')

    def test_fail_empty_make_dir(self):
        with pytest.raises(OSError):
            make_dir('')

    def test_success_make_dir(self):
        testdir = '/testing_mkdir'
        make_dir(self.testdir + testdir)
        assert os.path.exists(self.testdir + testdir) == True
        os.rmdir(self.testdir + testdir)


    @patch('subprocess.check_output', side_effect=[subprocess.CalledProcessError(1,'test')])
    def test_fail_put_file_to_ecserver(self, mock_co):
        with pytest.raises(SystemExit):
            put_file_to_ecserver(self.testfilesdir, 'test_put_to_ecserver.txt',
                                 'ecgate', 'ex_ECUID', 'ex_ECGID')

    @patch('subprocess.check_output', return_value=0)
    def test_general_success_put_file_to_ecserver(self, mock_co):
        result = put_file_to_ecserver(self.testfilesdir, 'test_put_to_ecserver.txt',
                                      'ecgate', 'ex_ECUID', 'ex_ECGID')
        assert result == None

    @pytest.mark.msuser_pw
    @pytest.mark.gateway
    @pytest.mark.skip(reason="easier to ignore for now - implement in final version")
    def test_full_success_put_file_to_ecserver(self):
        ecuid = os.environ['ECUID']
        ecgid = os.environ['ECGID']
        put_file_to_ecserver(self.testfilesdir, 'test_put_to_ecserver.txt',
                             'ecgate', ecuid, ecgid)
        assert subprocess.call(['ssh', ecuid+'@ecaccess.ecmwf.int' ,
                                'test -e ' +
                                pipes.quote('/home/ms/'+ecgid+'/'+ecuid)]) == 0

    @patch('subprocess.check_output', side_effect=[subprocess.CalledProcessError(1,'test'),
                                                   OSError])
    def test_fail_submit_job_to_ecserver(self, mock_co):
        with pytest.raises(SystemExit):
            job_id = submit_job_to_ecserver('ecgate', 'job.ksh')

    @pytest.mark.msuser_pw
    @pytest.mark.gateway
    @pytest.mark.skip(reason="easier to ignore for now - implement in final version")
    def test_success_submit_job_to_ecserver(self):
        job_id = submit_job_to_ecserver('ecgate',
                                        os.path.join(self.testfilesdir,
                                                     'test_put_to_ecserver.txt'))
        assert job_id.strip().isdigit() == True


