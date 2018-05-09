#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# TODO AP
# - add description of file
# - check of license of book content
#************************************************************************
"""
@Author: Anne Philipp (University of Vienna)

@Date: March 2018

@License:
    (C) Copyright 2018.

    This software is licensed under the terms of the Apache Licence Version 2.0
    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

@Requirements:
    A standard python 2.6 or 2.7 installation

@Description:
    ...
"""
# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
from functools import wraps
import time

# ------------------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------------
def timefn(fn):
    '''
    @Description:
        Decorator function. It takes the inner function as an argument.
    '''
    @wraps(fn)
    def measure_time(*args, **kwargs):
        '''
        @Descripton:
            Passes the arguments through fn for execution. Around the
            execution of fn the time is captured to execute the fn function
            and prints the result along with the function name.

            This is taken from the book "High Performance Python" from
            Micha Gorelick and Ian Ozsvald, O'Reilly publisher, 2014,
            ISBN: 978-1-449-36159-4

        @Input:
            *args: undefined
                A variable number of positional arguments.

            **kwargs: undefined
                A variable number of key/value arguments.

        @Return:
            <nothing>
        '''

        t1 = time.time()
        result = fn(*args, **kwargs)
        t2 = time.time()
        print("@timefn:" + fn.func_name + " took " + str(t2 - t1) + " seconds")

        return result

    return measure_time