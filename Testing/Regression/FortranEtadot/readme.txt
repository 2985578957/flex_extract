HOW TO DO REGRESSION TESTS OF THE FORTRAN CODE

1. Go to flex_extract/Testing/Regression/FortranEtadot (if not yet there)
2. Download the tarball containing the input files and reference outputs
2. Untar the tarball
3. Create a working directory: mkdir Work
4. Compile the unmodified Fortran code with makefile_fast and makefile_debug
   (is in flex_extract/Source/Fortran); you may use "build" for that.
5. Run a regression test to see whether the current Fortran code gives
   output consistent with the reference output.
   If not, carefully check why (machine-dependent small deviation?)
   The output from the regression run is in 'Outputs' (automatically created).
   If you need a new reference, you could remove or rename 'Outputs_ref', 
   and then run
   ./mk_outputdirs.sh
   ./run_ref.sh
   to create a new reference version. 
6. Work on the code and use the 'run_regrtest.sh' script to test your results.

Note 1: The regression tests except those with "high" in their name will
      altogether run in about 1 minute. The "high" tests (hemispherical data)
      can take many minutes and also require up to ca. 20 GB of memory.
      Therefore, the script can be invoked as
      ./run_ref.sh omithigh
      to omit the "high" tests. For single development steps this should be
      sufficient. When you are satisfied, run the "high" tests at the end.
Note 2: The test scripts contain
      export OMP_NUM_THREADS=4 # you may want to change this
      export OMP_PLACES=cores
      You should set OMP_NUM_THREADS to the number of physical cores of your
      test machine or less.
      OMP environment variables are explained on
      https://gcc.gnu.org/onlinedocs/libgomp/#toc-OpenMP-Environment-Variables
