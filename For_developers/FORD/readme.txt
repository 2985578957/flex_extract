HOW TO UPDATE THE AUTOMATED DOCUMENTATION OF THE FORTRAN CODE 

1. Install the FORtran Documenter from https://github.com/cmacmackin/ford
   Maybe read the documentation http://fortranwiki.org/fortran/show/FORD
2. Adapt the files in this directory if needed. fmw.md controls the the operation of FORD
3. Run Ford: ford fmw.md 

Note 1: Use --exclude_dir ../../Source/Fortran/<yourdir> if you have any subdir in the Fortran source directory containing Fortran source files (can be repeated)
