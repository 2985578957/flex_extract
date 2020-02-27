#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pytest
from ecmwfapi import ECMWFService

class TestECMWFApi:
    """
    """

    def test_member():
        server = ECMWFService("mars")

        server.execute({'class'   : "ei",
                        'time'    : "00",
                        'date'    : "2013-09-01/to/2013-09-30",
                        'step'    : "0",
                        'type'    : "an",
                        'levtype' : "sfc",
                        'param'   : "165.128/41.128",
                        'grid'    : "0.75/0.75"},
                       "interim201309.grib")

