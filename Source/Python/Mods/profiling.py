#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#************************************************************************
# ToDo AP
# - check license of book content
#************************************************************************
#*******************************************************************************
#
# @Author: Anne Philipp (University of Vienna)
#
# @Date: March 2018
#
# @License:
#    (C) Copyright 2020.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Program functionality:
#    This module is not part of flex_extract. It is just used for testing and
#    performance analysis of some functions.
#
# @Program Content:
#    - timefn
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
from __future__ import print_function

from functools import wraps
import time

# ------------------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------------
def timefn(func):
    '''
    @Description:
        Decorator function. It takes the inner function as an argument.
    '''
    @wraps(func)
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

        time1 = time.time()
        result = func(*args, **kwargs)
        time2 = time.time()
        print("@timefn:" + func.__name__ + " took " +
              str(time2 - time1) + " seconds")

        return result

    return measure_time
