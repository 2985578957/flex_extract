#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cdsapi

c = cdsapi.Client()

c.retrieve('reanalysis-era5-single-levels',
{ 
  "product_type":'reanalysis',
  "area": [40.0,-10.0,30.0,10.0],
  "year": "2018",
  "month": "08",
  "day": ['8','10'],
  "grid": [0.5,0.5],
  "param": "167.128",
  "time": ['00', '06', '12', '18'],
  "format":'grib2',
}, 'download_era5_flux_cdsapi.grib')

