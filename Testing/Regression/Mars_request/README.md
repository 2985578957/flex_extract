# Testcase - Mars request comparison

This testcase is composed of a number of comparisons of mars requests from two different flex_extract versions.

## Description

A single test compares the content of mars requests from two flex_extract versions. It checks for equal number of columns in the requests, if both versions have the same number of requests and the same request content.

The CONTROL files to be tested are stored in the CONTROL - directory. The corresponding mars request files of the previous version are stored in the directory 7.0.4. These are the references for version 7.1. During the execution of this test, the mars request files for version 7.1 are created and stored ( overwritten ) in directory 7.1. Results of the tests are stored in log files in the Log dir. Some extra output is printed on standard output. 

A log message could look like: 

Compare mars requests between version 7.0.4 and version 7.1 : 
... CONTROL_OD.OPER.highres.gauss_mr ... OK!
... CONTROL_OD.OPER.highres.eta_mr ... OK!
... CONTROL_OD.OPER.global.025_mr ... OK!
... CONTROL_OD.OPER.FC.twiceaday_mr ... OK!
... CONTROL_OD.OPER.FC.36hours_mr ... OK!
... CONTROL_OD.OPER.4V.operational_mr ... OK!
... CONTROL_OD.ENFO.PF_mr ... FAILED!
...     Inconsistency happend to be in column: step

... CONTROL_OD.ENFO.CF_mr ... FAILED!
...     Inconsistency happend to be in column: step

... CONTROL_OD.ELDA.FC.eta.ens.double_mr ... FAILED!
...     Inconsistency happend to be in column: date

... CONTROL_EI_mr ... OK!
... CONTROL_EI.public_mr ... OK!
... CONTROL_EA5_mr ... OK!
... CONTROL_EA5.public_mr ... OK!
... CONTROL_EA5.highres_mr ... OK!
... CONTROL_CV_mr ... OK!
... CONTROL_CF_mr ... OK!
... CONTROL_CERA_mr ... OK!
... CONTROL_CERA.public_mr ... OK!




## Usage

python test_cmp_mars_requests.py <previous-version> <version-to-be-tested>

e.g. python test_cmp_mars_requests.py 7.0.4 7.1

## Author
    Anne Philipp


## License
    (C) Copyright 2014-2019.

    SPDX-License-Identifier: CC-BY-4.0

    This work is licensed under the Creative Commons Attribution 4.0
    International License. To view a copy of this license, visit
    http://creativecommons.org/licenses/by/4.0/ or send a letter to
    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
