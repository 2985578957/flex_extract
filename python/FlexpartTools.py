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
# Extension May 2018 - Anne Philipp - University of Vienna
# - introduced new CONTROL parameter to seperate accumulation and other
#   data specification
# - modified code to be able to retrieve ERA-5 data
# - modified code to be able to retrieve CERA-20C data
# - added possibility to retrieve data from public data server als as
#   public user
# - allow specifying TIME/TYPE/STEP combinations only with needed data instead
#   of the full 24 hours
#
# Requirements:
# in addition to a standard python 2.6 or 2.7 installation the following packages need to be installed
# ECMWF WebMARS, gribAPI with python enabled, emoslib, ecaccess web toolkit, all available from https://software.ecmwf.int/
# dateutils
# matplotlib (optional, for debugging)
#
#
import subprocess
from argparse import ArgumentParser,ArgumentDefaultsHelpFormatter
import traceback
import shutil
import os, errno,sys,inspect,glob
import datetime

from string import atoi
from numpy  import *

ecapi=True
try:
    import ecmwfapi
except ImportError:
    ecapi=False
from gribapi import *
from GribTools import GribTools
from opposite import opposite

def interpret_args_and_control(*args,**kwargs):

    parser = ArgumentParser(description='Retrieve FLEXPART input from ECMWF MARS archive',
                            formatter_class=ArgumentDefaultsHelpFormatter)

# the most important arguments
    parser.add_argument("--start_date", dest="start_date",
                        help="start date YYYYMMDD")
    parser.add_argument( "--end_date", dest="end_date",
                         help="end_date YYYYMMDD")
    parser.add_argument( "--date_chunk", dest="date_chunk",default=None,
                         help="# of days to be retrieved at once")

# some arguments that override the default in the control file
    parser.add_argument("--basetime", dest="basetime", help="base such as 00/12 (for half day retrievals)")
    parser.add_argument("--step", dest="step", help="steps such as 00/to/48")
    parser.add_argument("--levelist", dest="levelist",help="Vertical levels to be retrieved, e.g. 30/to/60")
    parser.add_argument("--area", dest="area", help="area defined as north/west/south/east")

# set the working directories
    parser.add_argument("--inputdir", dest="inputdir",default=None,
                        help="root directory for storing intermediate files")
    parser.add_argument("--outputdir", dest="outputdir",default=None,
                        help="root directory for storing output files")
    parser.add_argument("--flexpart_root_scripts", dest="flexpart_root_scripts",
                        help="FLEXPART root directory (to find grib2flexpart and COMMAND file)\n\
                              Normally flex_extract resides in the scripts directory of the FLEXPART distribution")

# this is only used by prepareFLEXPART.py to rerun a postprocessing step
    parser.add_argument("--ppid", dest="ppid",
                        help="Specify parent process id for rerun of prepareFLEXPART")

# arguments for job submission to ECMWF, only needed by submit.py
    parser.add_argument("--job_template", dest='job_template',default="job.temp",
                        help="job template file for submission to ECMWF")
    #parser.add_argument("--remote", dest="remote",
                        #help="target for submission to ECMWF (ecgate or cca etc.)")
    parser.add_argument("--queue", dest="queue",
                        help="queue for submission to ECMWF (e.g. ecgate or cca )")


    parser.add_argument("--controlfile", dest="controlfile",default='CONTROL.temp',
                        help="file with control parameters")
    parser.add_argument("--debug", dest="debug",default=0,
                        help="Debug mode - leave temporary files intact")
    parser.add_argument("--public", dest="public", default=0,
                        help="Public mode - retrieves the public datasets")

    parser.add_argument("--request", dest="request", default=None,
                        help="list all mars request in file mars_requests.dat \
                        and skip submission to mars")

    args = parser.parse_args()

    try:
        c=Control(args.controlfile)
    except IOError:
        try:
            c=Control(localpythonpath+args.controlfile)

        except:
            print 'Could not read control file "'+args.controlfile+'"'
            print 'Either it does not exist or its syntax is wrong.'
            print 'Try "'+sys.argv[0].split('/')[-1]+' -h" to print usage information'
            exit(1)

    if  args.start_date==None and getattr(c,'start_date')==None:
        print 'start_date specified neither in command line nor in control file '+args.controlfile
        print 'Try "'+sys.argv[0].split('/')[-1]+' -h" to print usage information'
        exit(1)

    if args.start_date!=None:
        c.start_date=args.start_date
    if args.end_date!=None:
        c.end_date=args.end_date
    if c.end_date==None:
        c.end_date=c.start_date
    if args.date_chunk!=None:
        c.date_chunk=args.date_chunk

    if not hasattr(c,'debug'):
        c.debug=args.debug

    if not hasattr(c, 'public'):
        setattr(c, 'public', args.public)

    if args.inputdir==None and args.outputdir==None:
        c.inputdir='../work'
        c.outputdir='../work'
    else:
        if args.inputdir!=None:
            c.inputdir=args.inputdir
            if args.outputdir==None:
                c.outputdir=args.inputdir
        if args.outputdir!=None:
            c.outputdir=args.outputdir
            if args.inputdir==None:
                c.inputdir=args.outputdir

    if hasattr(c,'outputdir')==False and args.outputdir==None:
        c.outputdir=c.inputdir
    else:
        if args.outputdir!=None:
            c.outputdir=args.outputdir

    if args.area!=None:
        afloat='.' in args.area
        l=args.area.split('/')
        if afloat:
            for i in range(len(l)):
                l[i]=str(int(float(l[i])*1000))
        c.upper,c.left,c.lower,c.right=l

# basetime aktiviert den ''operational mode''
    if args.basetime!=None:
        c.basetime=args.basetime
    #if int(c.basetime)==0:
        #c.start_date=datetime.datetime.strftime(datetime.datetime.strptime(c.start_date,'%Y%m%d')-datetime.timedelta(days=1),'%Y%m%d')
        #c.end_date=c.start_date

    if args.step!=None:
        l=args.step.split('/')
        if 'to' in args.step.lower():
            if 'by' in args.step.lower():
                ilist=arange(int(l[0]),int(l[2])+1,int(l[4]))
                c.step=['{:0>3}'.format(i) for i in ilist]
            else:
                myerror(None,args.step+':\n'+'please use "by" as well if "to" is used')
        else:
            c.step=l

    if args.levelist!=None:
        c.levelist=args.levelist
        if 'to' in c.levelist:
            c.level=c.levelist.split('/')[2]
        else:
            c.level=c.levelist.split('/')[-1]


    if args.flexpart_root_scripts!=None:
        c.flexpart_root_scripts=args.flexpart_root_scripts

    # set request attribute to control file
    if args.request != None:
        c.request=int(args.request)
    else:
        c.request = 0

    if c.request != 0:
        marsfile = os.path.join(c.inputdir, 'mars_requests.csv')
        if os.path.isfile(marsfile):
            os.remove(marsfile)

    return args,c

def install_args_and_control():

    parser = ArgumentParser(description='Install flex_extract software locally or on ECMWF machines',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--target',dest='install_target',
                        help="Valid targets: local | ecgate | cca , the latter two are at ECMWF")
    parser.add_argument("--makefile", dest="makefile",help='Name of Makefile to use for compiling CONVERT2')
    parser.add_argument("--ecuid", dest="ecuid",help='user id at ECMWF')
    parser.add_argument("--ecgid", dest="ecgid",help='group id at ECMWF')
    parser.add_argument("--gateway", dest="gateway",help='name of local gateway server')
    parser.add_argument("--destination", dest="destination",help='ecaccess destination, e.g. leo@genericSftp')

    parser.add_argument("--flexpart_root_scripts", dest="flexpart_root_scripts",
                        help="FLEXPART root directory on ECMWF servers (to find grib2flexpart and COMMAND file)\n\
                              Normally flex_extract resides in the scripts directory of the FLEXPART distribution, thus the:")

# arguments for job submission to ECMWF, only needed by submit.py
    parser.add_argument("--job_template", dest='job_template',default="job.temp.o",
                        help="job template file for submission to ECMWF")

    parser.add_argument("--controlfile", dest="controlfile",default='CONTROL.temp',
                        help="file with control parameters")
    args = parser.parse_args()

    try:
#    if True:
        c=Control(args.controlfile)
#    else:
    except:
        print 'Could not read control file "'+args.controlfile+'"'
        print 'Either it does not exist or its syntax is wrong.'
        print 'Try "'+sys.argv[0].split('/')[-1]+' -h" to print usage information'
        exit(1)

    if args.install_target!='local':
        if args.ecgid==None or args.ecuid==None or args.gateway==None or args.destination==None :
            print 'Please enter your ECMWF user id and group id as well as the \nname of the local gateway and the ectrans destination '
            print 'with command line options --ecuid --ecgid --gateway --destination'
            print 'Try "'+sys.argv[0].split('/')[-1]+' -h" to print usage information'
            print 'Please consult ecaccess documentation or ECMWF user support for further details'
            sys.exit(1)
        else:
            c.ecuid=args.ecuid
            c.ecgid=args.ecgid
            c.gateway=args.gateway
            c.destination=args.destination

    try:
        c.makefile=args.makefile
    except:
        pass

    if args.install_target=='local':
        if args.flexpart_root_scripts==None:
            c.flexpart_root_scripts='../'
        else:
            c.flexpart_root_scripts=args.flexpart_root_scripts

    if args.install_target!='local':
        if args.flexpart_root_scripts==None:
            c.ec_flexpart_root_scripts='${HOME}'
        else:
            c.ec_flexpart_root_scripts=args.flexpart_root_scripts

    return args,c

def cleanup(c):
    print "cleanup"
    cleanlist=glob.glob(c.inputdir+"/*")
#    cleanlist[-1:-1]=glob.glob(c.inputdir+"/flux*")
#    cleanlist[-1:-1]=glob.glob(c.inputdir+"/*.grb")
#    if c.ecapi==False and (c.ectrans=='1' or c.ecstorage=='1'):
#	cleanlist[-1:-1]=glob.glob(c.inputdir+"/"+c.prefix+"*")


#    silentremove(c.inputdir+"/VERTICAL.EC")
#    silentremove(c.inputdir+"/date_time_stepRange.idx")
    for cl in cleanlist:
        if c.prefix not in cl:
            silentremove(cl)
        if c.ecapi==False and (c.ectrans=='1' or c.ecstorage=='1'):
            silentremove(cl)



    print "Done"


def myerror(c,message='ERROR'):

    try:
        target=c.mailfail
    except AttributeError:
        target=os.getenv('USER')

    if(type(target) is not list):
        target=[target]
    print message
    # uncomment if user wants email notification directly from python
    #for t in target:
        #p=subprocess.Popen(['mail','-s flex_extract v7.0.4 ERROR', os.path.expandvars(t)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,bufsize=1)
        #tr='\n'.join(traceback.format_stack())
        #pout=p.communicate(input=message+'\n\n'+tr)[0]
        #print 'Email sent to '+os.path.expandvars(t) # +' '+pout.decode()

    exit(1)

def normalexit(c,message='Done!'):

    try:
        target=c.mailops


        if(type(target) is not list):
            target=[target]
        # Uncomment if user wants notification directly from python
        #for t in target:
            #p=subprocess.Popen(['mail','-s flex_extract v7.0.4 normal exit', os.path.expandvars(t)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,bufsize=1)
            #pout=p.communicate(input=message+'\n\n')[0]
            #print pout.decode()

    except:
        pass

    print message

    return

def product(*args, **kwds):
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = map(tuple, args) * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)

###############################################################
# utility to remove a file if it exists
# it does not fail if the file does not exist
###############################################################
def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured


def init128(fn):

    table128=dict()
    with open(fn) as f:
        fdata = f.read().split('\n')
        for data in fdata:
            if data[0]!='!':
                table128[data[0:3]]=data[59:64].strip()

    return table128

def toparamId(pars,table):

    cpar=pars.upper().split('/')
    ipar=[]
    for par in cpar:
        found=False
        for k,v in table.iteritems():
            if par==k or par==v:
                ipar.append(int(k))
                found=True
                break
        if found==False:
            print 'Warning: par '+par+' not found in table 128'
    return ipar

def dapoly(alist):


    pya=(alist[3]-alist[0]+3.*(alist[1]-alist[2]))/6.
    pyb=(alist[2]+alist[0])/2.-alist[1]-9.*pya/2.
    pyc=alist[1]-alist[0]-7.*pya/2.-2.*pyb
    pyd=alist[0]-pya/4.-pyb/3.-pyc/2.
    sfeld=8.*pya+4.*pyb+2.*pyc+pyd

    return sfeld

def darain(alist):
    xa=alist[0]
    xb=alist[1]
    xc=alist[2]
    xd=alist[3]
    xa[xa<0.]=0.
    xb[xb<0.]=0.
    xc[xc<0.]=0.
    xd[xd<0.]=0.

    xac=0.5*xb
    mask=xa+xc>0.
    xac[mask]=xb[mask]*xc[mask]/(xa[mask]+xc[mask])
    xbd=0.5*xc
    mask=xb+xd>0.
    xbd[mask]=xb[mask]*xc[mask]/(xb[mask]+xd[mask])
    sfeld=xac+xbd

    return sfeld

def add_previousday_ifneeded(attrs):

    if attrs['type']=='FC' and 'acc' not in attrs['target']:
        steps=attrs['step'].split('/')
        times=attrs['time'].split('/')
        addpday=False
        #for t in times:
            #for s in steps:
        if int(times[0])+int(steps[0])>23:
            addpday=True
        if(addpday):
            dates=attrs['date'].split('/')
            start_date=dates[0]
            syear=int(start_date[:4])
            smonth=int(start_date[4:6])
            sday=int(start_date[6:])
            start = datetime.date( year = syear, month = smonth, day = sday )
            startm1=start- datetime.timedelta(days=1)

            attrs['date']='/'.join([startm1.strftime("%Y%m%d")]+dates[1:])
            print('CHANGED FC start date to '+startm1.strftime("%Y%m%d")+'to accomodate TIME='+times[0]+', STEP='+steps[0])

    return



class Control:
    'class containing the information of the flex_extract control file'

    def __init__(self,filename):

        #try:
        with open(filename) as f:
            fdata = f.read().split('\n')
            for ldata in fdata:
                data=ldata.split()
                if len(data)>1:
                    if 'm_' in data[0].lower():
                        data[0]=data[0][2:]
                    if data[0].lower()=='class':
                        data[0]='marsclass'
                    if data[0].lower()=='day1':
                        data[0]='start_date'
                    if data[0].lower()=='day2':
                        data[0]='end_date'
                    if data[0].lower()=='addpar':
                        if '/' in data[1]:
                            if data[1][0]=='/':
                                data[1]=data[1][1:]
                            dd=data[1].split('/')
                            data=[data[0]]
                            for d in dd:
                                data.append(d)
                        pass
                    if len(data)==2:
                        if '$' in data[1]:
#				print data[1]
                            setattr(self,data[0].lower(),data[1])
                            while '$' in data[1]:
                                i=data[1].index('$')
                                j=data[1].find('{')
                                k=data[1].find('}')
                                var=os.getenv(data[1][j+1:k])
                                if var is not None:
                                    data[1]=data[1][:i]+var+data[1][k+1:]
                                else:
                                    myerror(None,'Could not find variable '+data[1][j+1:k]+' while reading '+filename)

#				    print data[0],data[1]
                            setattr(self,data[0].lower()+'_expanded',data[1])
                        else:
                            if data[1].lower()!='none':
                                setattr(self,data[0].lower(),data[1])
                            else:
                                setattr(self,data[0].lower(),None)

                    elif len(data)>2:
                        setattr(self,data[0].lower(),(data[1:]))
                else:
                    pass

            if not hasattr(self,'start_date'):
                self.start_date=None
            if not hasattr(self,'end_date'):
                self.end_date=self.start_date
            if not hasattr(self,'accuracy'):
                self.accuracy=24
            if not hasattr(self,'omega'):
                self.omega='0'
            if not hasattr(self,'cwc'):
                self.cwc='0'
            if not hasattr(self,'omegadiff'):
                self.omegadiff='0'
            if not hasattr(self,'etadiff'):
                self.etadiff='0'

            if not isinstance(self.type, list):
                self.type = [self.type]
            if not isinstance(self.time, list):
                self.time = [self.time]
            if not isinstance(self.step, list):
                self.step = [self.step]

            max_level_list = [16, 19, 31, 40, 50, 60, 62, 91, 137]
            if not hasattr(self,'levelist'):
                if not hasattr(self,'level'):
                    print 'WARNING: neither levelist nor level specified in CONTROL file'
                else:
                    if self.level in max_level_list:
                        self.levelist='1/to/'+self.level
            else:
                if not hasattr(self, 'level'):
                    if 'to' in self.levelist.lower():
                        max_level = self.levelist.split('/')[2]
                        if int(max_level) in max_level_list:
                            self.level = max_level
                        else:
                            print 'ERROR: LEVEL-parameter could not be set'
                            print 'LEVEL must be the maximum level of a specified level list from ECMWF, e.g.'
                            print '16, 19, 31, 40, 50, 60, 62, 91 or 137'
                            sys.exit(1)
                    else:
                        max_level = self.levelist.split('/')[-1]
                        if int(max_level) in max_level_list:
                            self.level = max_level
                        else:
                            print 'ERROR: LEVEL-parameter could not be set'
                            print 'LEVEL must be the maximum level of a specified level list from ECMWF, e.g.'
                            print '16, 19, 31, 40, 50, 60, 62, 91 or 137'
                            sys.exit(1)
                else:
                    # check if consistent
                    if int(self.level) in max_level_list:
                        pass
                    else:
                        print 'ERROR: LEVEL-parameter is not properly selected'
                        print 'LEVEL must be the maximum level of a specified level list from ECMWF, e.g.'
                        print '16, 19, 31, 40, 50, 60, 62, 91 or 137'
                        sys.exit(1)

            if not hasattr(self,'maxstep'):
                self.maxstep=0
                for s in self.step:
                    if int(s)>self.maxstep:
                        self.maxstep=int(s)
            else:
                self.maxstep=int(self.maxstep)
            if not hasattr(self,'prefix'):
                self.prefix='EN'
            if not hasattr(self,'makefile'):
                self.makefile=None
            if not hasattr(self,'basetime'):
                self.basetime=None
            if not hasattr(self,'date_chunk'):
                self.date_chunk='3'

            self.flexextractdir=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+'/../' # script directory
#		if not hasattr(self,'exedir'):
            self.exedir=self.flexextractdir+'src/'
            if not hasattr(self,'grib2flexpart'):
                self.grib2flexpart='0'
            if not hasattr(self,'flexpart_root_scripts'):
                self.flexpart_root_scripts=self.flexextractdir

            if not hasattr(self,'acctype'):
                print('... Control paramter ACCTYPE was not defined in CONTROL file.')
                print('Important for (forecast) flux data extraction.')
                try:
                    if len(self.type) > 1 and self.type[1] != 'AN':
                        print('Use old setting by using TYPE[1].')
                        self.acctype = self.type[1]
                except:
                    print('Use default value "FC"!')
                    self.acctype='FC'

            if not hasattr(self,'acctime'):
                print('... Control paramter ACCTIME was not defined in CONTROL file.')
                print('Use default value "00/12" for flux forecast!')
                print('This may be different for single data sets, see documentation if retrieval fails!')
                self.acctime='00/12'

            if not hasattr(self, 'accmaxstep'):
                print('... Control paramter ACCMAXSTEP was not defined in CONTROL file.')
                print('Use default value "12" for flux forecast!')
                print('This may be different for single data sets, see documentation if retrieval fails!')
                self.accmaxstep='12'

            for i in range(len(self.type)):
                if self.type[i] == 'AN' and int(self.step[i]) != 0:
                    print('Analysis retrievals must have STEP = 0 (setting to 0)')
                    self.type[i] = 0

            if not hasattr(self,'request'):
                self.request=0
            elif int(self.request) != 0:
                self.request=int(self.request)
                marsfile = os.path.join(self.inputdir,
                                        'mars_requests.csv')
                if os.path.isfile(marsfile):
                    silentremove(marsfile)

        return
    def __str__(self):

        attrs = vars(self)
        # {'kids': 0, 'name': 'Dog', 'color': 'Spotted', 'age': 10, 'legs': 2, 'smell': 'Alot'}
        # now dump this in some way or another
        return ', '.join("%s: %s" % item for item in attrs.items())

    def tolist(self):
        attrs=vars(self)
        l=list()
        for item in attrs.items():
            if '_expanded' in item[0]:
                pass
            elif 'exedir' in item[0]:
                pass
            elif 'flexpart_root_scripts' in item[0]:
                pass
            elif 'flexextractdir' in item[0]:
                pass

            else:
                if type(item[1]) is list:
                    stot=''
                    for s in item[1]:
                        stot+=s+' '

                    l.append("%s %s" % (item[0],stot))
                else:
                    l.append("%s %s" % item )
        return sorted(l)



##############################################################
# MARSretrieval class
##############################################################
class MARSretrieval:
    'class for MARS retrievals'

    def __init__(self,server, public, marsclass="ei",type="",levtype="",levelist="",
                 repres="", date="",resol="",stream="",area="",time="",step="",expver="1",
                 number="",accuracy="", grid="", gaussian="", target="",param="",dataset="",expect=""):
        self.dataset=dataset
        self.marsclass=marsclass
        self.type=type
        self.levtype=levtype
        self.levelist=levelist
        self.repres=repres
        self.date=date
        self.resol=resol
        self.stream=stream
        self.area=area
        self.time=time
        self.step=step
        self.expver=expver
        self.target=target
        self.param=param
        self.number=number
        self.accuracy=accuracy
        self.grid=grid
        self.gaussian=gaussian
#	self.expect=expect
        self.server=server
        self.public=public

    def displayInfo(self):
        attrs=vars(self)
        for item in attrs.items():
            if item[0] in ('server'):
                pass
            else:
                print item[0]+': '+str(item[1])

        return

    def print_infodata_csv(self, inputdir, request_number):
        '''
        @Description:
            Write all request parameter in alpabetical order into a "csv" file.

        @Input:
            self: instance of MarsRetrieval
                For description see class documentation.

            inputdir: string
                The path where all data from the retrievals are stored.

            request_number: integer
                Number of mars requests for flux and non-flux data.

        @Return:
            <nothing>
        '''

        # Get all class attributes and their values as a dictionary
        attrs = vars(self).copy()
        del attrs['server']
        del attrs['public']

        # open a file to store all requests to
        with open(os.path.join(inputdir, 'mars_requests.csv'), 'a') as f:
            f.write(str(request_number) + ', ')
            f.write(', '.join(str(attrs[key])
                        for key in sorted(attrs.iterkeys())))
            f.write('\n')

        return

    def dataRetrieve(self):
        attrs=vars(self).copy()

        del attrs['server']
        del attrs['public']
        mclass = attrs.get('marsclass')
        del attrs['marsclass']
        attrs['class'] = mclass

        add_previousday_ifneeded(attrs)

        target = attrs.get('target')
        if not int(self.public):
            del attrs['target']
        print 'target: ', target

        delete_keys = []
        for k, v in attrs.iteritems():
            if v == '':
                delete_keys.append(str(k))
            else:
                attrs[k] = str(v)

        for k in delete_keys:
            del attrs[k]

        if self.server != False:
            try:
                if int(self.public):
                    print 'RETRIEVE DATA!'
                    self.server.retrieve(attrs)
                else:
                    print 'EXECUTE RETRIEVAL!'
                    self.server.execute(attrs, target)
            except:
                e = sys.exc_info()[0]
                print "Error: ", e
                print 'MARS Request failed'#, have you already registered at apps.ecmwf.int?'
                #raise IOError
            if not int(self.public) and os.stat(target).st_size==0:
                print 'MARS Request returned no data - please check request'
                raise IOError
            elif int(self.public) and os.stat(attrs.get('target')).st_size==0:
                print 'MARS Request returned no data - please check request'
                raise IOError
        else:
            s='ret'
            for k,v in attrs.iteritems():
                s=s+','+k+'='+str(v)

            s+=',target="'+target+'"'
            p=subprocess.Popen(['mars'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,bufsize=1)
            pout=p.communicate(input=s)[0]
            print pout.decode()
            if 'Some errors reported' in pout.decode():
                print 'MARS Request failed - please check request'
                raise IOError

            if os.stat(target).st_size==0:
                print 'MARS Request returned no data - please check request'
                raise IOError

        return

##############################################################
class EIFlexpart:
    'class to retrieve Era Interim data for running FLEXPART'
##############################################################

    def __init__(self,c,fluxes=False):
        # different mars types for retrieving reanalysis data for flexpart

        # set a counter for the number of mars requests generated
        self.mreq_count = 0
        self.types=dict()
        try:
            if c.maxstep>24: #len(c.type):    # Pure forecast mode
                c.type=[c.type[0]] # AP changed this index from 1 to 0
                c.step=['{:0>3}'.format(int(c.step[0]))]
                c.time=[c.time[0]]
                for i in range(1,c.maxstep+1):
                    c.type.append(c.type[0])
                    c.step.append('{:0>3}'.format(i))
                    c.time.append(c.time[0])
        except:
            pass

        self.inputdir=c.inputdir
        self.basetime=c.basetime
        self.dtime=c.dtime
        self.mars={}
        i=0
        j=0
        if fluxes==True and c.maxstep<=24:
            self.types[str(c.acctype)]={'times':str(c.acctime),
                                        'steps':'{}/to/{}/by/{}'.format(
                                               c.dtime,c.accmaxstep,c.dtime)}
            i=1
            for k in [0,12]:
                for j in range(int(c.dtime),13,int(c.dtime)):
                    self.mars['{:0>3}'.format(i*int(c.dtime))]=[c.type[1],'{:0>2}'.format(k),'{:0>3}'.format(j)]
                    i+=1
        else:
            for ty,st,ti in zip(c.type,c.step,c.time):
                btlist=range(len(c.time))
                if c.basetime=='12':
                    btlist=[1,2,3,4,5,6,7,8,9,10,11,12]
                if c.basetime=='00':
                    btlist=[13,14,15,16,17,18,19,20,21,22,23,0]


                if ((ty.upper() == 'AN' and mod(int(c.time[i]),int(c.dtime))==0 and int(c.step[i])==0) or \
                   (ty.upper() != 'AN' and mod(int(c.step[i]),int(c.dtime))==0 and \
                    mod(int(c.step[i]),int(c.dtime))==0) ) and \
                   (i in btlist or c.maxstep>24):
                    if ty not in self.types.keys():
                        self.types[ty]={'times':'','steps':''}
                    if ti not in self.types[ty]['times']:
                        if len(self.types[ty]['times'])>0:
                            self.types[ty]['times']+='/'
                        self.types[ty]['times']+=ti
                    if st not in self.types[ty]['steps']:
                        if len(self.types[ty]['steps'])>0:
                            self.types[ty]['steps']+='/'
                        self.types[ty]['steps']+=st

                    self.mars['{:0>3}'.format(j)]=[ty,'{:0>2}'.format(int(ti)),'{:0>3}'.format(int(st))]
                    j+=int(c.dtime)

                i+=1

# Different grids need different retrievals
# SH=Spherical Harmonics, GG=Gaussian Grid, OG=Output Grid, ML=MultiLevel, SL=SingleLevel
        self.params={'SH__ML':'','SH__SL':'',
                     'GG__ML':'','GG__SL':'',
                     'OG__ML':'','OG__SL':'',
                     'OG_OROLSM_SL':'','OG_acc_SL':''}

        self.marsclass=c.marsclass
        self.stream=c.stream
        self.number=c.number
        self.resol=c.resol
        if 'N' in c.grid:  # Gaussian output grid
            self.grid=c.grid
            self.area='G'
        else:
            self.grid='{}/{}'.format(int(c.grid)/1000.,int(c.grid)/1000.)
            self.area='{}/{}/{}/{}'.format(int(c.upper)/1000.,int(c.left)/1000.,int(c.lower)/1000.,int(c.right)/1000.)

        self.accuracy=c.accuracy
        self.level=c.level
        try:
            self.levelist=c.levelist
        except:
            self.levelist='1/to/'+c.level
        self.glevelist='1/to/'+c.level
        try:
            self.gaussian=c.gaussian
        except:
            self.gaussian=''
        try:
            self.dataset=c.dataset
        except:
            self.dataset=''
        try:
            self.expver=c.expver
        except:
            self.expver='1'
        try:
            self.number=c.number
        except:
            self.number='0'

        self.outputfilelist=[]


# Now comes the nasty part that deals with the different scenarios we have:
# 1) Calculation of etadot on
#    a) Gaussian grid
#    b) Output grid
#    c) Output grid using parameter 77 retrieved from MARS
# 3) Calculation/Retrieval of omega
# 4) Download also data for WRF

        if fluxes==False:
            self.params['SH__SL']=['LNSP','ML','1','OFF']
#	    self.params['OG__SL']=["SD/MSL/TCC/10U/10V/2T/2D/129/172",'SFC','1',self.grid]
            self.params['OG__SL']=["141/151/164/165/166/167/168/129/172",'SFC','1',self.grid]
            if c.marsclass.upper() == 'EA' or c.marsclass.upper() == 'EP':
                self.params['OG_OROLSM__SL']=["160/27/28/244",'SFC','1',self.grid]
            else:
                self.params['OG_OROLSM__SL']=["160/27/28/173",'SFC','1',self.grid]

            if len(c.addpar)>0:
                if c.addpar[0]=='/':
                    c.addpar=c.addpar[1:]
                self.params['OG__SL'][0]+='/'+'/'.join(c.addpar)
            self.params['OG__ML']=['T/Q','ML',self.levelist,self.grid]

            if c.gauss=='0' and c.eta=='1': # the simplest case
                self.params['OG__ML'][0]+='/U/V/77'
            elif c.gauss=='0' and c.eta=='0': # this is not recommended (inaccurate)
                self.params['OG__ML'][0]+='/U/V'
            elif c.gauss=='1' and c.eta=='0': # this is needed for data before 2008, or for reanalysis data
                self.params['GG__SL']=['Q','ML','1','{}'.format((int(self.resol)+1)/2)]
                self.params['SH__ML']=['U/V/D','ML',self.glevelist,'OFF']
            else:
                print 'Warning: This is a very costly parameter combination, use only for debugging!'
                self.params['GG__SL']=['Q','ML','1','{}'.format((int(self.resol)+1)/2)]
                self.params['GG__ML']=['U/V/D/77','ML',self.glevelist,'{}'.format((int(self.resol)+1)/2)]

            if c.omega=='1':
                self.params['OG__ML'][0]+='/W'

            try:            # add cloud water content if necessary
                if c.cwc=='1':
                    self.params['OG__ML'][0]+='/CLWC/CIWC'
            except:
                pass

            try:            # add vorticity and geopotential height for WRF if necessary
                if c.wrf=='1':
                    self.params['OG__ML'][0]+='/Z/VO'
                    if '/D' not in self.params['OG__ML'][0]:
                        self.params['OG__ML'][0]+='/D'
#		    wrf_sfc='sp/msl/skt/2t/10u/10v/2d/z/lsm/sst/ci/sd/stl1/stl2/stl3/stl4/swvl1/swvl2/swvl3/swvl4'.upper()
#                            134/151/235/167/165/166/168/129/172/034/031/141/139/170/183/236/039/040/041/042
                    wrf_sfc='134/235/167/165/166/168/129/172/34/31/141/139/170/183/236/39/40/41/42'.upper()
                    lwrt_sfc=wrf_sfc.split('/')
                    for par in lwrt_sfc:
                        if par not in self.params['OG__SL'][0]:
                            self.params['OG__SL'][0]+='/'+par

            except:
                pass
        else:
            self.params['OG_acc_SL']=["LSP/CP/SSHF/EWSS/NSSS/SSR",'SFC','1',self.grid]


        return
        # add additional WRF specific parameters here

    def create_namelist(self,c,filename):

#	if inputdir=="":
#	    self.inputdir='.'
#	else:
#	    self.inputdir=inputdir

        self.inputdir=c.inputdir
        area=asarray(self.area.split('/')).astype(float)
        grid=asarray(self.grid.split('/')).astype(float)

#	if area[3]<0:
#	    area[3]+=360
        if area[1]>area[3]:
            area[1]-=360
        zyk=abs((area[3]-area[1]-360.)+grid[1])<1.e-6
        maxl=int((area[3]-area[1])/grid[1])+1
        maxb=int((area[0]-area[2])/grid[0])+1

        f=open(self.inputdir+'/'+filename,'w')
        f.write('&NAMGEN\n')
        f.write(',\n  '.join(['maxl='+str(maxl),'maxb='+str(maxb),
                              'mlevel='+self.level,'mlevelist='+'"'+self.levelist+'"',
                    'mnauf='+self.resol,'metapar='+'77',
                    'rlo0='+str(area[1]),'rlo1='+str(area[3]),'rla0='+str(area[2]),'rla1='+str(area[0]),
                    'momega='+c.omega,'momegadiff='+c.omegadiff,'mgauss='+c.gauss,
                    'msmooth='+c.smooth,'meta='+c.eta,'metadiff='+c.etadiff,'mdpdeta='+c.dpdeta]))

        f.write('\n/\n')
        f.close()
        return


    def retrieve(self, server, public, dates, request, times, inputdir=''):
        self.dates=dates
        self.server=server
        self.public=public

        if inputdir=="":
            self.inputdir='.'
        else:
            self.inputdir=inputdir

            # Retrieve Q not for using Q but as a template for a reduced gaussian grid one date and time is enough
# Take analysis at 00
#        qdate=self.dates
#        idx=qdate.find("/")
#        if (idx >0):
#            qdate=self.dates[:idx]

        #QG= MARSretrieval(self.server, self.public, dataset=self.dataset, marsclass=self.marsclass, stream=self.stream, type="an", levtype="ML", levelist="1",
                            #gaussian="reduced",grid='{}'.format((int(self.resol)+1)/2), resol=self.resol,accuracy=self.accuracy,target=self.inputdir+"/"+"QG.grb",
                            #date=qdate, time="00",expver=self.expver, param="133.128")
        #QG.displayInfo()
        #QG.dataRetrieve()

        oro=False
        for ftype in self.types:
            for pk,pv in self.params.iteritems():
                if isinstance(pv,str):     # or pk!='GG__SL' :
                    continue
                mftype=''+ftype
                mftime=self.types[ftype]['times']
                mfstep=self.types[ftype]['steps']
                mfdate=self.dates
                mfstream=self.stream
                mftarget=self.inputdir+"/"+ftype+pk+'.'+self.dates.split('/')[0]+'.'+str(os.getppid())+'.'+str(os.getpid())+".grb"

                if pk=='OG__SL':
                    pass
                if pk=='OG_OROLSM__SL':
                    if oro==False:
                        # in CERA20C there is no stream "OPER"!
                        if self.marsclass.upper() != 'EP':
                            mfstream='OPER'
                        mftype='AN'
                        mftime='00'
                        mfstep='000'
                        mfdate=self.dates.split('/')[0]
                        mftarget=self.inputdir+"/"+pk+'.'+mfdate+'.'+str(os.getppid())+'.'+str(os.getpid())+".grb"
                        oro=True
                    else:
                        continue

                if pk=='GG__SL' and pv[0]=='Q':
                    area=""
                    gaussian='reduced'
                else:
                    area=self.area
                    gaussian=self.gaussian

                if self.basetime==None:
                    # increase number of mars requests
                    self.mreq_count += 1
                    MR= MARSretrieval(self.server, self.public, dataset=self.dataset, marsclass=self.marsclass, stream=mfstream,
                                      type=mftype, levtype=pv[1], levelist=pv[2],resol=self.resol, gaussian=gaussian,
                                  accuracy=self.accuracy,grid=pv[3],target=mftarget,area=area,
                                  date=mfdate, time=mftime,number=self.number,step=mfstep, expver=self.expver, param=pv[0])

                    if request == 0:
                        MR.displayInfo()
                        MR.dataRetrieve()
                    elif request == 1:
                        MR.print_infodata_csv(self.inputdir, self.mreq_count)
                    elif request == 2:
                        MR.print_infodata_csv(self.inputdir, self.mreq_count)
                        MR.displayInfo()
                        MR.dataRetrieve()
# The whole else section is only necessary for operational scripts. It could be removed
                else: # check if mars job requests fields beyond basetime. If yes eliminate those fields since they may not
                        # be accessible with user's credentials
                    sm1=-1
                    if 'by' in mfstep:
                        sm1=2
                    tm1=-1
                    if 'by' in mftime:
                        tm1=2
                    maxtime=datetime.datetime.strptime(mfdate.split('/')[-1]+mftime.split('/')[tm1],'%Y%m%d%H')+ \
                        datetime.timedelta(hours=int(mfstep.split('/')[sm1]))

                    elimit=datetime.datetime.strptime(mfdate.split('/')[-1]+self.basetime,'%Y%m%d%H')

                    if self.basetime=='12':
                        if 'acc' in pk:

                    # Strategy: if maxtime-elimit>=24h reduce date by 1,
                    # if 12h<=maxtime-elimit<12h reduce time for last date
                    # if maxtime-elimit<12h reduce step for last time
                    # A split of the MARS job into 2 is likely necessary.
                            maxtime=elimit-datetime.timedelta(hours=24)
                            mfdate='/'.join(('/'.join(mfdate.split('/')[:-1]),datetime.datetime.strftime(maxtime,'%Y%m%d')))
                            # increase number of mars requests
                            self.mreq_count += 1
                            MR= MARSretrieval(self.server, self.public, dataset=self.dataset, marsclass=self.marsclass, stream=self.stream,
                                              type=mftype, levtype=pv[1], levelist=pv[2],resol=self.resol, gaussian=gaussian,
                                                accuracy=self.accuracy,grid=pv[3],target=mftarget,area=area,
                                                date=mfdate, time=mftime,number=self.number,step=mfstep, expver=self.expver, param=pv[0])

                            if request == 0:
                                MR.displayInfo()
                                MR.dataRetrieve()
                            elif request == 1:
                                MR.print_infodata_csv(self.inputdir, self.mreq_count)
                            elif request == 2:
                                MR.print_infodata_csv(self.inputdir, self.mreq_count)
                                MR.displayInfo()
                                MR.dataRetrieve()

                            maxtime=elimit-datetime.timedelta(hours=12)
                            mfdate=datetime.datetime.strftime(maxtime,'%Y%m%d')
                            mftime='00'
                            mftarget=self.inputdir+"/"+ftype+pk+'.'+mfdate+'.'+str(os.getppid())+'.'+str(os.getpid())+".grb"
                            # increase number of mars requests
                            self.mreq_count += 1
                            MR= MARSretrieval(self.server, self.public, dataset=self.dataset, marsclass=self.marsclass, stream=self.stream,
                                              type=mftype, levtype=pv[1], levelist=pv[2],resol=self.resol, gaussian=gaussian,
                                                accuracy=self.accuracy,grid=pv[3],target=mftarget,area=area,
                                                date=mfdate, time=mftime,number=self.number,step=mfstep, expver=self.expver, param=pv[0])
                            if request == 0:
                                MR.displayInfo()
                                MR.dataRetrieve()
                            elif request == 1:
                                MR.print_infodata_csv(self.inputdir, self.mreq_count)
                            elif request == 2:
                                MR.print_infodata_csv(self.inputdir, self.mreq_count)
                                MR.displayInfo()
                                MR.dataRetrieve()
                        else:
                            # increase number of mars requests
                            self.mreq_count += 1
                            MR= MARSretrieval(self.server, self.public, dataset=self.dataset, marsclass=self.marsclass, stream=self.stream,
                                              type=mftype, levtype=pv[1], levelist=pv[2],resol=self.resol, gaussian=gaussian,
                                                accuracy=self.accuracy,grid=pv[3],target=mftarget,area=area,
                                                date=mfdate, time=mftime,number=self.number,step=mfstep, expver=self.expver, param=pv[0])

                            if request == 0:
                                MR.displayInfo()
                                MR.dataRetrieve()
                            elif request == 1:
                                MR.print_infodata_csv(self.inputdir, self.mreq_count)
                            elif request == 2:
                                MR.print_infodata_csv(self.inputdir, self.mreq_count)
                                MR.displayInfo()
                                MR.dataRetrieve()
                    else:
                        maxtime=elimit-datetime.timedelta(hours=24)
                        mfdate=datetime.datetime.strftime(maxtime,'%Y%m%d')

                        mftimesave=''.join(mftime)

                        if pk=='OG_OROLSM__SL':
                            mfdate=self.dates.split('/')[0]
                            mftarget=self.inputdir+"/"+pk+'.'+mfdate+'.'+str(os.getppid())+'.'+str(os.getpid())+".grb"

                        if '/' in mftime:
                            times=mftime.split('/')
                            while int(times[0])+int(mfstep.split('/')[0])<=12 and pk!='OG_OROLSM__SL' and 'acc' not in pk:
                                times=times[1:]
                                if len(times)>1:
                                    mftime='/'.join(times)
                                else:
                                    mftime=times[0]

                        if int(mftimesave.split('/')[0])==0 and int(mfstep.split('/')[0])==0 and pk!='OG_OROLSM__SL':
                            mfdate=datetime.datetime.strftime(elimit,'%Y%m%d')
                            mftime='00'
                            mfstep='000'
                            mftarget=self.inputdir+"/"+ftype+pk+'.'+mfdate+'.'+str(os.getppid())+'.'+str(os.getpid())+".grb"

                        # increase number of mars requests
                        self.mreq_count += 1
                        MR= MARSretrieval(self.server, self.public, dataset=self.dataset, marsclass=self.marsclass, stream=self.stream,
                                          type=mftype, levtype=pv[1], levelist=pv[2],resol=self.resol, gaussian=gaussian,
                                      accuracy=self.accuracy,grid=pv[3],target=mftarget,area=area,
                                      date=mfdate, time=mftime,number=self.number,step=mfstep, expver=self.expver, param=pv[0])

                        if request == 0:
                            MR.displayInfo()
                            MR.dataRetrieve()
                        elif request == 1:
                            MR.print_infodata_csv(self.inputdir, self.mreq_count)
                        elif request == 2:
                            MR.print_infodata_csv(self.inputdir, self.mreq_count)
                            MR.displayInfo()
                            MR.dataRetrieve()


        if request == 0 or request == 2:
            print('MARS retrieve done ... ')
        elif request == 1:
            print('MARS request printed ...')

    def getFlexpartTime(self, type,step, time):
        cstep='{:0>3}'.format(step)
        ctime='{:0>2}'.format(int(time/100))

        ctype = str(type).upper()
        myinfo = [ctype,ctime, cstep]
        cflextime = None
        for t, marsinfo in self.mars.items():
            if myinfo == marsinfo:
                cflextime=t
        return cflextime

    def process_output(self, c):

        print 'Postprocessing:\n Format: {}\n'.format(c.format)
        if c.ecapi==False:
            print 'ecstorage: {}\n ecfsdir: {}\n'.format(c.ecstorage,c.ecfsdir)
            if not hasattr(c,'gateway'):
                c.gateway=os.getenv('GATEWAY')
            if not hasattr(c,'destination'):
                c.destination=os.getenv('DESTINATION')
            print 'ectrans: {}\n gateway: {}\n destination: {}\n '.format(c.ectrans, c.gateway,c.destination)
        print 'Output filelist: \n',self.outputfilelist

        if c.format.lower()=='grib2':
            for ofile in self.outputfilelist:
                p=subprocess.check_call(['grib_set','-s','edition=2,productDefinitionTemplateNumber=8',ofile,ofile+'_2'])
                p=subprocess.check_call(['mv',ofile+'_2',ofile])
        if c.debug==0:
            inputfiles=glob.glob('*.grb')
            for grb in inputfiles:
                try:
                    os.remove(grb)
                except:
                    pass
        if c.stream=='ELDA':
            opposite(self.inputdir+'/'+c.prefix)
            for i in range(len(self.outputfilelist)):
                if self.outputfilelist[i][-4:]!='N000' :
                    j=int(self.outputfilelist[i][-3:])
                    self.outputfilelist.append(self.outputfilelist[i][:-3]+'{:0>3}'.format(j+25))

        if int(c.ectrans)==1 and c.ecapi==False:
            for ofile in self.outputfilelist:
                p=subprocess.check_call(['ectrans','-overwrite','-gateway',c.gateway,
                                         '-remote',c.destination,'-source',ofile])
                print 'ectrans:',p
        if int(c.ecstorage)==1 and c.ecapi==False:
            for ofile in self.outputfilelist:
                p=subprocess.check_call(['ecp','-o',ofile,os.path.expandvars(c.ecfsdir)])

#20131107 000000      EN13110700              ON DISC
        if c.outputdir!=c.inputdir:
            for ofile in self.outputfilelist:
                p=subprocess.check_call(['mv',ofile,c.outputdir])

        if c.grib2flexpart=='1':
            f=open(c.outputdir+'/'+'AVAILABLE','w')
            clist=[]
            for ofile in self.outputfilelist: # generate AVAILABLE file
                fname=ofile.split('/')
                if '.' in fname[-1]:
                    l=fname[-1].split('.')
                    timestamp=datetime.datetime.strptime(l[0][-6:]+l[1],'%y%m%d%H')
                    timestamp+=datetime.timedelta(hours=int(l[2]))
                    cdate=datetime.datetime.strftime(timestamp,'%Y%m%d')
                    chms=datetime.datetime.strftime(timestamp,'%H%M%S')

                else:
                    cdate='20'+fname[-1][-8:-2]
                    chms=fname[-1][-2:]+'0000'
                clist.append(cdate+' '+chms+' '*6+fname[-1]+' '*14+'ON DISC')
            clist.sort()
            f.write('\n'.join(clist)+'\n')
            f.close()

            pwd=os.path.abspath(c.outputdir)
            f=open(pwd+'/pathnames','w')
            f.write(pwd+'/Options/\n')
            f.write(pwd+'/\n')
            f.write(pwd+'/\n')
            f.write(pwd+'/AVAILABLE\n')
            f.write('==================\n')
            f.close()

            if not os.path.exists(pwd+'/Options'):
                os.makedirs(pwd+'/Options')
            f=open(os.path.expandvars(os.path.expanduser(c.flexpart_root_scripts))+'/../Options/COMMAND','r')
            lflist=f.read().split('\n')
            i=0
            for l in lflist:
                if 'LDIRECT' in l.upper():
                    break
                i+=1

            clist.sort()
            lflist=lflist[:i+1]+[clist[0][:16],clist[-1][:16]]+lflist[i+3:]
            g=open(pwd+'/Options/COMMAND','w')
            g.write('\n'.join(lflist)+'\n')
            g.close()

            os.chdir(c.outputdir)
            p=subprocess.check_call([os.path.expandvars(os.path.expanduser(c.flexpart_root_scripts))+'/../FLEXPART_PROGRAM/grib2flexpart',
                                     'useAvailable','.'])
            os.chdir(pwd)

    def create(self, inputfiles, c,):

        table128=init128(c.flexextractdir+'/grib_templates/ecmwf_grib1_table_128')
        wrfpars=toparamId('sp/mslp/skt/2t/10u/10v/2d/z/lsm/sst/ci/sd/stl1/stl2/stl3/stl4/swvl1/swvl2/swvl3/swvl4',table128)
#        index_keys=["date","time","stepRange"]
        if '/' in c.number:
            index_keys=["number","date","time","step"]
        else:
            index_keys=["date","time","step"]

        indexfile=c.inputdir+"/date_time_stepRange.idx"
        silentremove(indexfile)
        grib=GribTools(inputfiles.files)
        iid=grib.index(index_keys=index_keys, index_file = indexfile)

        print 'index done...'
        fdict={'10':None,'11':None,'12':None,'13':None,'16':None,'17':None,'19':None,'21':None,'22':None,'20':None}
        for f in fdict.keys():
            silentremove(c.inputdir+"/fort."+f)

        index_vals = []
        for key in index_keys:
            key_vals = grib_index_get(iid,key)
            print key_vals

            index_vals.append(key_vals)

        for prod in product(*index_vals):
            for i in range(len(index_keys)):
                grib_index_select(iid,index_keys[i],prod[i])


            gid = grib_new_from_index(iid)
            hid = gid
            cflextime = None
            for k,f in fdict.iteritems():
                fdict[k] = open(c.inputdir+'/fort.'+k,'w')
            if gid is not None:
                cdate = str(grib_get(gid, 'date'))
                time = grib_get(gid, 'time')
                type = grib_get(gid, 'type')
                step = grib_get(gid, 'step')
#                step = grib_get(gid, 'stepRange')
#		cflextime = self.getFlexpartTime(type,step, time)
                timestamp=datetime.datetime.strptime(cdate+'{:0>2}'.format(time/100),'%Y%m%d%H')
                timestamp+=datetime.timedelta(hours=int(step))
#		print gid,index_keys[i],prod[i],cdate,time,step,timestamp

                cdateH=datetime.datetime.strftime(timestamp,'%Y%m%d%H')
                chms=datetime.datetime.strftime(timestamp,'%H%M%S')

                if c.basetime !=None:
                    slimit=datetime.datetime.strptime(c.start_date+'00','%Y%m%d%H')
                    bt='23'
                    if c.basetime=='00':
                        bt='00'
                        slimit=datetime.datetime.strptime(c.end_date+bt,'%Y%m%d%H')-datetime.timedelta(hours=12-int(c.dtime))

                    if c.basetime=='12':
                        bt='12'
                        slimit=datetime.datetime.strptime(c.end_date+bt,'%Y%m%d%H')-datetime.timedelta(hours=12-int(c.dtime))

                    elimit=datetime.datetime.strptime(c.end_date+bt,'%Y%m%d%H')

                    if timestamp<slimit or timestamp>elimit:
                        continue
                else:
                    if c.maxstep<24:
                        if cdateH<c.start_date+'00':
                            continue
                        if cdateH>c.end_date+'23':
                            continue



            try:
                if c.wrf=='1':
                    if 'olddate' not in locals():
                        fwrf = open(c.outputdir+'/WRF'+cdate+'.{:0>2}'.format(time)+'.000.grb2','w')
                        olddate=cdate[:]
                    else:
                        if cdate!=olddate:
                            fwrf = open(c.outputdir+'/WRF'+cdate+'.{:0>2}'.format(time)+'.000.grb2','w')
                            olddate=cdate[:]
            except AttributeError:
                pass

#                print 'cyear '+cyear+'/'+cmonth+'/'+'/EI'+cyear[2:4]+cmonth+cday+cflextime

            savedfields=[]
            while 1:
                if gid is None: break
                paramId = grib_get(gid, 'paramId')
                gridtype = grib_get(gid, 'gridType')
                datatype = grib_get(gid, 'dataType')
                levtype = grib_get(gid, 'typeOfLevel')
                if paramId == 133 and gridtype=='reduced_gg':
# Relative humidity (Q.grb) is used as a template only so we need the first we "meet"
                    fout=open(c.inputdir+'/fort.18','w')
                    grib_write(gid,fout)
                    fout.close()
                elif paramId == 131 or paramId == 132:
                    grib_write(gid, fdict['10'])
                elif paramId == 130:
                    grib_write(gid, fdict['11'])
                elif paramId == 133 and gridtype!='reduced_gg':
                    grib_write(gid, fdict['17'])
                elif paramId == 152:
                    grib_write(gid, fdict['12'])
                elif paramId == 155 and gridtype=='sh':
                    grib_write(gid, fdict['13'])
                elif paramId in [129,138,155] and levtype=='hybrid' and c.wrf=='1':
#		    print paramId,'not written'
                    pass
                elif paramId == 246 or paramId == 247:  # cloud liquid water and ice
                    if paramId==246:
                        clwc=grib_get_values(gid)
                    else:
                        clwc+=grib_get_values(gid)
                        grib_set_values(gid,clwc)
#			grib_set(gid,'shortName','qc')
                        grib_set(gid,'paramId',201031)
                        grib_write(gid, fdict['22'])

                elif paramId == 135:
                    grib_write(gid, fdict['19'])
                elif paramId == 77:
                    grib_write(gid, fdict['21'])
                else:
                    if paramId not in savedfields:
                        grib_write(gid, fdict['16'])
                        savedfields.append(paramId)
                    else:
                        print 'duplicate '+str(paramId)+' not written'

                try:
                    if c.wrf=='1':
                        if levtype=='hybrid':
                            if paramId in [129,130,131,132,133,138,155]:
                                grib_write(gid,fwrf)
                        else:
                            if paramId in wrfpars:
                                grib_write(gid,fwrf)
                except AttributeError:
                    pass



                grib_release(gid)
                gid = grib_new_from_index(iid)
# call for CONVERT2

            for f in fdict.values():
                f.close()

            if hid is not None:
                pwd=os.getcwd()
                os.chdir(c.inputdir)
                if os.stat('fort.21').st_size==0 and int(c.eta)==1:
                    print 'Parameter 77 (etadot) is missing, most likely it is not available for this type or date/time\n'
                    print 'Check parameters CLASS, TYPE, STREAM, START_DATE\n'
                    myerror(c,'fort.21 is empty while parameter eta is set to 1 in CONTROL file')

                p=subprocess.check_call([os.path.expandvars(os.path.expanduser(c.exedir))+'/CONVERT2'],shell=True)
                os.chdir(pwd)
# create the corresponding output file  fort.15 (generated by CONVERT2) + fort.16 (paramId 167 and paramId 168)
                fnout=c.inputdir+'/'+c.prefix
                if c.maxstep>12:
                    suffix=cdate[2:8]+'.{:0>2}'.format(time/100)+'.{:0>3}'.format(step)
                else:
                    suffix=cdateH[2:10]
                try:
                    numberindex=index_keys.index('number')
                    if len(index_vals[numberindex])>1:
                        suffix=suffix+'.N{:0>3}'.format(int(prod[numberindex]))
                except:
                    pass

                fnout+=suffix
                print "outputfile = " + fnout
                self.outputfilelist.append(fnout) # needed for final processing
                fout = open(fnout,'wb')
                shutil.copyfileobj(open(c.inputdir+'/fort.15','rb'), fout)
                if c.cwc=='1':
                    shutil.copyfileobj(open(c.inputdir+'/fort.22','rb'), fout)
                shutil.copyfileobj(open(c.inputdir+'/flux'+cdate[0:2]+suffix,'rb'), fout)
                shutil.copyfileobj(open(c.inputdir+'/fort.16','rb'), fout)
                orolsm=glob.glob(c.inputdir+'/OG_OROLSM__SL.*.'+c.ppid+'*')[0]
                shutil.copyfileobj(open(orolsm,'rb'), fout)
                fout.close()
                if c.omega=='1':
                    fnout=c.outputdir+'/OMEGA'+suffix
                    fout = open(fnout,'wb')
                    shutil.copyfileobj(open(c.inputdir+'/fort.25','rb'), fout)



        try:
            if c.wrf=='1':
                fwrf.close()
        except:
            pass

        grib_index_release(iid)

        return

    def deacc_fluxes(self, inputfiles, c):

        table128=init128(c.flexextractdir+'/grib_templates/ecmwf_grib1_table_128')
        pars=toparamId(self.params['OG_acc_SL'][0],table128)
        if '/' in c.number:
            index_keys=["number","date","time","step"]
        else:
            index_keys=["date","time","step"]
        indexfile=c.inputdir+"/date_time_stepRange.idx"
        silentremove(indexfile)
        grib=GribTools(inputfiles.files)
        iid=grib.index(index_keys=index_keys, index_file = indexfile)

        print 'index done...'

        index_vals = []
        for key in index_keys:
            key_vals = grib_index_get(iid,key)
            print(key_vals)
            l=[]
            for k in key_vals:
                l.append(int(k))
            l.sort()
            key_vals=[]
            for k in l:
                key_vals.append(str(k))
            print key_vals
            index_vals.append(key_vals)


        valsdict={}
        svalsdict={}
        stepsdict={}
        for p in pars:
            valsdict[str(p)]=[]
            svalsdict[str(p)]=[]
            stepsdict[str(p)]=[]

        for prod in product(*index_vals):
            for i in range(len(index_keys)):
                grib_index_select(iid,index_keys[i],prod[i])

            #for k,f in fdict.iteritems():
                #fdict[k] = open('fort.'+k,'w')
            gid = grib_new_from_index(iid)
            hid = gid
            cflextime = None
            if gid is not None:
                cdate = grib_get(gid, 'date')
                #cyear = cdate[:4]
                #cmonth = cdate[4:6]
                #cday = cdate[6:8]
                time = grib_get(gid, 'time')
                type = grib_get(gid, 'type')
                step = grib_get(gid, 'step')
                # date+time+step-2*dtime (since interpolated value valid for step-2*dtime)
                sdate=datetime.datetime(year=cdate/10000,month=mod(cdate,10000)/100,
                                        day=mod(cdate,100),hour=time/100)
                fdate=sdate+datetime.timedelta(hours=step-2*int(c.dtime))
                sdates=sdate+datetime.timedelta(hours=step)
            else:
                break

            fnout=c.inputdir+'/'
            numbersuffix=''
            try:
                numberindex=index_keys.index('number')
                if len(index_vals[numberindex])>1:
                    numbersuffix='.N{:0>3}'.format(int(prod[numberindex]))
            except:
                pass

            if c.maxstep>12:
                fnout+='flux'+sdate.strftime('%Y%m%d')+'.{:0>2}'.format(time/100)+'.{:0>3}'.format(step-2*int(c.dtime))+numbersuffix
                gnout=c.inputdir+'/flux'+sdate.strftime('%Y%m%d')+'.{:0>2}'.format(time/100)+'.{:0>3}'.format(step-int(c.dtime))+numbersuffix
                hnout=c.inputdir+'/flux'+sdate.strftime('%Y%m%d')+'.{:0>2}'.format(time/100)+'.{:0>3}'.format(step)+numbersuffix
                g=open(gnout,'w')
                h=open(hnout,'w')
            else:
                fnout+='flux'+fdate.strftime('%Y%m%d%H')+numbersuffix
                gnout=c.inputdir+'/flux'+(fdate+datetime.timedelta(hours=int(c.dtime))).strftime('%Y%m%d%H')+numbersuffix
                hnout=c.inputdir+'/flux'+sdates.strftime('%Y%m%d%H')+numbersuffix
                g=open(gnout,'w')
                h=open(hnout,'w')
            print "outputfile = " + fnout
            f=open(fnout,'w')

            while 1:
                if gid is None: break
                cparamId = str(grib_get(gid, 'paramId'))
                step = grib_get(gid, 'step')
                atime = grib_get(gid, 'time')
                ni=grib_get(gid, 'Ni')
                nj=grib_get(gid, 'Nj')
                if cparamId in valsdict.keys():
                    values = grib_get_values(gid)
                    vdp=valsdict[cparamId]
                    svdp=svalsdict[cparamId]
                    sd=stepsdict[cparamId]

                    if cparamId=='142' or cparamId=='143':
                        fak=1./1000.
                    else:
                        fak=3600.

                    values=(reshape(values,(nj,ni))).flatten()/fak
                    vdp.append(values[:]) # save the accumulated values
                    if c.marsclass.upper() in ('EA') or \
                       step<=int(c.dtime):
                        svdp.append(values[:]/int(c.dtime))
                    else:
                        svdp.append((vdp[-1]-vdp[-2])/int(c.dtime))

                    print cparamId,atime,step,len(values),values[0],std(values)
                    #svdp.append(values[:]) # save the 1-hourly or 3-hourly specific values
                    sd.append(step)
                    if len(svdp)>=3:
                        if len(svdp)>3:
                            if cparamId=='142' or cparamId=='143':
                                values=darain(svdp)
                            else:
                                values=dapoly(svdp)

                            if not (step==c.maxstep and c.maxstep>12 or sdates==elimit):
                                vdp.pop(0)
                                svdp.pop(0)
                        else:
                            if c.maxstep>12:
                                values=svdp[1]
                            else:
                                values=svdp[0]

                        grib_set_values(gid, values)
                        if c.maxstep>12:
                            grib_set(gid,'stepRange',max(0,step-2*int(c.dtime)))
                        else:
                            grib_set(gid,'stepRange',0)
                            grib_set(gid,'time',fdate.hour*100)
                            grib_set(gid,'date',fdate.year*10000+fdate.month*100+fdate.day)
                        grib_write(gid, f)

                        if c.basetime is not None:
                            elimit=datetime.datetime.strptime(c.end_date+c.basetime,'%Y%m%d%H')
                        else:
                            elimit=sdate+datetime.timedelta(2*int(c.dtime))

                        # squeeze out information of last two steps contained in svdp
    #			if step+int(c.dtime)==c.maxstep and c.maxstep>12 or sdates+datetime.timedelta(hours=int(c.dtime))>=elimit:
    #                       Note that svdp[0] has not been popped in this case


                        if step==c.maxstep and c.maxstep>12 or sdates==elimit:
                            values=svdp[3]
                            grib_set_values(gid, values)
                            grib_set(gid,'stepRange',0)
                            truedatetime=fdate+datetime.timedelta(hours=2*int(c.dtime))
                            grib_set(gid,'time',truedatetime.hour*100)
                            grib_set(gid,'date',truedatetime.year*10000+truedatetime.month*100+truedatetime.day)
                            grib_write(gid, h)

                            #values=(svdp[1]+svdp[2])/2.
                            if cparamId=='142' or cparamId=='143':
                                values=darain(list(reversed(svdp)))
                            else:
                                values=dapoly(list(reversed(svdp)))

                            grib_set(gid,'stepRange',0)
                            truedatetime=fdate+datetime.timedelta(hours=int(c.dtime))
                            grib_set(gid,'time',truedatetime.hour*100)
                            grib_set(gid,'date',truedatetime.year*10000+truedatetime.month*100+truedatetime.day)
                            grib_set_values(gid, values)
                            grib_write(gid, g)

                    grib_release(gid)

                gid = grib_new_from_index(iid)

            f.close()
            g.close()
            h.close()


        grib_index_release(iid)
