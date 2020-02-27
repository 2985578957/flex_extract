#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pytest

sys.path.append("../python")
import _config

def test_path_localpython():
    assert os.path.exists(_config.PATH_LOCAL_PYTHON) == 1

def test_path_flexextract():
    assert os.path.exists(_config.PATH_FLEXEXTRACT_DIR) == 1

def test_path_flexextract_name():
    version = _config._VERSION_STR
    flexextract_name = 'flex_extract_v' + version
    assert os.path.basename(_config.PATH_FLEXEXTRACT_DIR) == flexextract_name

def test_path_templates():
    assert os.path.exists(_config.PATH_TEMPLATES) == 1

def test_path_vtable():
    assert os.path.exists(_config.PATH_GRIBTABLE) == 1

def test_file_vtable():
    assert os.path.isfile(_config.PATH_GRIBTABLE) == 1

def test_path_run():
    assert os.path.exists(_config.PATH_RUN_DIR) == 1

def test_path_control():
    assert os.path.exists(_config.PATH_CONTROLFILES) == 1
