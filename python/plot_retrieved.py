#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# TODO AP
# - documentation der Funktionen
# - docu der progam functionality
# - apply pep8
#************************************************************************
#*******************************************************************************
# @Author: Leopold Haimberger (University of Vienna)
#
# @Date: November 2015
#
# @Change History:
#
#    February 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - created function main and moved the two function calls for
#          arguments and plotting into it
#        - added function getBasics to extract the boundary conditions
#          of the data fields from the first grib file it gets.
#
# @License:
#    (C) Copyright 2015-2018.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Program Functionality:
#    Simple tool for creating maps and time series of retrieved fields.
#
# @Program Content:
#    - main
#    - getBasics
#    - plotRetrieved
#    - plotTS
#    - plotMap
#    - getPlotArgs
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import time
import datetime
import os
import inspect
import sys
import glob
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from matplotlib.pylab import *
import matplotlib.patches as mpatches
from mpl_toolkits.basemap import Basemap, addcyclic
import matplotlib.colors as mcolors
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon
import matplotlib.cm as cmx
import matplotlib.colors as colors
#from rasotools.utils import stats

font = {'family': 'monospace', 'size': 12}
matplotlib.rcParams['xtick.major.pad'] = '20'

matplotlib.rc('font', **font)

from eccodes import *
import numpy as np

# add path to pythonpath so that python finds its buddies
localpythonpath = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
if localpythonpath not in sys.path:
    sys.path.append(localpythonpath)

# software specific classes and modules from flex_extract
from Tools import silentremove
from ControlFile import ControlFile
#from GribTools import GribTools
from UIOFiles import UIOFiles

# ------------------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------------
def main():
    '''
    @Description:
        If plotRetrieved is called from command line, this function controls
        the program flow and calls the argumentparser function and
        the plotRetrieved function for plotting the retrieved GRIB data.

    @Input:
        <nothing>

    @Return:
        <nothing>
    '''
    args, c = getPlotArgs()
    plotRetrieved(args, c)

    return

def getBasics(ifile, verb=False):
    """
    @Description:
        An example grib file will be opened and basic information will
        be extracted. These information are important for later use and the
        initialization of numpy arrays for data storing.

    @Input:
        ifile: string
            Contains the full absolute path to the ECMWF grib file.
        verb (opt): bool
            Is True if there should be extra output in verbose mode.
            Default value is False.

    @Return:
        data: dict
            Contains basic informations of the ECMWF grib files, e.g.
            'Ni', 'Nj', 'latitudeOfFirstGridPointInDegrees',
            'longitudeOfFirstGridPointInDegrees',
            'latitudeOfLastGridPointInDegrees',
            'longitudeOfLastGridPointInDegrees',
            'jDirectionIncrementInDegrees',
            'iDirectionIncrementInDegrees'
    """
    from eccodes import *

    data = {}

    # --- open file ---
    print("Opening file for getting information data --- %s" %
          os.path.basename(ifile))

    with open(ifile) as f:

        # load first message from file
        gid = codes_grib_new_from_file(f)

        # information needed from grib message
        keys = [
                'Ni',
                'Nj',
                'latitudeOfFirstGridPointInDegrees',
                'longitudeOfFirstGridPointInDegrees',
                'latitudeOfLastGridPointInDegrees',
                'longitudeOfLastGridPointInDegrees',
                'jDirectionIncrementInDegrees',
                'iDirectionIncrementInDegrees'
               ]

        if verb: print('\nInformations are: ')
        for key in keys:
            # Get the value of the key in a grib message.
            data[key] = codes_get(gid,key)
            if verb: print "%s = %s" % (key,data[key])
        if verb: print '\n'

        # Free the memory for the message referred as gribid.
        codes_release(gid)

    return data

def getFilesPerDate(files, datelist):
    '''
    @Description:
        The filenames contain dates which are used to select a list
        of files for a specific time period specified in datelist.

    @Input:
        files: instance of UIOFiles
            For description see class documentation.
            It contains the attribute "files" which is a list of pathes
            to filenames.

        datelist: list of datetimes
            Contains the list of dates which should be processed for plotting.

    @Return:
        filelist: list of strings
            Contains the selected files for the time period.
    '''

    filelist = []
    for file in files:
        fdate = file[-8:]
        ddate = datetime.datetime.strptime(fdate, '%y%m%d%H')
        if ddate in datelist:
            filelist.append(file)

    return filelist

def plotRetrieved(args, c):
    '''
    @Description:
        Reads GRIB data from a specified time period, a list of levels
        and a specified list of parameter.

    @Input:
        args: instance of ArgumentParser
            Contains the commandline arguments from script/program call.

        c: instance of class ControlFile
            Contains all necessary information of a CONTROL file. The parameters
            are: DAY1, DAY2, DTIME, MAXSTEP, TYPE, TIME, STEP, CLASS, STREAM,
            NUMBER, EXPVER, GRID, LEFT, LOWER, UPPER, RIGHT, LEVEL, LEVELIST,
            RESOL, GAUSS, ACCURACY, OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA,
            SMOOTH, FORMAT, ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS,
            ECFSDIR, MAILOPS, MAILFAIL, GRIB2FLEXPART, DEBUG, INPUTDIR,
            OUTPUTDIR, FLEXPART_ROOT_SCRIPTS
            For more information about format and content of the parameter see
            documentation.

    @Return:
        <nothing>
    '''
    start = datetime.datetime.strptime(c.start_date, '%Y%m%d%H')
    end = datetime.datetime.strptime(c.end_date, '%Y%m%d%H')

    # create datelist between start and end date
    datelist = [start] # initialise datelist with first date
    run_date = start
    while run_date < end:
        run_date += datetime.timedelta(hours=int(c.dtime))
        datelist.append(run_date)

    print 'datelist: ', datelist

    c.paramIds = asarray(c.paramIds, dtype='int')
    c.levels = asarray(c.levels, dtype='int')
    c.area = asarray(c.area)

    # index_keys = ["date", "time", "step"]
    # indexfile = c.inputdir + "/date_time_stepRange.idx"
    # silentremove(indexfile)
    # grib = GribTools(inputfiles.files)
    # # creates new index file
    # iid = grib.index(index_keys=index_keys, index_file=indexfile)

    # # read values of index keys
    # index_vals = []
    # for key in index_keys:
        # index_vals.append(grib_index_get(iid, key))
        # print(index_vals[-1])
        # # index_vals looks for example like:
        # # index_vals[0]: ('20171106', '20171107', '20171108') ; date
        # # index_vals[1]: ('0', '1200', '1800', '600') ; time
        # # index_vals[2]: ('0', '12', '3', '6', '9') ; stepRange




    #index_keys = ["date", "time", "step", "paramId"]
    #indexfile = c.inputdir + "/date_time_stepRange.idx"
    #silentremove(indexfile)

    files = UIOFiles(c.prefix+'*')
    files.listFiles(c.inputdir)
    ifiles = getFilesPerDate(files.files, datelist)
    ifiles.sort()

    gdict = getBasics(ifiles[0], verb=False)

    fdict = dict()
    fmeta = dict()
    fstamp = dict()
    for p in c.paramIds:
        for l in c.levels:
            key = '{:0>3}_{:0>3}'.format(p, l)
            fdict[key] = []
            fmeta[key] = []
            fstamp[key] = []

    for file in ifiles:
        f = open(file)
        print( "Opening file for reading data --- %s" % file)
        fdate = datetime.datetime.strptime(file[-8:], "%y%m%d%H")

        # Load in memory a grib message from a file.
        gid = codes_grib_new_from_file(f)
        while(gid is not None):
            gtype = codes_get(gid, 'type')
            paramId = codes_get(gid, 'paramId')
            parameterName = codes_get(gid, 'parameterName')
            level = codes_get(gid, 'level')

            if paramId in c.paramIds and level in c.levels:
                key = '{:0>3}_{:0>3}'.format(paramId, level)
                print 'key: ', key
                if len(fstamp[key]) != 0 :
                    for i in range(len(fstamp[key])):
                        if fdate < fstamp[key][i]:
                            fstamp[key].insert(i, fdate)
                            fmeta[key].insert(i, [paramId, parameterName, gtype,
                                                fdate, level])
                            fdict[key].insert(i, flipud(reshape(
                                            codes_get_values(gid),
                                            [gdict['Nj'], gdict['Ni']])))
                            break
                        elif fdate > fstamp[key][i] and i == len(fstamp[key])-1:
                            fstamp[key].append(fdate)
                            fmeta[key].append([paramId, parameterName, gtype,
                                                fdate, level])
                            fdict[key].append(flipud(reshape(
                                            codes_get_values(gid),
                                            [gdict['Nj'], gdict['Ni']])))
                            break
                        elif fdate > fstamp[key][i] and i != len(fstamp[key])-1 \
                             and fdate < fstamp[key][i+1]:
                            fstamp[key].insert(i, fdate)
                            fmeta[key].insert(i, [paramId, parameterName, gtype,
                                                    fdate, level])
                            fdict[key].insert(i, flipud(reshape(
                                            codes_get_values(gid),
                                            [gdict['Nj'], gdict['Ni']])))
                            break
                        else:
                            pass
                else:
                    fstamp[key].append(fdate)
                    fmeta[key].append((paramId, parameterName, gtype,
                                       fdate, level))
                    fdict[key].append(flipud(reshape(
                        codes_get_values(gid), [gdict['Nj'], gdict['Ni']])))

            codes_release(gid)

            # Load in memory a grib message from a file.
            gid = codes_grib_new_from_file(f)

        f.close()
    #print 'fstamp: ', fstamp
    #exit()

    for k in fdict.keys():
        print 'fmeta: ', len(fmeta),fmeta
        fml = fmeta[k]
        fdl = fdict[k]
        print 'fm1: ', len(fml), fml
        #print 'fd1: ', fdl
        #print zip(fdl, fml)
        for fd, fm in zip(fdl, fml):
            print fm
            ftitle = fm[1] + ' {} '.format(fm[-1]) + \
                datetime.datetime.strftime(fm[3], '%Y%m%d%H') #+ ' ' + stats(fd)
            pname = '_'.join(fm[1].split()) + '_{}_'.format(fm[-1]) + \
                datetime.datetime.strftime(fm[3], '%Y%m%d%H')
            plotMap(c, fd, fm, gdict, ftitle, pname, 'png')

    for k in fdict.keys():
        fml = fmeta[k]
        fdl = fdict[k]
        fsl = fstamp[k]
        if fdl:
            fm = fml[0]
            fd = fdl[0]
            ftitle = fm[1] + ' {} '.format(fm[-1]) + \
                datetime.datetime.strftime(fm[3], '%Y%m%d%H') #+ ' ' + stats(fd)
            pname = '_'.join(fm[1].split()) + '_{}_'.format(fm[-1]) + \
                datetime.datetime.strftime(fm[3], '%Y%m%d%H')
            lat = -20
            lon = 20
            plotTS(c, fdl, fml, fsl, lat, lon,
                           gdict, ftitle, pname, 'png')

    return

def plotTS(c, flist, fmetalist, ftimestamps, lat, lon,
                   gdict, ftitle, filename, fending, show=False):
    '''
    @Description:

    @Input:
        c:

        flist:
            The actual data values to be plotted from the grib messages.

        fmetalist: list of strings
            Contains some meta date for the data field to be plotted:
            parameter id, parameter Name, grid type, datetime, level

        ftimestamps: list of datetime
            Contains the time stamps.

        lat:

        lon:

        gdict:

        ftitle: string
            The title of the timeseries.

        filename: string
            The time series is stored in a file with this name.

        fending: string
            Contains the type of plot, e.g. pdf or png

        show: boolean
            Decides if the plot is shown after plotting or hidden.

    @Return:
        <nothing>
    '''
    print 'plotting timeseries'

    t1 = time.time()

    llx = gdict['longitudeOfFirstGridPointInDegrees']
    if llx > 180. :
        llx -= 360.
    lly = gdict['latitudeOfLastGridPointInDegrees']
    dxout = gdict['iDirectionIncrementInDegrees']
    dyout = gdict['jDirectionIncrementInDegrees']
    urx = gdict['longitudeOfLastGridPointInDegrees']
    ury = gdict['latitudeOfFirstGridPointInDegrees']
    numxgrid = gdict['Ni']
    numygrid = gdict['Nj']

    farr = asarray(flist)
    #(time, lat, lon)

    lonindex = linspace(llx, urx, numxgrid)
    latindex = linspace(lly, ury, numygrid)
    #print len(lonindex), len(latindex), farr.shape

    #latindex = (lat + 90) * 180 / (gdict['Nj'] - 1)
    #lonindex = (lon + 179) * 360 / gdict['Ni']
    #print latindex, lonindex


    ts = farr[:, 0, 0]#latindex[0], lonindex[0]]

    fig = plt.figure(figsize=(12, 6.7))

    plt.plot(ftimestamps, ts)
    plt.title(ftitle)

    plt.savefig(c.outputdir+'/'+filename+'_TS.'+fending, facecolor=fig.get_facecolor(), edgecolor='none',format=fending)
    print 'created ', c.outputdir + '/' + filename
    if show == True:
        plt.show()
    fig.clf()
    plt.close(fig)

    print time.time() - t1, 's'

    return

def plotMap(c, flist, fmetalist, gdict, ftitle, filename, fending, show=False):
    '''
    @Description:

    @Input:
        c: instance of class ControlFile
            Contains all necessary information of a CONTROL file. The parameters
            are: DAY1, DAY2, DTIME, MAXSTEP, TYPE, TIME, STEP, CLASS, STREAM,
            NUMBER, EXPVER, GRID, LEFT, LOWER, UPPER, RIGHT, LEVEL, LEVELIST,
            RESOL, GAUSS, ACCURACY, OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA,
            SMOOTH, FORMAT, ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS,
            ECFSDIR, MAILOPS, MAILFAIL, GRIB2FLEXPART, DEBUG, INPUTDIR,
            OUTPUTDIR, FLEXPART_ROOT_SCRIPTS
            For more information about format and content of the parameter see
            documentation.

        flist

        fmetalist

        gdict: dict
            Contains basic informations of the ECMWF grib files, e.g.
            'Ni', 'Nj', 'latitudeOfFirstGridPointInDegrees',
            'longitudeOfFirstGridPointInDegrees',
            'latitudeOfLastGridPointInDegrees',
            'longitudeOfLastGridPointInDegrees',
            'jDirectionIncrementInDegrees',
            'iDirectionIncrementInDegrees'

        ftitle: string
            The titel of the plot.

        filename: string
            The plot is stored in a file with this name.

        fending: string
            Contains the type of plot, e.g. pdf or png

        show: boolean
            Decides if the plot is shown after plotting or hidden.

    @Return:
        <nothing>
    '''
    print 'plotting map'

    t1 = time.time()

    fig = plt.figure(figsize=(12, 6.7))
    #mbaxes = fig.add_axes([0.05, 0.15, 0.8, 0.7])

    llx = gdict['longitudeOfFirstGridPointInDegrees'] #- 360
    if llx > 180. :
        llx -= 360.
    lly = gdict['latitudeOfLastGridPointInDegrees']
    dxout = gdict['iDirectionIncrementInDegrees']
    dyout = gdict['jDirectionIncrementInDegrees']
    urx = gdict['longitudeOfLastGridPointInDegrees']
    ury = gdict['latitudeOfFirstGridPointInDegrees']
    numxgrid = gdict['Ni']
    numygrid = gdict['Nj']

    m = Basemap(projection='cyl', llcrnrlon=llx, llcrnrlat=lly,
                urcrnrlon=urx, urcrnrlat=ury,resolution='i')

    lw = 0.5
    m.drawmapboundary()
    x = linspace(llx, urx, numxgrid)
    y = linspace(lly, ury, numygrid)

    xx, yy = m(*meshgrid(x, y))

    #s = m.contourf(xx, yy, flist)

    s = plt.imshow(flist.T,
                    extent=(llx, urx, lly, ury),
                    alpha=1.0,
                    interpolation='nearest'
                    #vmin=vn,
                    #vmax=vx,
                    #cmap=my_cmap,
                    #levels=levels,
                    #cmap=my_cmap,
                    #norm=LogNorm(vn,vx)
                    )

    title(ftitle, y=1.08)
    cb = m.colorbar(s, location="right", pad="10%")
    #cb.set_label('Contribution per cell (ng m$^{-3}$)',size=14)

    thickline = np.arange(lly,ury+1,10.)
    thinline  = np.arange(lly,ury+1,5.)
    m.drawparallels(thickline,color='gray',dashes=[1,1],linewidth=0.5,labels=[1,1,1,1], xoffset=1.) # draw parallels
    m.drawparallels(np.setdiff1d(thinline,thickline),color='lightgray',dashes=[1,1],linewidth=0.5,labels=[0,0,0,0]) # draw parallels

    thickline = np.arange(llx,urx+1,10.)
    thinline  = np.arange(llx,urx+1,5.)
    m.drawmeridians(thickline,color='gray',dashes=[1,1],linewidth=0.5,labels=[1,1,1,1],yoffset=1.) # draw meridians
    m.drawmeridians(np.setdiff1d(thinline,thickline),color='lightgray',dashes=[1,1],linewidth=0.5,labels=[0,0,0,0]) # draw meridians

    m.drawcoastlines()
    m.drawcountries()

    plt.savefig(c.outputdir+'/'+filename+'_MAP.'+fending, facecolor=fig.get_facecolor(), edgecolor='none',format=fending)
    print 'created ', c.outputdir + '/' + filename
    if show == True:
        plt.show()
    fig.clf()
    plt.close(fig)

    print time.time() - t1, 's'

    return

def getPlotArgs():
    '''
    @Description:
        Assigns the command line arguments and reads CONTROL file
        content. Apply default values for non mentioned arguments.

    @Input:
        <nothing>

    @Return:
        args: instance of ArgumentParser
            Contains the commandline arguments from script/program call.

        c: instance of class ControlFile
            Contains all necessary information of a CONTROL file. The parameters
            are: DAY1, DAY2, DTIME, MAXSTEP, TYPE, TIME, STEP, CLASS, STREAM,
            NUMBER, EXPVER, GRID, LEFT, LOWER, UPPER, RIGHT, LEVEL, LEVELIST,
            RESOL, GAUSS, ACCURACY, OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA,
            SMOOTH, FORMAT, ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS,
            ECFSDIR, MAILOPS, MAILFAIL, GRIB2FLEXPART, DEBUG, INPUTDIR,
            OUTPUTDIR, FLEXPART_ROOT_SCRIPTS
            For more information about format and content of the parameter see
            documentation.
    '''
    parser = ArgumentParser(description='Plot retrieved GRIB data from ' + \
                            'ECMWF MARS archive',
                            formatter_class=ArgumentDefaultsHelpFormatter)

# the most important arguments
    parser.add_argument("--start_date", dest="start_date",
                        help="start date YYYYMMDD")
    parser.add_argument( "--end_date", dest="end_date",
                         help="end_date YYYYMMDD")

    parser.add_argument("--start_step", dest="start_step",
                        help="start step in hours")
    parser.add_argument( "--end_step", dest="end_step",
                         help="end step in hours")

# some arguments that override the default in the CONTROL file
    parser.add_argument("--levelist", dest="levelist",
                        help="vertical levels to be retrieved, e.g. 30/to/60")
    parser.add_argument("--area", dest="area",
                        help="area defined as north/west/south/east")
    parser.add_argument("--paramIds", dest="paramIds",
                        help="parameter IDs")
    parser.add_argument("--prefix", dest="prefix", default='EN',
                        help="output file name prefix")

# set the working directories
    parser.add_argument("--inputdir", dest="inputdir", default=None,
                        help="root directory for storing intermediate files")
    parser.add_argument("--outputdir", dest="outputdir", default=None,
                        help="root directory for storing output files")
    parser.add_argument("--flexpart_root_scripts", dest="flexpart_root_scripts",
                        help="FLEXPART root directory (to find \
                        'grib2flexpart and COMMAND file)\n \
                        Normally ECMWFDATA resides in the scripts directory \
                        of the FLEXPART distribution")

    parser.add_argument("--controlfile", dest="controlfile",
                        default='CONTROL.temp',
                        help="file with CONTROL parameters")
    args = parser.parse_args()

    try:
        c = ControlFile(args.controlfile)
    except IOError:
        try:
            c = ControlFile(localpythonpath + args.controlfile)

        except:
            print 'Could not read CONTROL file "' + args.controlfile + '"'
            print 'Either it does not exist or its syntax is wrong.'
            print 'Try "' + sys.argv[0].split('/')[-1] + \
                  ' -h" to print usage information'
            exit(1)

    if args.levelist:
        c.levels = args.levelist.split('/')
    else:
        c.levels = [0]

    if args.area:
        c.area = args.area.split('/')
    else:
        c.area = '[0,0]'

    c.paramIds = args.paramIds.split('/')

    if args.start_step:
        c.start_step = int(args.start_step)
    else:
        c.start_step = 0

    if args.end_step:
        c.end_step = int(args.end_step)
    else:
        c.end_step = 0

    c.start_date = args.start_date
    c.end_date = args.end_date

    c.prefix = args.prefix

    c.inputdir = args.inputdir

    if args.outputdir:
        c.outputdir = args.outputdir
    else:
        c.outputdir = c.inputdir

    return args, c

if __name__ == "__main__":
    main()

