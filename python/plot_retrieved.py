#!/usr/bin/env python
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# Functionality provided: Simple tool for creating maps and time series of retrieved fields.
#
# Requirements:
# in addition to a standard python 2.6 or 2.7 installation the following packages need to be installed
# ECMWF WebMARS, gribAPI with python enabled, emoslib, ecaccess web toolkit, all available from https://software.ecmwf.int/
# dateutils
# matplotlib (optional, for debugging)

import datetime
import time
import os,inspect,sys,glob
import socket
# add path to submit.py to pythonpath so that python finds its buddies
localpythonpath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if localpythonpath not in sys.path:
    sys.path.append(localpythonpath)

from matplotlib.pylab import *
import matplotlib.patches as mpatches
from mpl_toolkits.basemap import Basemap,addcyclic
import matplotlib.colors as mcolors
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon
import matplotlib.cm as cmx
import matplotlib.colors as colors
from argparse import ArgumentParser,ArgumentDefaultsHelpFormatter

from Tools import interpret_args_and_control, silentremove, product
from Control import Control
from GribTools import GribTools
from gribapi import *
from rasotools.utils import stats

def plot_retrieved(args,c):

    start = datetime.datetime.strptime(c.start_date,'%Y%m%d%H')
    end = datetime.datetime.strptime(c.end_date,'%Y%m%d%H')

    c.paramIds=asarray(c.paramIds,dtype='int')
    c.levels=asarray(c.levels,dtype='int')
    c.area=asarray(c.area)

    index_keys=["date","time","step"]
    indexfile=c.inputdir+"/date_time_stepRange.idx"
    silentremove(indexfile)
    files=glob.glob(c.inputdir+'/'+c.prefix+'*')
    grib=GribTools(files)
    iid=grib.index(index_keys=index_keys, index_file = indexfile)

    gdict=dict(Ni = 360, Nj = 181,  iScansNegatively = 0,  jScansPositively = 0,
               jPointsAreConsecutive = 0,  alternativeRowScanning = 0,
               latitudeOfFirstGridPointInDegrees = 90,
               longitudeOfFirstGridPointInDegrees = 181,
               latitudeOfLastGridPointInDegrees = -90,
               longitudeOfLastGridPointInDegrees = 180,
               iDirectionIncrementInDegrees = 1,
               jDirectionIncrementInDegrees = 1
               )

    index_vals = []
    for key in index_keys:
        key_vals = grib_index_get(iid,key)
        print key_vals

        index_vals.append(key_vals)

    fdict=dict()
    fmeta=dict()
    fstamp=dict()
    for p in c.paramIds:
        for l in c.levels:
            key='{:0>3}_{:0>3}'.format(p,l)
            fdict[key]=[]
            fmeta[key]=[]
            fstamp[key]=[]
    for prod in product(*index_vals):
        for i in range(len(index_keys)):
            grib_index_select(iid,index_keys[i],prod[i])

        gid = grib_new_from_index(iid)
#        if gid is not None:

        while(gid is not None):
            date = grib_get(gid, 'date')
            fdate= datetime.datetime(date/10000,mod(date,10000)/100,mod(date,100))
            gtime = grib_get(gid, 'time')
            step = grib_get(gid, 'step')
            fdatetime=fdate+datetime.timedelta(hours=gtime/100)
#            if fdatetime<start or fdatetime>end:
#                break
            gtype = grib_get(gid, 'type')
            paramId = grib_get(gid, 'paramId')
            parameterName = grib_get(gid, 'parameterName')
            level=grib_get(gid,'level')
            if step>=c.start_step and step <=c.end_step and fdatetime>=start and fdatetime<=end and paramId in c.paramIds and level in c.levels:
                key='{:0>3}_{:0>3}'.format(paramId,level)
                print key
                fdatetimestep=fdatetime+datetime.timedelta(hours=step)
                if len(fstamp)==0:
                    fstamp[key].append(fdatetimestamp)
                    fmeta[key].append((paramId,parameterName,gtype,fdatetime,gtime,step,level))
                    fdict[key].append(flipud(reshape(grib_get_values(gid),[gdict['Nj'],gdict['Ni']])))
                else:
                    i=0
                    inserted=False
                    for i in range(len(fstamp[key])):
                        if fdatetimestep<fstamp[key][i]:
                            fstamp[key][i:i]=[fdatetimestep]
                            fmeta[key][i:i]=[(paramId,parameterName,gtype,fdatetime,gtime,step,level)]
                            fdict[key][i:i]=[flipud(reshape(grib_get_values(gid),[gdict['Nj'],gdict['Ni']]))]
                            inserted=True
                            break
                    if not inserted:
                        fstamp[key].append(fdatetimestep)
                        fmeta[key].append((paramId,parameterName,gtype,fdatetime,gtime,step,level))
                        fdict[key].append(flipud(reshape(grib_get_values(gid),[gdict['Nj'],gdict['Ni']])))


            grib_release(gid)
            gid = grib_new_from_index(iid)

    for k in fdict.keys():
        fml=fmeta[k]
        fdl=fdict[k]

        for fd,fm in zip(fdl,fml):
            ftitle=fm[1]+' {} '.format(fm[-1])+datetime.datetime.strftime(fm[3],'%Y%m%d%H')+' '+stats(fd)
            pname='_'.join(fm[1].split())+'_{}_'.format(fm[-1])+datetime.datetime.strftime(fm[3],'%Y%m%d%H')+'.{:0>3}'.format(fm[5])
            plotmap(fd, fm,gdict,ftitle,pname+'.eps')

    for k in fdict.keys():
        fml=fmeta[k]
        fdl=fdict[k]
        fsl=fstamp[k]
        if fdl:
            fm=fml[0]
            fd=fdl[0]
            ftitle=fm[1]+' {} '.format(fm[-1])+datetime.datetime.strftime(fm[3],'%Y%m%d%H')+' '+stats(fd)
            pname='_'.join(fm[1].split())+'_{}_'.format(fm[-1])+datetime.datetime.strftime(fm[3],'%Y%m%d%H')+'.{:0>3}'.format(fm[5])
            lat=-20
            lon=20
            plottimeseries(fdl,fml,fsl,lat,lon, gdict, ftitle, pname+'.eps')

def plottimeseries(flist,fmetalist,ftimestamps,lat,lon,gdict,ftitle,filename):
    t1=time.time()
    latindex=(lat+90)*180/(gdict['Nj']-1)
    lonindex=(lon+179)*360/gdict['Ni']
    farr=asarray(flist)
    ts=farr[:,latindex,lonindex]
    f=plt.figure(figsize=(12,6.7))
    plt.plot(ftimestamps,ts)
    plt.title(ftitle)
    savefig(c.outputdir+'/'+filename)
    print 'created ',c.outputdir+'/'+filename
    plt.close(f)
    print time.time()-t1,'s'

def plotmap(flist,fmetalist,gdict,ftitle,filename):
    t1=time.time()
    f=plt.figure(figsize=(12,6.7))
    mbaxes = f.add_axes([0.05, 0.15, 0.8, 0.7])
    m =Basemap(llcrnrlon=-180.,llcrnrlat=-90.,urcrnrlon=180,urcrnrlat=90.)
    #if bw==0 :
        #fill_color=rgb(0.6,0.8,1)
    #else:
        #fill_color=rgb(0.85,0.85,0.85)

    lw=0.3
    m.drawmapboundary()
    parallels = arange(-90.,91,90.)
    # labels = [left,right,top,bottom]
    m.drawparallels(parallels,labels=[True,True,True,True],linewidth=lw)
    meridians = arange(-180.,181.,60.)
    m.drawmeridians(meridians,labels=[True,True,True,True],linewidth=lw)
    m.drawcoastlines(linewidth=lw)
    xleft=gdict['longitudeOfFirstGridPointInDegrees']
    if xleft>180.0:
        xleft-=360.
    x=linspace(xleft,gdict['longitudeOfLastGridPointInDegrees'],gdict['Ni'])
    y=linspace(gdict['latitudeOfLastGridPointInDegrees'],gdict['latitudeOfFirstGridPointInDegrees'],gdict['Nj'])
    xx, yy = m(*meshgrid(x,y))

    s=m.contourf(xx,yy, flist)
    title(ftitle,y=1.1)
    cbaxes = f.add_axes([0.9, 0.2, 0.04, 0.6])
    cb=colorbar(cax=cbaxes)

    savefig(c.outputdir+'/'+filename)
    print 'created ',c.outputdir+'/'+filename
    plt.close(f)
    print time.time()-t1,'s'


def interpret_plotargs(*args,**kwargs):

    parser = ArgumentParser(description='Retrieve FLEXPART input from ECMWF MARS archive',
                            formatter_class=ArgumentDefaultsHelpFormatter)

# the most important arguments
    parser.add_argument("--start_date", dest="start_date",
                        help="start date YYYYMMDD")
    parser.add_argument( "--end_date", dest="end_date",
                         help="end_date YYYYMMDD")

    parser.add_argument("--start_step", dest="start_step",
                        help="start step in hours")
    parser.add_argument( "--end_step", dest="end_step",
                         help="end_step in hours")

# some arguments that override the default in the control file
    parser.add_argument("--levelist", dest="levelist",help="Vertical levels to be retrieved, e.g. 30/to/60")
    parser.add_argument("--area", dest="area", help="area defined as north/west/south/east")
    parser.add_argument("--paramIds", dest="paramIds", help="parameter IDs")
    parser.add_argument("--prefix", dest="prefix",default='EN', help="output file name prefix")

# set the working directories
    parser.add_argument("--inputdir", dest="inputdir",default=None,
                        help="root directory for storing intermediate files")
    parser.add_argument("--outputdir", dest="outputdir",default=None,
                        help="root directory for storing output files")
    parser.add_argument("--flexpart_root_scripts", dest="flexpart_root_scripts",
                        help="FLEXPART root directory (to find grib2flexpart and COMMAND file)\n\
                              Normally ECMWFDATA resides in the scripts directory of the FLEXPART distribution")

    parser.add_argument("--controlfile", dest="controlfile",default='CONTROL.temp',
                        help="file with control parameters")
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

    if args.levelist:
        c.levels=args.levelist.split('/')
    else:
        c.levels=[0]
    if args.area:
        c.area=args.area.split('/')
    else:
        c.area='[0,0]'

    c.paramIds=args.paramIds.split('/')
    if args.start_step:
        c.start_step=int(args.start_step)
    else:
        c.start_step=0
    if args.end_step:
        c.end_step=int(args.end_step)
    else:
        c.end_step=0

    c.start_date=args.start_date
    c.end_date=args.end_date
    c.prefix=args.prefix
    c.inputdir=args.inputdir
    if args.outputdir:
        c.outputdir=args.outputdir
    else:
        c.outputdir=c.inputdir

        return args,c

if __name__ == "__main__":

    args,c=interpret_plotargs()
    plot_retrieved(args,c)
