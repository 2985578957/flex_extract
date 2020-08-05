#!/bin/bash
#
# @Author: Anne Philipp
#
# @Date: September, 10 2018
#
# @Description: 
#    This file defines the flex_extract's available installation
#    parameters and puts them together for the call of the actual 
#    python installation script. It also does some checks to 
#    guarantee necessary parameters were set.
#
# @Licence:
#    (C) Copyright 2014-2020.
#
#    SPDX-License-Identifier: CC-BY-4.0
#
#    This work is licensed under the Creative Commons Attribution 4.0
#    International License. To view a copy of this license, visit
#    http://creativecommons.org/licenses/by/4.0/ or send a letter to
#    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#
# -----------------------------------------------------------------
# AVAILABLE COMMANDLINE ARGUMENTS TO SET
#
# THE USER HAS TO SPECIFY THESE PARAMETERS
#
TARGET='ecgate'
MAKEFILE='makefile_ecgate'
ECUID='<username>'
ECGID='<groupID>'
GATEWAY='<gatewayname>'
DESTINATION='<username>@genericSftp'
INSTALLDIR=None
JOB_TEMPLATE=''
CONTROLFILE='CONTROL_CERA'
# -----------------------------------------------------------------
#
# AFTER THIS LINE THE USER DOES NOT HAVE TO CHANGE ANYTHING !!!
#
# -----------------------------------------------------------------

# PATH TO INSTALLATION SCRIPT
script="Source/Python/install.py"

# INITIALIZE EMPTY PARAMETERLIST
parameterlist=""

# CHECK IF ON ECMWF SERVER; 
if [[ $HOST == *"ecgb"* ]] || [[ $HOST == *"cca"* ]] || [[ $HOST == *"ccb"* ]]; then
# LOAD PYTHON3 MODULE
  module load python3
fi 

# DEFAULT PARAMETERLIST
if [ -n "$TARGET" ]; then
  parameterlist=" --target=$TARGET"
else
  echo "ERROR: No installation target specified."
  echo "EXIT WITH ERROR"
  exit
fi

# CHECK FOR MORE PARAMETER 
if [ "$TARGET" == "ecgate" ] || [ "$TARGET" == "cca" ] || [ "$TARGET" == "ccb" ]; then
  # check if necessary Parameters are set
  if [ -z "$ECUID" ] || [ -z "$ECGID" ] || [ "$ECUID" == "<username>" ] || [ "$ECGID" == "<groupID>" ] ; then
    echo "ERROR: At least one of the following parameters are not properly set: ECUID or ECGID!"
    echo "EXIT WITH ERROR"
    exit
  else
    parameterlist+=" --ecuid=$ECUID --ecgid=$ECGID --gateway=$GATEWAY --destination=$DESTINATION"
  fi
  if [ -z "$GATEWAY" ] || [ -z "$DESTINATION" ] || [ "$GATEWAY" == "<gatewayname>" ] || [ "$DESTINATION" == "<username>@genericSftp" ] ; then
    echo "WARNING: Not setting parameters GATEWAY and DESTINATION means there will be no file transfer to local gateway server."
  fi
fi
if [ -n "$MAKEFILE" ]; then
  parameterlist+=" --makefile=$MAKEFILE"
fi
if [ -n "$FLEXPARTDIR" ]; then # not empty
  parameterlist+=" --flexpartdir=$FLEXPARTDIR"
fi
if [ -n "$JOB_TEMPLATE" ]; then
  parameterlist+=" --job_template=$JOB_TEMPLATE"
fi
if [ -n "$CONTROLFILE" ]; then
  parameterlist+=" --controlfile=$CONTROLFILE"
fi

# -----------------------------------------------------------------
# CALL INSTALLATION SCRIPT WITH DETERMINED COMMANDLINE ARGUMENTS

$script $parameterlist

