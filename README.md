# flex_extract 

`flex_extract` is a software package to support retrieving meteorological fields from the ECMWF MARS archive as input for the `FLEXTRA`/`FLEXPART` Atmospheric Transport Modelling system.

`FLEXPART` (“FLEXible PARTicle dispersion model”) is a Lagrangian transport and dispersion model suitable for the simulation of a large range of atmospheric transport processes.

`FLEXPART` expects GRIB files containing a set of meteorological fields separated by time. The format of these file names look like: `<prefix>YYMMDDHH`, where `<prefix>` can be defined by the user (usually it should be limited to "2" characters because of further processing reasons). 

The MARS (Meteorological Archival and Retrieval System) archive from ECMWF saves a number of different data sets, such as the ERA-Interim and ERA 5 reanalysis and the daily operational data. More can be found here: <https://confluence.ecmwf.int/display/UDOC/MARS+content>

To define the data set and its composition of, e.g. time, field types and paramaters, `flex_extract` uses `CONTROL` files to set a number of MARS keywords and `flex_extract` specific control parameters. Detailed description can be found in the documentation and a set of example `CONTROL` files are also distributed with `flex_extract`.





## ECMWF DATA


There are two modes for accessing ECMWF data sets: the **_full access_** and the **_public access_** mode.
A description of these two modes and links to the available data sets is available here: https://www.ecmwf.int/en/forecasts/datasets/archive-datasets

####  Important note for public users

If you want to extract public data sets from the ECMWF servers you first have to register at the ECMWF. Do this by following the instructions at: https://software.ecmwf.int/wiki/display/WEBAPI/Access+MARS

Afterwards you **_need to accept the licenses_** of the data sets you want to extract: 

https://software.ecmwf.int/wiki/display/WEBAPI/Available+ECMWF+Public+Datasets

Now your able to use `flex_extract` in public mode (command line parameter "*--public=1*"). 






## Application modes

There are 4 different modes of running `flex_extract` :
1. Remote (*): ***flex_extract*** is installed and executed directly on the ECMWF Linux member state server ecgate. Users have to be a registered member-state user.
2. Gateway (*): ***flex_extract*** is installed on a local machine and the scripts are submitted to ECMWF
computer facilities via a member-state gateway server. Users have to be a registered member-state user.
3. Local member state (*): ***flex_extract*** is installed and executed on a local machine. Users have to be a registered member-state user.
4. Local public (**): ***flex_extract*** is installed and executed on a local machine. Users do not have to be a member-state user. A normal registration at the ECMWF website is enough. 

*(\*) To get a ms (member-state) user access, users have to be a resident of a [member state](https://www.ecmwf.int/en/about/who-we-are/member-states) and have to contact their national meteorological center for granting access.*

*(\*\*) To get a public user account, the user can just register at the ECMWF website following the instructions [here](https://apps.ecmwf.int/registration/)!*




<!--
[![NPM Version][npm-image]][npm-url]
[![Build Status][travis-image]][travis-url]
[![Downloads Stats][npm-downloads]][npm-url]


![](header.png)
-->








## Installation



### Requirements


To run the python part of flex_extract a [Python 3](https://docs.python.org/3/) environment is needed.<br>
We tested `flex_extract` with a normal Linux Python package distribution and Anaconda Python. 
* [Python3](https://www.python.org/downloads/) or [Anaconda Python 3](https://www.anaconda.com/distribution/#download-section)
* [numpy](http://www.numpy.org/)
* [ecmwf-api-client](https://confluence.ecmwf.int/display/WEBAPI/ECMWF+Web+API+Home)
* [cdsapi](https://cds.climate.copernicus.eu/api-how-to)
* [genshi](https://genshi.edgewall.org/)
* [eccodes for python](https://packages.debian.org/sid/python3-eccodes) (e.g. manually from source or from distribution package) or [eccodes for conda](https://anaconda.org/conda-forge/eccodes)
 
 For the Fortran part of flex_extract we need: 
 
 * [gfortran](https://gcc.gnu.org/wiki/GFortran)
 * [fftw3](http://www.fftw.org)
 * [eccodes](https://software.ecmwf.int/wiki/display/ECC)
 * [emoslib](https://software.ecmwf.int/wiki/display/EMOS/Emoslib)



###  Prepare the environment


##### On ecgate

All libraries and software packages needed by flex_extract are already installed on the ECMWF servers. They can be loaded by a module management system. In general, `flex_extract` is managing the correct settings of modules if you submit to the `ecgate` or `cca` queue. If the user works directly on ecgate, he has to assure that a Python3 environment is loaded before starting `flex_extract`. 

```bash
# on ecgate
module unload python
module load python3
```

##### On a local and a gateway machine

The easiest way to install all required packages is to use the package management system of the Linux distribution. If you have any problems with this method, you can ask for support or just try to install specific packages from source. 

_We are not describing the installation of a gateway server since this is out of scope. Please see [here](https://confluence.ecmwf.int/display/ECAC/ECaccess+Home)!_

On a Linux Debian or Ubuntu system:

```sh
# on your local system, do:
sudo apt -PV install python3
sudo apt -PV install pip3
sudo apt -PV install gfortran
sudo apt -PV install fftw3-dev 
sudo apt -PV install libeccodes-dev
sudo apt -PV install libemos-dev 
sudo apt -PV install python3-eccodes
pip3 install cdsapi 
pip3 install ecmwf-api-client
pip3 install genshi
pip3 install numpy
```

Afterwards, check the availability of the python packages:
```python
# check in python3 console
import eccodes
import cdsapi
import ecmwfapi
import genshi
```
Additionally, start simple test retrievals for both API's: 
```python
#!/usr/bin/env python3
from ecmwfapi import ECMWFDataServer
    
server = ECMWFDataServer()
    
server.retrieve({
    'stream'    : "oper",
    'levtype'   : "sfc",
    'param'     : "165.128/166.128/167.128",
    'dataset'   : "interim",
    'step'      : "0",
    'grid'      : "0.75/0.75",
    'time'      : "00/06/12/18",
    'date'      : "2014-07-01/to/2014-07-31",
    'type'      : "an",
    'class'     : "ei",
    'target'    : "download_ecmwfapi.grib"
})
```
```python
#!/usr/bin/env python
import cdsapi
c = cdsapi.Client()
c.retrieve("reanalysis-era5-pressure-levels",
{
"variable": "temperature",
"pressure_level": "1000",
"product_type": "reanalysis",
"year": "2008",
"month": "01",
"day": "01",
"time": "12:00",
"format": "grib"
},
"download_cdsapi.grib")
```
 


### Some important notes for a manual installation process:
- Use the same compiler and compiler version for all libraries and the Fortran program of `flex_extract`.
- Don't forget to set all library paths to the `LD_LIBRARY_PATH` variable.
- Don't forget to adapt the makefile for the Fortran program.
- Please follow the instructions on the websites of the libraries.

For the manual installation of these libraries it is useful to consider the official documentation (and also the hints from the ECMWF) rather than trying to explain every detail in here. Nevertheless, if you have to do the manual installation, we recommend doing the installation in the following order (see links to the libraries in the table above):


1. Read `Emoslib` [installation instructions](https://confluence.ecmwf.int/display/EMOS/Installation+Guide).
2. Read [ECMWF blog about gfortran](https://software.ecmwf.int/wiki/display/SUP/2015/05/11/Building+ECMWF+software+with+gfortran).
3. [Install `FFTW`](http://www.fftw.org/).
4. [Install `EMOSLIB`](https://confluence.ecmwf.int/display/EMOS/Emoslib) (Hint: Apply make 2 times! One time without any options and one time with single precision option).
5. [Install `ECCODES` from source](https://confluence.ecmwf.int/display/ECC/ecCodes+installation) from source (for python and fortran). `ECCODES` is downward compatible with `GRIB_API`. `GRIB_API` support was expire at the end of 2018.
6. For local usage and as public user, install the ECMWF key by following step 1 [here](https://confluence.ecmwf.int/display/WEBAPI/Access+ECMWF+Public+Datasets). 
7. [Install `ECMWF_Web API.`](https://confluence.ecmwf.int/display/WEBAPI/Access+ECMWF+Public+Datasets#AccessECMWFPublicDatasets-python)
8. [Install `CDS API.`](https://cds.climate.copernicus.eu/api-how-to)
9. Check `LD_LIBRARY_PATH `environment variable if it contains all paths to the libs. 
10. Do some tests as listed above.






### Installation of `flex_extract`


To install `flex_extract` you have to first decide which application mode you want to use and then, if you choosed one of the local version, edit the corresponding Makefile for the Fortran programm. Makefiles for ECMWF server are already fixed. 
For example: 
```bash
cd flex_extract_v7.1/source/fortran
nedit Makefile.local.gfortran
```
Edit the pathes to the ECCODES library on your local machine in this file:
```sh
ECCODES_INCLUDE_DIR=/usr/lib/
ECCODES_LIB= -L/usr/lib -leccodes_f90  -leccodes -lm  
```
Now go to the root directory and open the setup.sh file:
```bash
cd ../../
nedit setup.sh
```
In this file edit the labelled block for "AVAILABLE COMMANDLINE ARGUMENTS TO SET"
```bash
# -----------------------------------------------------------------
# AVAILABLE COMMANDLINE ARGUMENTS TO SET
#
# THE USER HAS TO SPECIFY THESE PARAMETER
#
TARGET='ecgate'
MAKEFILE='Makefile.gfortran'
ECUID='uid'
ECGID='gid'
GATEWAY='server.example.edu'
DESTINATION='example@genericSftp'
FLEXPARTDIR=""
JOB_TEMPLATE="job.template"
CONTROLFILE="CONTROL_EA5.testgrid"
```









```
./setup.sh
```


On ECMWF servers a makefile named "Makefile.gfortran" is already provided in the "source/fortran"-directory. It is also the default makefile, so that the parameter does not have to be set when calling "install.py".

If the ***flex_extract*** is to be installed within a ***FLEXPART*** environment it should be called with the parameter `flexpart_root_scripts` to let ***flex_extract*** know about the path to ***FLEXPART***.

The installation was successful if the compilation of the Fortran program ``CONVERT2`` didn't fail and is displayed in the terminal. 

#### Installation using a gateway server (***flex_extract*** mode 2 only)

---

If the user has a gateway server and the Ecaccess toolkit available, ***flex_extract*** can be installed such that it is executed on the local machine and a job script is submitted to the ECMWF server. The final ***FLEXPART*** input files are then send back via the Ecaccess command line tool "ectrans". To use this tool, the user has to create an association directly on the local gateway server via the localhost ecaccess.ecmwf.int and provide the association name as the "destination"-parameter when calling "install.py". 

The gateway server has to be registered at ECMWF. For information about a gateway server see: 
- https://software.ecmwf.int/wiki/display/ECAC/Releases+-+Gateway+package
- and the Software Installation Plan (SIP.pdf) in the docs/ directory.

Afterwards ***flex_extract*** can be installed with the following command:
```
./install.py --target=local --makefile=Makefile.gfortan --ecuid=<id> --ecgid=<gid> --gateway=<servername> --destination=<destinationname>
```

If the installation was successful the user gets an email with a success note!




## How to use flex_extract

A few motivating and useful examples of how your product can be used. Spice this up with code blocks and potentially more screenshots.

_For more examples and usage, please refer to the [Wiki][wiki]._




This section provides the absolut basics on how ***flex_extract*** is to be used. For more information about possible settings, performance, parameter combinations and so one, the user is referred to the SIP.pdf and SUT.pdf documents and the www.flexpart.eu community website. It is also possible to ask for help by writing to the ***FLEXPART*** user email list (registration needed) or by creating a ticket on the community website.

#### CONTROL file 

***flex_extract*** is controlled by providing "CONTROL"-files with a list of parameter settings. These parameter are described in detail in the *Software User Tutorial (SUT.pdf)*. 
The "CONTROL"-files specifies which ECMWF data set is to be retrieved, the time and spatial resolution, the format of the grib file and many more. In the `python` directory are some example `CONTROL` files for the different data sets and access modes which can be retrieved with ***flex_extract***:

```
CONTROL_CERA
CONTROL_CV
CONTROL_EA5.public
CONTROL_FC.pure
CONTROL_OD.highres.gauss
CONTROL_CERA.public
CONTROL_EA5
CONTROL_EI.global
CONTROL_FC.twiceaday
CONTROL_OPS.4V
CONTROL_CF
CONTROL_EA5.highres
CONTROL_EI.public
CONTROL_OD.highres.eta
CONTROL.temp
```

For information about all the possible parameter settings and explanation, please see the SUT.pdf document in the `docs/` directory.

`CONTROL`-files with a `.public` ending is usable for the public access mode. The main difference is the parameter ``dataset`` which explicitly specifies the public data sets. Additionally, not all meteorological fields and times were archived in the public data sets and are considered in the public `CONTROL`-files.

#### Python scripts 

* `submit.py`

This is the main program for doing both, retrieving ECMWF data and generating the ***FLEXPART*** input files. It combines the two sub-programs `getMARSdata.py` and `prepareFLEXPART.py` which can also be run by themselves for debugging purposes.
Use the `-h` option to get the parameter options:

```
usage: submit.py [-h] [--start_date START_DATE] [--end_date END_DATE]
                 [--date_chunk DATE_CHUNK] [--basetime BASETIME] [--step STEP]
                 [--levelist LEVELIST] [--area AREA] [--inputdir INPUTDIR]
                 [--outputdir OUTPUTDIR]
                 [--flexpart_root_scripts FLEXPART_ROOT_SCRIPTS] [--ppid PPID]
                 [--job_template JOB_TEMPLATE] [--queue QUEUE]
                 [--controlfile CONTROLFILE] [--debug DEBUG] [--public PUBLIC]

Retrieve FLEXPART input from ECMWF MARS archive

optional arguments:
  -h, --help            show this help message and exit
  --start_date START_DATE
                        start date YYYYMMDD (default: None)
  --end_date END_DATE   end_date YYYYMMDD (default: None)
  --date_chunk DATE_CHUNK
                        # of days to be retrieved at once (default: None)
  --basetime BASETIME   base such as 00/12 (for half day retrievals) (default:
                        None)
  --step STEP           steps such as 00/to/48 (default: None)
  --levelist LEVELIST   Vertical levels to be retrieved, e.g. 30/to/60
                        (default: None)
  --area AREA           area defined as north/west/south/east (default: None)
  --inputdir INPUTDIR   root directory for storing intermediate files
                        (default: None)
  --outputdir OUTPUTDIR
                        root directory for storing output files (default:
                        None)
  --flexpart_root_scripts FLEXPART_ROOT_SCRIPTS
                        FLEXPART root directory (to find grib2flexpart and
                        COMMAND file) Normally flex_extract resides in the
                        scripts directory of the FLEXPART distribution
                        (default: None)
  --ppid PPID           Specify parent process id for rerun of prepareFLEXPART
                        (default: None)
  --job_template JOB_TEMPLATE
                        job template file for submission to ECMWF (default:
                        job.temp)
  --queue QUEUE         queue for submission to ECMWF (e.g. ecgate or cca )
                        (default: None)
  --controlfile CONTROLFILE
                        file with control parameters (default: CONTROL.temp)
  --debug DEBUG         Debug mode - leave temporary files intact (default: 0)
  --public PUBLIC       Public mode - retrieves the public datasets (default:
                        0)
```

*Optional arguments are listed in squared brackets.*


* `getMARSdata.py`

This program retrieves the ECMWF data from ECMWF servers using [ECMWF WebApi](https://software.ecmwf.int/wiki/display/WEBAPI/ECMWF+Web+API+Home) or [Mars](https://software.ecmwf.int/wiki/display/UDOC/MARS+user+documentation), depending on your user status and your selection of the running mode. It requires the `ECMWF WebApi` python library (see Requirements below). Check with your local IT group as it may be already available.


* `prepareFLEXPART.py`

This program generates FLEXPART input files from the retrieved meteorological fields. It requires python interface to grib_api or eccodes and the Fortran program `CONVERT2` (located in `src` directory). `CONVERT2` needs a namelist which is generated from the python program.


#### execute flex_extract locally (member-state user)

Almost every command line parameter for the `submit.py` script call has a default value or is read from the specified `CONTROL` file. 
Therefore, for a local extraction of ERA-Interim data as a member-state user the script can be called simply by passing a `CONTROL` file and a starting date with the following command:
```
./submit.py --controlfile=CONTROL_EI.global --start_date=20101201
```
If there was just a starting date without an end date, ***flex_extract*** retrieves just this one day of meteorological data. The `CONTROL_EI.global` file has a set of default values which needs to be adjusted regarding users needs. It is also possible to set the dates within the `CONTROL`-file instead of passing it via command line parameter. 


#### execute flex_extract locally (public user)

As a public user one has to use the `CONTROL` file with the `.public` extension and the parameter `public`:
```
./submit.py --controlfile=CONTROL_EI.public --start_date=20101201 --public=1
```
Otherwise, except of the different data available, the usage of ***flex_extract*** is the same as for member-state users.

#### execute flex_extract via gateway server

If ***flex_extract*** was installed via a gateway server and a file "*ECMWF_ENV*" is available in the ``python``-directory, the ``submit.py`` script can be called with the `--queue` option. A job script is then prepared and submitted to the ECMWF server (in this case, "ecgate") .

```
./submit.py --queue=ecgate --controlfile=CONTROL_EI.global --start_date=20101201
```

The job status can then be checked by typing:
````
ecaccess-job-list
```` 

If the parameters *ecuid*, *ecgid*, *gateway* and *destination* were set correctly during installation and the gateway server is running, the resulting ***FLEXPART*** input files can be directly transferred to the local gateway by setting the paramter ``ectrans`` in the ``CONTROL``-file to ``1``.

Regardless of the job being successful or not, the user will receive an email with the log messages. 




## Development setup

install more python modules and run some tests, describe here

Describe how to install all development dependencies and how to run an automated test-suite of some kind. Potentially do this for multiple platforms.

```sh
make install
npm test
```

## Release History

* 7.1 
   * Completely revised/refactored python section
   * restructured program directories
   * simplified installation process
   * CHANGE: upgraded to Python3
   * CHANGE: applied PEP8 style guide
   * CHANGE: use of genshi templates 
   * CHANGE: modularization of python source code
   * CAHNGE: upgrade from grib_api to ecCodes
   * ADD: first UNIT tests
   * ADD: some regression tests   
   * ADD: more detailed documentation
   * ADD: local retrieval via CDS API for ERA 5 data
* 7.0.4
    * FIX: ERA 5 retrieval 
    * FIX: CERA-20C retrieval
    * FIX: in BASETIME retrieval option
    * FIX: `CONVERT2` FORTRAN program: initialise fields to 0.
    * ADD: Ensemble retrieval for ENFO and ELDA stream (ZAMG specific with extra ensembles for ELDA stream)
* 7.0.3
    * CHANGE:
    * ADD: output of mars requests to an extra file
    * ADD: CERA-20C download
    * ADD: ERA 5 download
    * ADD: public user interface with ECMWF Web API
    * ADD: use of ECMWF Web API for local retrieval version
* 7.0.2
    * Python based version
    * CHANGE: korn shell scripts were substituted by python scripts
* v0.1 - v6.0 
    * old versions which should no longer be used anymore

# SUPPORT

##### FLEXPART's community website: <http://flexpart.eu>

##### flex_extract information:  [https://www.flexpart.eu/wiki/FpInputMetEcmwf](https://www.flexpart.eu/wiki/FpInputMetEcmwf)

##### Git-repository: <https://www.flexpart.eu/browser/flex_extract.git>

##### Mailing list: [FP-dev(at)lists.univie.ac.at](mailto:fp-dev@lists.univie.ac.at)

##### Ticket system: <https://www.flexpart.eu/report/1>


If you have any problems please open a ticket at <http://flexpart.eu> or send an e-mail to: <br>
 [FP-dev(at)lists.univie.ac.at](mailto:fp-dev@lists.univie.ac.at)




# COPYRIGHT AND LICENSE
 &copy; Copyright 2014-2019.
 Anne Philipp and Leopold Haimberger 
 
<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />

 This work is licensed under the <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>. <br /> 
 To view a copy of this license, visit  http://creativecommons.org/licenses/by/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.


<!--
[npm-image]: https://img.shields.io/npm/v/datadog-metrics.svg?style=flat-square
[npm-url]: https://npmjs.org/package/datadog-metrics
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square
[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics
[wiki]: https://github.com/yourname/yourproject/wiki
-->