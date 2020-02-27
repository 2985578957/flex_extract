#!/usr/bin/env python3
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

Licence:
--------
    (C) Copyright 2014-2019.

    SPDX-License-Identifier: CC-BY-4.0

    This work is licensed under the Creative Commons Attribution 4.0
    International License. To view a copy of this license, visit
    http://creativecommons.org/licenses/by/4.0/ or send a letter to
    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

Example
-------
    python test_cmp_mars_requests.py 7.0.4 7.1
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

sys.path.append('../../../Source/Python')
import _config
from  Mods.tools import init128

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
    mr_new = trim_all_columns(mr_new)
    mr_old = trim_all_columns(mr_old)
    for col in columns:
        if mr_new[col].equals(mr_old[col]):
            lresult = True
        else:
            err_msg += 'Inconsistency in column: ' + col + '\n'
            print("THERE SEEMS TO BE AN ERROR:")
            print("CONTENT OF NEW VERSION:")
            print(mr_new[col])
            print("CONTENT OF OLD VERSION:")
            print(mr_old[col])
            return False
    return lresult


def trim_all_columns(df):
    """
    Trim whitespace from ends of each value across all series in dataframe
    """
    trim_strings = lambda x: x.strip() if isinstance(x, str) else x
    return df.applymap(trim_strings)

def convert_param_numbers(mr_old):
    """
    Convert the numbers parameter into integers with 3 digits.
    """

    if str(mr_old).strip() != "OFF" and mr_old != None and '/' in str(mr_old) :
        numbers = mr_old.split('/')
        number = str(int(numbers[0])).zfill(3)+'/TO/'+str(int(numbers[2])).zfill(3)

        return number

    return mr_old

def convert_param_step(mr_old):
    """
    For pure forecast with steps greater than 23 hours, the older versions 
    writes out a list of steps instead with the syntax 'to' and 'by'. 
    e.g. 000/003/006/009/012/015/018/021/024/027/030/033/036
    
    Convert this to 0/to/36/by/3
    """

    #if 'to' in str(mr_old) and 'by' in str(mr_old):
    #    steps = mr_old.split('/')
    #    step = []
    #    for i in range(int(steps[0]),int(steps[2]),int(steps[4])):
    #        step.append(str(int(i)).zfill(2))
    #    return '/'.join(step)
    
    if not mr_old.isdigit() and 'to' not in mr_old.lower():
        if int(mr_old.split('/')[-1]) > 23:
    
            steps = mr_old.split('/')
            dtime = int(steps[1]) - int(steps[0])
            
            nsteps = str(int(steps[1]))+'/to/'+str(int(steps[-1]))+'/by/'+str(int(dtime))
            return nsteps            
    
    return mr_old

def to_param_id(pars, table):
    '''Transform parameter names to parameter ids with ECMWF grib table 128.

    Parameters
    ----------
    pars : str
        Addpar argument from CONTROL file in the format of
        parameter names instead of ids. The parameter short
        names are sepearted with "/" and they are passed as
        one single string.

    table : dict
        Contains the ECMWF grib table 128 information.
        The key is the parameter number and the value is the
        short name of the parameter.

    Return
    ------
    ipar : list of int
        List of addpar parameters from CONTROL file transformed to
        parameter ids in the format of integer.
    '''
    if not pars:
        return []
    if not isinstance(pars, str):
        pars=str(pars)

    cpar = pars.upper().split('/')
    spar = []
    for par in cpar:
        par = par.strip()
        for k, v in table.items():
            if par.isdigit():
                par = str(int(par)).zfill(3)
            if par == k or par == v:
                spar.append(k + '.128')
                break
        else:
            print('\n\Warning: par ' + par + ' not found in table 128\n\n”')

    return '/'.join(str(l) for l in spar)



if __name__ == '__main__':

    # basic values for paths and versions
    control_path = 'Controls'
    log_path = 'Log'
    old_dir = sys.argv[1] # e.g. '7.0.4'
    new_dir = sys.argv[2] # e.g. '7.1'
    mr_filename = 'mars_requests.csv'

    # have to be set to "True" in the beginnning
    # so it only fails if a test fails
    lfinal = True

    # prepare log file for this test run
    currenttime = datetime.now()
    time_str = currenttime.strftime('%Y-%m-%d_%H-%M-%S')
    logfile = os.path.join(log_path, 'log_' + time_str)
    with open(logfile, 'a') as f:
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

        # convert names in old to ids
        table128 = init128(_config.PATH_GRIBTABLE)
        #print mr_old['param']

        # some format corrections are necessary to compare older versions with 7.1
        mr_old['param'] = mr_old['param'].apply(to_param_id, args=[table128])
        mr_old['number'] = mr_old['number'].apply(convert_param_numbers)  
        if '142' in mr_old.loc[0,'param']: # if flux request
            mr_old.loc[0,'step'] = convert_param_step(mr_old.loc[0,'step'])

        print('Results: ', c)

        # do tests on mr files
        lcoleq = test_mr_column_equality(mr_old, mr_new)
        lnoeq = test_mr_number_equality(mr_old, mr_new)
        lcoeq = test_mr_content_equality(mr_old, mr_new)

        # check results for mr file
        lfinal = lfinal and lcoleq and lnoeq and lcoeq

        # write out result to logging file
        with open(logfile, 'a') as f:
            if lcoleq and lnoeq and lcoeq:
                f.write('... ' + c + ' ... OK!' + '\n')
            else:
                f.write('... ' + c + ' ... FAILED!' + '\n')
                if err_msg:
                    f.write('...    ' + err_msg + '\n')

        exit

    # exit with success or error status
    if lfinal:
        sys.exit(0) # 'SUCCESS'
    else:
        sys.exit(1) # 'FAIL'
