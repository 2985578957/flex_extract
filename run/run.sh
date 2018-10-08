#!/bin/bash
#
# @Author: Anne Philipp
#
# @Date: October, 4 2018
#
# @Description: 
#


# -----------------------------------------------------------------
# AVAILABLE COMMANDLINE ARGUMENTS TO SET
#
# THE USER HAS TO SPECIFY THESE PARAMETER
#

QUEUE=None
START_DATE='20120908'
END_DATE=None
DATE_CHUNK=None
BASETIME=None
STEP=None
LEVELIST=None
AREA=None
INPUTDIR='/nas/tmc/Anne/Interpolation/flexextract/flex_extract_v7.1/run/workspace/test3'
OUTPUTDIR=None
FLEXPART_ROOT_SCRIPTS=None 
PP_ID=None
JOB_TEMPLATE='job.temp' 
CONTROLFILE='CONTROL_EA5' 
DEBUG=1 
REQUEST=2
PUBLIC=0

# -----------------------------------------------------------------
#
# AFTER THIS LINE THE USER DOES NOT HAVE TO CHANGE ANYTHING !!!
#
# -----------------------------------------------------------------

# PATH TO SUBMISSION SCRIPT
pyscript=../source/python/submit.py

# INITIALIZE EMPTY PARAMETERLIST
parameterlist=""

# CHECK FOR MORE PARAMETER 
if [ -n "$START_DATE" ]; then
  parameterlist+=" --start_date=$START_DATE"
fi
if [ -n "$END_DATE" ]; then
  parameterlist+=" --end_date=$END_DATE"
fi
if [ -n "$DATE_CHUNK" ]; then
  parameterlist+=" --date_chunk=$DATE_CHUNK"
fi
if [ -n "$BASETIME" ]; then
  parameterlist+=" --basetime=$BASETIME"
fi
if [ -n "$STEP" ]; then
  parameterlist+=" --step=$STEP"
fi
if [ -n "$LEVELIST" ]; then
  parameterlist+=" --levelist=$LEVELIST"
fi
if [ -n "$AREA" ]; then
  parameterlist+=" --area=$AREA"
fi
if [ -n "$INPUTDIR" ]; then
  parameterlist+=" --inputdir=$INPUTDIR"
fi
if [ -n "$OUTPUTDIR" ]; then
  parameterlist+=" --outputdir=$OUTPUTDIR"
fi
if [ -n "$FLEXPART_ROOT_SCRIPTS" ]; then
  parameterlist+=" --flexpart_root_scripts=$FLEXPART_ROOT_SCRIPTS"
fi
if [ -n "$PP_ID" ]; then
  parameterlist+=" --ppid=$PP_ID"
fi
if [ -n "$JOB_TEMPLATE" ]; then
  parameterlist+=" --job_template=$JOB_TEMPLATE"
fi
if [ -n "$QUEUE" ]; then
  parameterlist+=" --queue=$QUEUE"
fi
if [ -n "$CONTROLFILE" ]; then
  parameterlist+=" --controlfile=$CONTROLFILE"
fi
if [ -n "$DEBUG" ]; then
  parameterlist+=" --debug=$DEBUG"
fi
if [ -n "$REQUEST" ]; then
  parameterlist+=" --request=$REQUEST"
fi
if [ -n "$PUBLIC" ]; then
  parameterlist+=" --public=$PUBLIC"
fi

# -----------------------------------------------------------------
# CALL INSTALLATION SCRIPT WITH DETERMINED COMMANDLINE ARGUMENTS

$pyscript $parameterlist

