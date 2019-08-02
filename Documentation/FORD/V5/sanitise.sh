#!/bin/bash

# Sanitise the output of FORD so that it uses a local copy of the CC-BY img
# rather than downloading it, and comment out the mathjax.js library being 
# fetched (from mathjax.com) for data protection reasons.

# Copyright Petra Seibert, 2019
# SPDX-License-Identifier: MIT-0 

doc=`grep output_dir fmw.md|cut -d\  -f2`
old='https://i.creativecommons.org/l/by/4.0/80x15.png'
new='80x15.png'
for f in `find $doc -type f -exec grep -l ${old} {} \; ` ; do

  depth=`echo $f | tr -cd '/' | wc -c`
  depth=$(( depth - 2))
  sub=$new
  while (( --depth >= 0 )); do
    sub='../'$sub
  done
  sed -i "s=${old}=${sub}=g" $f
  echo 'remove cc link in ' $f
  
done
searchstring='https://cdn.mathjax.org'
old='<script src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>'
new='<!-- <script src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script> -->'
for f in `find $doc -type f -exec grep -l ${searchstring} {} \; ` ; do

  sed -i "s+${old}+${new}+g" $f
  echo 'comment out mathjax link in ' $f
  
done

