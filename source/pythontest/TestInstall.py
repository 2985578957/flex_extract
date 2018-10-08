#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import inspect
import pytest

sys.path.append('../python')
import _config
import install
from mods.tools import make_dir, silent_remove


class TestTools():
    '''
    '''


    #    - main
    #    - get_install_cmdline_arguments
    #    - install_via_gateway
    #!    - mk_tarball
    #!    - un_tarball
    #!    - mk_env_vars
    #    - mk_compilejob
    #    - mk_job_template
    #    - delete_convert_build
    #    - make_convert_build

    def test_mk_tarball_local(self):
        import tarfile

        ecd = _config.PATH_FLEXEXTRACT_DIR + os.path.sep

        # list comparison files for tarball content
        tar_test_dir = os.path.join(_config.PATH_TEST_DIR +
                                    os.path.sep + 'TestInstallTar')
        tar_test_file = os.path.join(tar_test_dir,
                                     'flex_extract_v7.1_local.tar')
        with tarfile.open(tar_test_file, 'r') as tar_handle:
            comparison_list = tar_handle.getnames()

        # create test tarball and list its content files
        tarballname = _config.FLEXEXTRACT_DIRNAME + '_localtest.tar'
        install.mk_tarball(ecd + tarballname, 'local')
        with tarfile.open(ecd + tarballname, 'r') as tar_handle:
            tar_content_list = tar_handle.getnames()

        # remove test tar file from flex_extract directory
        os.remove(ecd + tarballname)

        # test if comparison filelist is equal to the
        # filelist of tarball content
        assert sorted(comparison_list) == sorted(tar_content_list)

    def test_mk_tarball_ecgate(self):
        import tarfile

        ecd = _config.PATH_FLEXEXTRACT_DIR + os.path.sep

        # list comparison files for tarball content
        tar_test_dir = os.path.join(_config.PATH_TEST_DIR +
                                    os.path.sep + 'TestInstallTar')
        tar_test_file = os.path.join(tar_test_dir,
                                     'flex_extract_v7.1_ecgate.tar')
        with tarfile.open(tar_test_file, 'r') as tar_handle:
            comparison_list = tar_handle.getnames()

        # create test tarball and list its content files
        tarballname = _config.FLEXEXTRACT_DIRNAME + '_ecgatetest.tar'
        install.mk_tarball(ecd + tarballname, 'ecgate')
        with tarfile.open(ecd + tarballname, 'r') as tar_handle:
            tar_content_list = tar_handle.getnames()

        # remove test tar file from flex_extract directory
        os.remove(ecd + tarballname)

        # test if comparison filelist is equal to the
        # filelist of tarball content
        assert sorted(comparison_list) == sorted(tar_content_list)

    def test_un_tarball(self):
        import tarfile
        import shutil

        ecd = _config.PATH_FLEXEXTRACT_DIR + os.path.sep

        # list comparison files for tarball content
        tar_test_dir = os.path.join(_config.PATH_TEST_DIR +
                                        os.path.sep + 'TestInstallTar')
        tar_test_fedir = os.path.join(tar_test_dir, 'flex_extract_v7.1_ecgate')
        comparison_list = []
        for path, subdirs, files in os.walk(tar_test_fedir):
            for name in files:
                if 'tar' not in name:
                    comparison_list.append(os.path.relpath(
                        os.path.join(path, name), tar_test_fedir))

        # untar in test directory
        test_dir = os.path.join(tar_test_dir, 'test_untar')
        make_dir(test_dir)
        os.chdir(test_dir)
        tarballname = _config.FLEXEXTRACT_DIRNAME + '_ecgate.tar'
        install.un_tarball(os.path.join(tar_test_dir, tarballname))
        tarfiles_list = []
        for path, subdirs, files in os.walk(test_dir):
            for name in files:
                tarfiles_list.append(os.path.relpath(
                    os.path.join(path, name), test_dir))

        # test for equality
        assert sorted(tarfiles_list) == sorted(comparison_list)

        # clean up temp test dir
        shutil.rmtree(test_dir)

    def test_mk_env_vars(self):
        import filecmp

        # comparison file
        testfile = os.path.join(_config.PATH_TEST_DIR,'TestData',
                                'ECMWF_ENV.test')

        # create test ECMWF_ENV file
        install.mk_env_vars('testuser',
                            'testgroup',
                            'gateway.test.ac.at',
                            'user@destination')

        assert filecmp.cmp(testfile, _config.PATH_ECMWF_ENV, shallow=False)

        # delte test file
        silent_remove(_config.PATH_ECMWF_ENV)

    def test_mk_compilejob(self):
        import filecmp

        # comparison file
        testfile = os.path.join(_config.PATH_TEST_DIR,'TestData',
                                    'compilejob.test')

        # create
        install.mk_compilejob('Makefile.TEST',
                              '',
                              'testuser',
                              'testgroup',
                              'fp_root_test_path')

        finalfile = os.path.join(_config.PATH_JOBSCRIPTS,
                              _config.FILE_INSTALL_COMPILEJOB)
        assert filecmp.cmp(testfile, finalfile, shallow=False)

        # delete test file
        silent_remove(finalfile)
