#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ecmwfapi import ECMWFService

server = ECMWFService('mars')

server.retrieve({
 'stream'    : "oper",
 'levtype'   : "sfc",
 'param'     : "165.128/166.128/167.128",
 'dataset'   : "interim",
 'step'      : "0",
 'grid'      : "0.75/0.75",
 'time'      : "00/06/12/18",
 'date'      : "2014-07-01/to/2014-07-31",
 'type'      : "an",
 'class'     : "ei",
 'target'    : "download_erainterim_ecmwfapi.grib"
})
