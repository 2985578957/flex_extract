#!/bin/bash

# Testing environment for Fortran code in flex_extract v7
# Create reference output dirs for test cases found in "Inputs"
#
# Copyright Petra Seibert, 2019
# SPDX-License-Identifier: MIT-0 


for d in `ls Inputs`; do
  for exe in 'debug' 'fast'; do
    newdir='Outputs/Output_ref_'${d}'_'${exe}
    mkdir -pv $newdir
  done
done
