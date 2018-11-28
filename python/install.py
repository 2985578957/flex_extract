#!/usr/bin/env python
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# Functionality provided: Prepare input 3D-wind fields in hybrid coordinates + surface fields for FLEXPART runs
#
# Creation: October  2014 - Anne Fouilloux - University of Oslo
# Extension November 2015 - Leopold Haimberger - University of Vienna for:
# - using the WebAPI also for general MARS retrievals
# - job submission on ecgate and cca
# - job templates suitable for twice daily operational dissemination
# - dividing retrievals of longer periods into digestable chunks
# - retrieve also longer term forecasts, not only analyses and short term forecast data
# - conversion into GRIB2
# - conversion into .fp format for faster execution of FLEXPART
#
#
# Further documentation may be obtained from www.flexpart.eu
#
# Requirements:
# in addition to a standard python 2.6 or 2.7 installation the following packages need to be installed
# ECMWF WebMARS, gribAPI with python enabled, emoslib, ecaccess web toolkit, all available from https://software.ecmwf.int/
# dateutils
# matplotlib (optional, for debugging)
#
#
import calendar
import shutil
import datetime
import time
import os,sys,glob
import subprocess
import inspect
# add path to submit.py to pythonpath so that python finds its buddies
localpythonpath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(localpythonpath)
from UIOTools import UIOFiles
from string import strip
from argparse import ArgumentParser,ArgumentDefaultsHelpFormatter
from GribTools import GribTools
from FlexpartTools import EIFlexpart, Control, install_args_and_control
from getMARSdata import getMARSdata
from prepareFLEXPART import prepareFLEXPART



def main():

    calledfromdir=os.getcwd()
    os.chdir(localpythonpath)
    args,c=install_args_and_control()
#    if c.outputdir[0]!='/':
#	c.outputdir=os.path.join(calledfromdir,c.outputdir)
#	c.inputdir=c.outputdir
    if args.install_target!=None:
        install_via_gateway(c,args.install_target)

    else:
        print 'Please specify installation target (local|ecgate|cca)'
        print 'use -h or --help for help'
    sys.exit()

def install_via_gateway(c,target):

    ecd=c.flexextractdir
    template=ecd+'python/compilejob.temp'
    job=ecd+'python/compilejob.ksh'
    fo=open(job,'w')
    with open(template) as f:
        fdata = f.read().split('\n')
        for data in fdata:
            if 'MAKEFILE=' in data:
                if c.makefile is not None:
                    data='export MAKEFILE='+c.makefile
            if 'FLEXPART_ROOT_SCRIPTS=' in data:
                if c.flexpart_root_scripts!='../':
                    data='export FLEXPART_ROOT_SCRIPTS='+c.flexpart_root_scripts
                else:
                    data='export FLEXPART_ROOT_SCRIPTS=$HOME'
            if target.lower()!='local':
                if '--workdir' in data:
                    data='#SBATCH --workdir=/scratch/ms/'+c.ecgid+'/'+c.ecuid
                if '##PBS -o' in data:
                    data='##PBS -o /scratch/ms/'+c.ecgid+'/'+c.ecuid+'flex_ecmwf.$Jobname.$Job_ID.out'
                if 'FLEXPART_ROOT_SCRIPTS=' in data:
                    if c.ec_flexpart_root_scripts!='../':
                        data='export FLEXPART_ROOT_SCRIPTS='+c.ec_flexpart_root_scripts
                    else:
                        data='export FLEXPART_ROOT_SCRIPTS=$HOME'

            fo.write(data+'\n')
    f.close()
    fo.close()

    if target.lower()!='local':
        template=ecd+'python/job.temp.o'
        with open(template) as f:
            fdata = f.read().split('\n')
        f.close()
        fo=open(template[:-2],'w')
        for data in fdata:
            if '--workdir' in data:
                data='#SBATCH --workdir=/scratch/ms/'+c.ecgid+'/'+c.ecuid
            if '##PBS -o' in data:
                data='##PBS -o /scratch/ms/'+c.ecgid+'/'+c.ecuid+'flex_ecmwf.$Jobname.$Job_ID.out'
            if  'export PATH=${PATH}:' in data:
                data+=c.ec_flexpart_root_scripts+'/flex_extract_v7.0.4/python'

            if 'cat>>' in data or 'cat >>' in data:
                i=data.index('>')
                fo.write(data[:i]+data[i+1:]+'\n')
                fo.write('GATEWAY '+c.gateway+'\n')
                fo.write('DESTINATION '+c.destination+'\n')
                fo.write('EOF\n')

            fo.write(data+'\n')
        fo.close()

        job=ecd+'python/ECMWF_ENV'
        fo=open(job,'w')
        fo.write('ECUID '+c.ecuid+'\n')
        fo.write('ECGID '+c.ecgid+'\n')
        fo.write('GATEWAY '+c.gateway+'\n')
        fo.write('DESTINATION '+c.destination+'\n')
        fo.close()



    if target.lower()=='local':
        # compile CONVERT2
        if c.flexpart_root_scripts==None or c.flexpart_root_scripts=='../':
            print 'Warning: FLEXPART_ROOT_SCRIPTS has not been specified'
            print 'Only CONVERT2 will be compiled in '+ecd+'/../src'
        else:
            c.flexpart_root_scripts=os.path.expandvars(os.path.expanduser(c.flexpart_root_scripts))
            if os.path.abspath(ecd)!=os.path.abspath(c.flexpart_root_scripts):
                os.chdir('/')
                p=subprocess.check_call(['tar','-cvf',ecd+'../flex_extract_v7.0.4.tar',ecd+'python',ecd+'grib_templates',ecd+'src'])
                try:
                    os.makedirs(c.flexpart_root_scripts+'/flex_extract_v7.0.4')
                except:
                    pass
                os.chdir(c.flexpart_root_scripts+'/flex_extract_v7.0.4')
                p=subprocess.check_call(['tar','-xvf',ecd+'../flex_extract_v7.0.4.tar'])
                os.chdir(c.flexpart_root_scripts+'/flex_extract_v7.0.4/src')

        os.chdir('../src')
        print 'install flex_extract_v7.0.4 software on '+target+' in directory '+os.getcwd()
        if c.makefile==None:
            makefile='Makefile.local.ifort'
        else:
            makefile=c.makefile
        flist=glob.glob('*.mod')+glob.glob('*.o')
        if flist:
            p=subprocess.check_call(['rm']+flist)
        try:
            print 'Using makefile: '+makefile
            p=subprocess.check_call(['make','-f',makefile])
            p=subprocess.check_call(['ls','-l','CONVERT2'])
        except:
            print 'compile failed - please edit '+makefile+' or try another Makefile in the src directory.'
            print 'most likely GRIB_API_INCLUDE_DIR, GRIB_API_LIB and EMOSLIB must be adapted.'
            print 'Available Makefiles:'
            print glob.glob('Makefile*')

    elif target.lower()=='ecgate':
        os.chdir('/')
        p=subprocess.check_call(['tar','-cvf',ecd+'../flex_extract_v7.0.4.tar',ecd+'python',ecd+'grib_templates',ecd+'src'])
        try:
            p=subprocess.check_call(['ecaccess-file-put',ecd+'../flex_extract_v7.0.4.tar','ecgate:/home/ms/'+c.ecgid+'/'+c.ecuid+'/flex_extract_v7.0.4.tar'])
        except:
            print 'ecaccess-file-put failed! Probably the eccert key has expired.'
            exit(1)
        p=subprocess.check_call(['ecaccess-job-submit','-queueName',target,ecd+'python/compilejob.ksh'])
        print 'compilejob.ksh has been submitted to ecgate for installation in '+c.ec_flexpart_root_scripts+'/flex_extract_v7.0.4'
        print 'You should get an email with subject flexcompile within the next few minutes'
    elif target.lower()=='cca':
        os.chdir('/')
        p=subprocess.check_call(['tar','-cvf',ecd+'../flex_extract_v7.0.4.tar',ecd+'python',ecd+'grib_templates',ecd+'src'])
        try:
            p=subprocess.check_call(['ecaccess-file-put',ecd+'../flex_extract_v7.0.4.tar','cca:/home/ms/'+c.ecgid+'/'+c.ecuid+'/flex_extract_v7.0.4.tar'])
        except:
            print 'ecaccess-file-put failed! Probably the eccert key has expired.'
            exit(1)

        p=subprocess.check_call(['ecaccess-job-submit','-queueName',target,ecd+'python/compilejob.ksh'])
        print 'compilejob.ksh has been submitted to cca for installation in '+c.ec_flexpart_root_scripts+'/flex_extract_v7.0.4'
        print 'You should get an email with subject flexcompile within the next few minutes'
    else:
        print 'ERROR: unknown installation target ',target
        print 'Valid targets: ecgate, cca, local'
    return


if __name__ == "__main__":
    main()
