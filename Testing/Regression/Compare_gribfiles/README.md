# Testcase - Grib file comparison

This testcase is composed of a number of comparisons of grib files from two different flex_extract versions. 


## Description

A single test run tests if there are the same number of files and the files have the same names. 
The test also checks if the files of each version have the same number of grib messages. It also uses the command line program "grib_compare" to check the equality of grib message headers. A comparison of the statistics of each grib message is also done with "grib_compare".
 


Manually retrieve test data?



## Usage

python test_cmp_grib_files.py -r <path-to-reference-files> -n <path-to-new-files>  -p <file-pattern> 

e.g. python test_cmp_grib_file.py -r 7.0.4/EA5/ -n 7.1/EA5/ -p 'EA*'

## Author
 Anne Philipp


## License
    (C) Copyright 2014-2019.

    SPDX-License-Identifier: CC-BY-4.0

    This work is licensed under the Creative Commons Attribution 4.0
    International License. To view a copy of this license, visit
    http://creativecommons.org/licenses/by/4.0/ or send a letter to
    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
