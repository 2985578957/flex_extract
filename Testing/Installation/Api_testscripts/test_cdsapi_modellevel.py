#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cdsapi

c = cdsapi.Client()

c.retrieve('reanalysis-era5-complete',
{
  'class'   : 'ea',
  'expver'  : '1',
  'stream'  : 'oper',
  'type'    : 'fc',
  'step'    : '3/to/12/by/3',
  'param'   : 't',
  'levtype' : 'ml',
  'levelist': '135/to/137',
  'date'    : '2013-01-01',
  'time'    : '06/18',
  'area'    : '50/-5/40/5',
  'grid'    : '1.0/1.0',
  'format'  : 'grib',
}, 'download_era5_cdsapi.grib')
