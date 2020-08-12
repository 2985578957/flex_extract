#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ecmwfapi import ECMWFDataServer

server = ECMWFDataServer()

server.retrieve({
 'stream'    : "enda",
 'levtype'   : "sfc",
 'param'     : "165.128/166.128/167.128",
 'dataset'   : "cera20c",
 'step'      : "0",
 'grid'      : "1./1.",
 'time'      : "00/06/12/18",
 'date'      : "2000-07-01/to/2000-07-31",
 'type'      : "an",
 'class'     : "ep",
 'number'    : "0",
 'target'    : "download_cera20c_ecmwfapi.grib"
})
