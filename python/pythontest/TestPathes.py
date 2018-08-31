#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pytest

sys.path.append("../")
import _config


def test_path_vtable():
    assert os.path.exists(_config.PATH_GRIBTABLE) == 1

def test_file_vtable():
    assert os.path.isfile(_config.PATH_GRIBTABLE) == 1

