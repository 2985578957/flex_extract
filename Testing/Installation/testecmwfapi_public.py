#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pytest
from ecmwfapi import ECMWFDataServer

class TestECMWFApi:
    """
    """

    def test_public():
        server = ECMWFDataServer()

        server.retrieve({'dataset' : "interim",
                         'time'    : "00",
                         'date'    : "2013-09-01/to/2013-09-30",
                         'step'    : "0",
                         'type'    : "an",
                         'levtype' : "sfc",
                         'param'   : "165.128/41.128",
                         'grid'    : "0.75/0.75",
                         'target'  : "interim201309.grib"
                        })


