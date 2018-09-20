#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import os
import inspect
sys.path.append('../')
import _config
import install
from tools import make_dir


class TestTools(unittest.TestCase):
    '''
    '''

    def setUp(self):
        pass

    #    - main
    #    - get_install_cmdline_arguments
    #    - install_via_gateway
    #!    - mk_tarball
    #!    - un_tarball
    #    - mk_env_vars
    #    - mk_compilejob
    #    - mk_job_template
    #    - delete_convert_build
    #    - make_convert_build

    def test_mk_tarball(self):
        import tarfile

        ecd = _config.PATH_FLEXEXTRACT_DIR + os.path.sep

        # list comparison files for tarball content
        tar_test_dir = os.path.join(_config.PATH_TEST_DIR +
                                    os.path.sep + 'TestInstallTar')
        tar_test_fedir = os.path.join(tar_test_dir, 'flex_extract_v7.1')

        comparison_list = []
        for path, subdirs, files in os.walk(tar_test_fedir):
            for name in files:
                if 'tar' not in name:
                    comparison_list.append(os.path.relpath(os.path.join(path, name), tar_test_fedir))

        # create test tarball and list its content files
        tarballname = _config.FLEXEXTRACT_DIRNAME + '_test.tar'
        install.mk_tarball(ecd + tarballname)
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
        tar_test_fedir = os.path.join(tar_test_dir, 'flex_extract_v7.1')
        comparison_list = []
        for path, subdirs, files in os.walk(tar_test_fedir):
            for name in files:
                if 'tar' not in name:
                    comparison_list.append(os.path.relpath(os.path.join(path, name), tar_test_fedir))

        # untar in test directory
        test_dir = os.path.join(tar_test_dir, 'test_untar')
        make_dir(test_dir)
        os.chdir(test_dir)
        tarballname = _config.FLEXEXTRACT_DIRNAME + '.tar'
        install.un_tarball(os.path.join(tar_test_dir, tarballname))
        tarfiles_list = []
        for path, subdirs, files in os.walk(test_dir):
            for name in files:
                tarfiles_list.append(os.path.relpath(os.path.join(path, name), test_dir))

        # test for equality
        assert sorted(tarfiles_list) == sorted(comparison_list)

        # clean up temp test dir
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    unittest.main()
