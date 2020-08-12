#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os
import inspect
import subprocess
import tarfile
import errno
import shutil
from genshi.template import TemplateLoader
from genshi.template.eval import UndefinedError

try:
    import exceptions
except ImportError:
    import builtins
import pytest
from mock import patch
import mock

sys.path.append('../Python')
import _config
from . import _config_test
from install import (mk_tarball, un_tarball, mk_env_vars, mk_compilejob,
                     mk_job_template)

from Mods.tools import make_dir, silent_remove

#    - main
#    - get_install_cmdline_arguments
#    - install_via_gateway
#    - delete_convert_build
#    - make_convert_build

class TestInstall():
    '''
    '''
    @classmethod
    def setup_class(self):
        self.testdir = _config_test.PATH_TEST_DIR
        self.testfilesdir = _config_test.PATH_TESTFILES_DIR
        self.testinstalldir = _config_test.PATH_TESTINSTALL_DIR

        # make test tarballs from shell script
        subprocess.check_output([os.path.join(self.testinstalldir,
                                              'mk_install_tar.sh')])

        # un tar the test tarballs from shell script
#        subprocess.check_output([os.path.join(self.testinstalldir,
#                                            'un_install_tar.sh')])



    @patch('tarfile.open', side_effect=[tarfile.TarError, OSError])
    def test_fail_mk_tarball_local(self, mock_open):
        import tarfile
       # mock_open.side_effekt = tarfile.TarError
        ecd = _config.PATH_FLEXEXTRACT_DIR + os.path.sep
        # create test tarball and list its content files
        tarballname = _config.FLEXEXTRACT_DIRNAME + '_localtest.tar'

        with pytest.raises(SystemExit):
            mk_tarball(ecd + tarballname, 'local')


    def test_success_mk_tarball_local(self):
        ecd = _config.PATH_FLEXEXTRACT_DIR + os.path.sep

        # list comparison files for tarball content
        tar_test_dir = os.path.join(self.testdir, 'InstallTar')
        tar_test_file = os.path.join(tar_test_dir,
                                     'flex_extract_v7.1_local.tar')
        with tarfile.open(tar_test_file, 'r') as tar_handle:
            comparison_list = tar_handle.getnames()

        # create test tarball and list its content files
        tarballname = _config.FLEXEXTRACT_DIRNAME + '_localtest.tar'
        mk_tarball(ecd + tarballname, 'local')
        with tarfile.open(ecd + tarballname, 'r') as tar_handle:
            tar_content_list = tar_handle.getnames()

        # remove test tar file from flex_extract directory
        #os.remove(ecd + tarballname)

        # test if comparison filelist is equal to the
        # filelist of tarball content
        assert sorted(comparison_list) == sorted(tar_content_list)

    def test_success_mk_tarball_ecgate(self):
        ecd = _config.PATH_FLEXEXTRACT_DIR + os.path.sep

        # list comparison files for tarball content
        tar_test_dir = os.path.join(self.testdir, 'InstallTar')
        tar_test_file = os.path.join(tar_test_dir,
                                     'flex_extract_v7.1_ecgate.tar')
        with tarfile.open(tar_test_file, 'r') as tar_handle:
            comparison_list = tar_handle.getnames()

        # create test tarball and list its content files
        tarballname = _config.FLEXEXTRACT_DIRNAME + '_ecgatetest.tar'
        mk_tarball(ecd + tarballname, 'ecgate')
        with tarfile.open(ecd + tarballname, 'r') as tar_handle:
            tar_content_list = tar_handle.getnames()

        # remove test tar file from flex_extract directory
        os.remove(ecd + tarballname)

        # test if comparison filelist is equal to the
        # filelist of tarball content
        assert sorted(comparison_list) == sorted(tar_content_list)

    @patch('tarfile.open', side_effect=[tarfile.TarError, OSError])
    def test_fail_un_tarball(self, mock_open):
        with pytest.raises(SystemExit):
            un_tarball('testpath')

    def test_success_ecgate_un_tarball(self):
        ecd = _config.PATH_FLEXEXTRACT_DIR + os.path.sep

        # list comparison files for tarball content
        tar_test_dir = os.path.join(self.testdir, 'InstallTar')
        tarballname = _config.FLEXEXTRACT_DIRNAME + '_ecgate.tar'
        with tarfile.open(os.path.join(tar_test_dir, tarballname), 'r') as tar_handle:
            comparison_list = tar_handle.getnames()

        # untar in test directory
        test_dir = os.path.join(tar_test_dir, 'test_ecgate')
        make_dir(test_dir)
        os.chdir(test_dir)
        un_tarball(os.path.join(tar_test_dir, tarballname))
        tarfiles_list = []
        for path, subdirs, files in os.walk(test_dir):
            for name in files:
                tarfiles_list.append(os.path.relpath(
                    os.path.join(path, name), test_dir))

        # test for equality
        assert sorted(tarfiles_list) == sorted(comparison_list)

    def test_success_local_un_tarball(self):
        ecd = _config.PATH_FLEXEXTRACT_DIR + os.path.sep

        # list comparison files for tarball content
        tar_test_dir = os.path.join(self.testdir, 'InstallTar')
        tarballname = _config.FLEXEXTRACT_DIRNAME + '_local.tar'
        with tarfile.open(os.path.join(tar_test_dir, tarballname), 'r') as tar_handle:
            comparison_list = tar_handle.getnames()

        # untar in test directory
        test_dir = os.path.join(tar_test_dir, 'test_local')
        make_dir(test_dir)
        os.chdir(test_dir)
        un_tarball(os.path.join(tar_test_dir, tarballname))
        tarfiles_list = []
        for path, subdirs, files in os.walk(test_dir):
            for name in files:
                tarfiles_list.append(os.path.relpath(
                    os.path.join(path, name), test_dir))

        # test for equality
        assert sorted(tarfiles_list) == sorted(comparison_list)

    @patch('_config.PATH_ECMWF_ENV', _config_test.PATH_TESTFILES_DIR+'/ecmwf_test')
    def test_success_mk_env_vars(self):
        import filecmp

        cmp_file = os.path.join(self.testfilesdir,
                                'ECMWF_ENV.test')

        mk_env_vars('testuser',
                    'testgroup',
                    'gateway.test.ac.at',
                    'user@destination')

        assert filecmp.cmp(cmp_file, _config.PATH_ECMWF_ENV, shallow=False)

        silent_remove(_config.PATH_ECMWF_ENV)

    @patch('genshi.template.TemplateLoader', side_effect=[OSError])
    def test_fail_load_mk_env_vars(self, mock_generate):
        with pytest.raises(SystemExit):
            mk_env_vars('testuser',
                        'testgroup',
                        'gateway.test.ac.at',
                        'user@destination')

    def test_fail_generate_mk_env_vars(self):
        with patch('genshi.template.TemplateLoader.load') as MockHelper:
            MockHelper.return_value.generate.side_effect = UndefinedError('undefined')
            with pytest.raises(SystemExit):
                mk_env_vars('testuser',
                            'testgroup',
                            'gateway.test.ac.at',
                            'user@destination')

    @patch('_config.FILE_INSTALL_COMPILEJOB', _config_test.PATH_TESTFILES_DIR+'/compilejob_test.ksh')
    def test_success_mk_compilejob(self):
        import filecmp

        testfile = os.path.join(self.testfilesdir,
                                'compilejob.test')

        mk_compilejob('Makefile.TEST',
                      'testuser',
                      'testgroup',
                      'fp_root_test_path')

        finalfile = os.path.join(_config.PATH_JOBSCRIPTS,
                                 _config.FILE_INSTALL_COMPILEJOB)
        assert filecmp.cmp(testfile, finalfile, shallow=False)

        silent_remove(finalfile)

    @patch('genshi.template.TemplateLoader', side_effect=[OSError])
    def test_fail_load_mk_compilejob(self, mock_generate):
        with pytest.raises(SystemExit):
            mk_compilejob('Makefile.TEST',
                          'testuser',
                          'testgroup',
                          'fp_root_test_path')

    def test_fail_generate_mk_compilejob(self):
        with patch('genshi.template.TemplateLoader.load') as MockHelper:
            MockHelper.return_value.generate.side_effect = UndefinedError('undefined')
            with pytest.raises(SystemExit):
                mk_compilejob('Makefile.TEST',
                              'testuser',
                              'testgroup',
                              'fp_root_test_path')

#    @patch('builtins.open', side_effect=[OSError(errno.EPERM)])
#    def test_fail_open_mk_compilejob(self, mock_open):
#        with pytest.raises(SystemExit):
#            mk_compilejob('Makefile.TEST',
#                          'testuser',
#                          'testgroup',
#                          'fp_root_test_path')

    @patch('_config.TEMPFILE_JOB', _config_test.PATH_TESTFILES_DIR+'/submitscript.template.test.comp')
    def test_success_mk_job_template(self):
        import filecmp

        testfile = os.path.join(self.testfilesdir,
                                'submitscript.template.test')

        mk_job_template('testuser',
                        'testgroup',
#                        'gateway.test.ac.at',
#                        'dest@generic',
                        'fp_root_test_path')

        finalfile = os.path.join(_config.PATH_TEMPLATES,
                                 _config.TEMPFILE_JOB)
        assert filecmp.cmp(testfile, finalfile, shallow=False)

        silent_remove(finalfile)

    @patch('genshi.template.TemplateLoader', side_effect=[OSError])
    def test_fail_load_mk_job_template(self, mock_generate):
        with pytest.raises(SystemExit):
            mk_job_template('testuser',
                            'testgroup',
#                            'gateway.test.ac.at',
#                            'dest@generic',
                            'fp_root_test_path')

    def test_fail_generate_mk_job_template(self):
        with patch('genshi.template.TemplateLoader.load') as MockHelper:
            MockHelper.return_value.generate.side_effect = UndefinedError('undefined')
            with pytest.raises(SystemExit):
                mk_job_template('testuser',
                                'testgroup',
 #                               'gateway.test.ac.at',
 #                               'dest@generic',
                                'fp_root_test_path')

#    @patch('builtins.open', side_effect=[OSError(errno.EPERM)])
#    def test_fail_open_mk_job_template(self, mock_open):
#        with pytest.raises(SystemExit):
#            mk_job_template('testuser',
#                            'testgroup',
#                            'gateway.test.ac.at',
#                            'dest@generic',
#                            'fp_root_test_path')

    @classmethod
    def teardown_class(self):

        test_dir = os.path.join(self.testinstalldir,
                                _config.FLEXEXTRACT_DIRNAME + '_local')
#        shutil.rmtree(test_dir)
        test_dir = os.path.join(self.testinstalldir,
                                _config.FLEXEXTRACT_DIRNAME + '_ecgate')
#        shutil.rmtree(test_dir)

        test_dir = os.path.join(self.testinstalldir,
                                'test_local')
#        shutil.rmtree(test_dir)
        test_dir = os.path.join(self.testinstalldir,
                                'test_ecgate')
#        shutil.rmtree(test_dir)

        tar_file = os.path.join(self.testinstalldir,
                     _config.FLEXEXTRACT_DIRNAME + '_local.tar')
#        os.remove(tar_file)
        tar_file = os.path.join(self.testinstalldir,
                                _config.FLEXEXTRACT_DIRNAME + '_ecgate.tar')
#        os.remove(tar_file)
        pass
