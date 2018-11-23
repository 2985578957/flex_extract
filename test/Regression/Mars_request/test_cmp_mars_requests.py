#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comparison of the created MARS requests of two flex_extract versions.

There will be comparisons for the given standard control files in the
"Controls" - directory. The result of the comparison is stored in the
"Log" - directory with an individual timestamp in the format %Y-%m-%d_%H-%M-%S.
(E.g. log_2018-11-23_12-42-29)
The MARS request files are named such that it contains the name of the
corresponding control files "<control-identifier>.csv" (e.g. EA5_mr.csv).
They are stored in the corresponding version directory and have the same
name in both versions.

The script should be called like:

    python test_cmp_mars_requests.py <old_version_number> <new_version_number>

Note
----
The MARS request files from the older version have to be in place already.
The request files of the new/current version will be generated automatically
with the "run_local.sh" script.
It is necessary to have a directory named after the version number of
flex_extract. For example: "7.0.3" and "7.1".

Example
-------
    python test_cmp_mars_requests.py 7.0.3 7.1
"""

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import sys
import pandas as pd
import subprocess
import shutil
from datetime import datetime

sys.path.append('../../../source/python')
import _config

# ------------------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------------
def test_mr_column_equality(mr_old, mr_new):
    '''Check if old and new version of MARS requests have the same
    amount of columns.

    If the number is not equal and/or the column names are not equal
    an error message is stored in global variable "err_msg".

    Parameters
    ----------
    mr_old : :obj:`pandas DataFrame`
        Contains the mars requests from the old version of
        flex_extract.

    mr_new : :obj:`pandas DataFrame`
        Contains the mars requests from the new version of
        flex_extract.

    Return
    ------
    bool
        True if successful, False otherwise.
    '''
    global err_msg
    if (len(mr_old.columns.values) == len(mr_new.columns.values) and
        sorted(mr_old.columns.values) == sorted(mr_new.columns.values)):
        return True
    else:
        err_msg = 'Unequal number and/or column names!\n'
        return False


def test_mr_number_equality(mr_old, mr_new):
    '''Check if old and new version have the same number of requests.

    If the number is not equal an error message is stored in
    global variable "err_msg".

    Parameters
    ----------
    mr_old : :obj:`pandas DataFrame`
        Contains the mars requests from the old version of
        flex_extract.

    mr_new : :obj:`pandas DataFrame`
        Contains the mars requests from the new version of
        flex_extract.

    Return
    ------
    bool
        True if successful, False otherwise.
    '''
    global err_msg
    if len(mr_new.index) == len(mr_old.index):
        return True
    else:
        err_msg = 'Unequal number of mars requests!\n'
        return False

def test_mr_content_equality(mr_old, mr_new):
    '''Check if old and new version have the same request contents.

    If the content in a column is not equal an error message is stored in
    global variable "err_msg", recording the column.

    Parameters
    ----------
    mr_old : :obj:`pandas DataFrame`
        Contains the mars requests from the old version of
        flex_extract.

    mr_new : :obj:`pandas DataFrame`
        Contains the mars requests from the new version of
        flex_extract.

    Return
    ------
    bool
        True if successful, False otherwise.
    '''
    global err_msg
    lresult = None
    columns = list(mr_new.columns.values)
    del columns[columns.index('target')]
    for col in columns:
        if mr_new[col].equals(mr_old[col]):
            lresult = True
        else:
            err_msg += 'Unconsistency happend to be in column: ' + col + '\n'
            return False
    return lresult


if __name__ == '__main__':

    # basic values for paths and versions
    control_path = 'Controls'
    log_path = 'Log'
    old_dir = sys.argv[1] # e.g. '7.0.3'
    new_dir = sys.argv[2] # e.g. '7.1'
    mr_filename = 'mars_requests.csv'

    # have to be set to "True" in the beginnning
    # so it only fails if a test fails
    lfinal = True

    # prepare log file for this test run
    currenttime = datetime.now()
    time_str = currenttime.strftime('%Y-%m-%d_%H-%M-%S')
    logfile = os.path.join(log_path, 'log_' + time_str)
    with open(logfile, 'aw') as f:
        f.write('Compare mars requests between version ' + old_dir +
                ' and version ' + new_dir + ' : \n')

    # list all controlfiles
    controls =  os.listdir(control_path)

    # loop over controlfiles
    for c in controls:
        # empty error message for every controlfile
        err_msg = ''

        # start flex_extract with controlfiles to get mars_request files
        shutil.copy(os.path.join(control_path,c), _config.PATH_CONTROLFILES)
        subprocess.check_output(['run_local.sh', new_dir, c])
        os.remove(os.path.join(_config.PATH_CONTROLFILES,c))

        # cut-of "CONTROL_" string and mv mars_reqeust file
        # to a name including control specific name
        mr_name = c.split('CONTROL_')[1] + '.csv'
        shutil.move(os.path.join(new_dir,mr_filename), os.path.join(new_dir,mr_name))

        # read both mr files (old & new)
        mr_old = pd.read_csv(os.path.join(old_dir, mr_name))
        mr_new = pd.read_csv(os.path.join(new_dir, mr_name))

        mr_old.columns = mr_old.columns.str.strip()
        mr_new.columns = mr_new.columns.str.strip()

        # do tests on mr files
        lcoleq = test_mr_column_equality(mr_old, mr_new)
        lnoeq = test_mr_number_equality(mr_old, mr_new)
        lcoeq = test_mr_content_equality(mr_old, mr_new)

        # check results for mr file
        lfinal = lfinal and lcoleq and lnoeq and lcoeq

        # write out result to logging file
        with open(logfile, 'aw') as f:
            if lcoleq and lnoeq and lcoeq:
                f.write('... ' + c + ' ... OK!' + '\n')
            else:
                f.write('... ' + c + ' ... FAILED!' + '\n')
                if err_msg:
                    f.write('... \t' + err_msg + '\n')

    # exit with success or error status
    if lfinal:
        sys.exit(0) # 'SUCCESS'
    else:
        sys.exit(1) # 'FAIL'
