#!/usr/bin/env python
import sys
# import optparse
import argparse
import glob
import re

import numpy      as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import xarray as xr

import yaml
from collections import ChainMap

# import plotutils

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

xr.set_options(use_new_combine_kwarg_defaults=True)

opDict = {'average':'average',
              'ave':'avearge',
              'mean':'average',
              'integral':'integral',
              'int':'integral'}

# ===-----------------------------------------------------------------===
def plot(ax,env,lineList):
    '''
    Plot a line given specified parameters

    Parameters
    ----------
    ax : matplotlib.Axis
        Axis object for plotting
    env : ChainMap
        Hierarchical collection of plot general and specific parameters
    lineList : list
        Accumulated list of line properties for construction of line label. Each
        call of this function appends an entry to this list. This entry is a dictionary
        that includes information sufficient to construct a unique line label.
    '''

    print('Parameters of plot')
    for item in env:
        print(f'{item:>10} : {env[item]}')

# TODO: avoid repeatedly reading data and measure files, if they are the same for all plots
#       check if the data set is specified in the plot spec (enc.)
    src = openFiles(env['files'])

    # get variable data
    varName = env['var']
#     report(f'Reading variable "{varName}"...')
    var  = src[varName]

    # get area associated with variable
    area = areaName(var)
    measures = openFiles(env['measures'])
    try:
        area = measures[area]
    except KeyError:
        die(f'Area variable "{area}" is not found in cell measure file(s) "{args.measures}"')

#     report(f'Calculating annual mean of variable "{var.name}"...')
    timeName = var.dims[0]
    # TODO: use annual average that takes into account different length of each month;
    #       make sure that it is generic enough for monthly and annual input data
    ann = var.groupby(f'{timeName}.year').mean(dim=timeName)

    ys,ye = coordToFloat(env['region'][0]),coordToFloat(env['region'][1])
    if ys > ye:
        ys,ye = ye,ys

    # add parameters of the line to the dictionary, for constructing of default label
    lineDict = {}
    for item in ['var','smooth','label', 'op' ]:
        if item in env:
            lineDict[item] = env[item]
    lineDict['region'] = regionStr([ys,ye])
    lineDict['exp'] = src.title
    lineDict['long_name'] = var.long_name
    if ('units' in env) :
        lineDict['units'] = env['units']
    else:
        lineDict['units'] = var.units


    ann  = ann.sel(lat=slice(ys,ye))
    area = area.sel(lat=slice(ys,ye))

#     report(f'Applying area weights "{area.name}" to "{var.name}"...')
    wgt = ann.weighted(area)

#     report(f'Calculating lat-lon integral of variable "{var.name}"...')
    if env['op'] == 'average':
        gbl = wgt.mean(dim=var.dims[1:])*float(env['scale'])
    else:
        gbl = wgt.sum(dim=var.dims[1:])*float(env['scale'])

    # set up the years for the plot
    time = src[timeName]
    d0 = time.values[0]
    d1 = time.values[-1]
    years = np.array(range(d0.year,d1.year+1))

    report(f'Plotting variable "{var.name}"...')
    if 'lineProperties' in env:
        opts = env['lineProperties']
    else:
        opts = {}

#     if 'label' in env:
#         opts['label'] = env['label']
#     else:
#         opts['label'] = f'{src.title}, {var.name}, {env["region"]}'
    if 'smooth' in env:
        box=np.ones((env['smooth'],))
        l0 = ax.plot(np.convolve(years,box,'valid')/np.sum(box),
                     np.convolve(gbl,box,'valid')/np.sum(box),
                     **opts)[0]
        ax.plot(years,gbl,c=l0.get_color(),alpha=0.33,lw=l0.get_linewidth()*0.67)
    else:
        l0 = ax.plot(years,gbl,**opts)[0]
    lineDict['line'] = l0
    lineList.append(lineDict)


# ===-----------------------------------------------------------------===
# helper functions
def die(message,code=255) :
    print ('Error :: '+message)
    exit(code)

def coordToFloat(str):
    '''
    Given a string, possibly with one of the S, N, E, or W suffixes
    return a floating point value of coordinate with appropriate sign
    '''
    if type(str) is float:
        return str
    if type(str) is int:
        return float(str)
    else:
        if str[-1] in 'nNsSeEwW' :
          str1 = str[:-1]
        else:
          str1 = str
        try:
          x=float(str1)
        except:
          die(f'cannot convert "{str}" to floating-point number')
        if str[-1] in 'sSwW' :
          x = -x
        return x


def openFiles(files):
    '''
    Given list of patterns, open files and return Xarray data set
    files: list of pattern or a single pattern
    '''
    report(f'Locating input files matching pattern(s) "{files}"')
    if type(files) is str:
        patternList = [files]
    else:
        patternList = files
    fileNames=[]
    for f in patternList:
       fileNames += sorted(glob.glob(f))

    if len(fileNames) == 0:
        die(f'Found no files that match pattern(s) "{files}"')

    if args.verb > 1:
        print('input file(s):')
        for f in fileNames:
            print(f'   "{f}"')
    report(f'Opening {len(fileNames)} input netcdf files')

    timeCoder = xr.coders.CFDatetimeCoder(use_cftime=True)
#     return xr.open_mfdataset(fileNames,decode_times=timeCoder,data_vars='minimal')
    return xr.open_mfdataset(fileNames,decode_times=timeCoder)

def areaName(var):
    '''
    Given xarray DataArray, try to find associated are in cell_measures attribute
    var: xarray DataArra
    '''

    try:
        m=re.search(r'\barea\s*:\s*(\w+)',var.cell_measures)
    except AttributeError:
        die(f'cell_measures not found in attributes of variabe "{varname}"')
    if m is None :
        die(f'"cell_measures : area" not found in attributes of variabe "{varname}"')
    return m.group(1)

def report(message, verb=0):
    ''' prints message if current level of verbosity is high enough '''
    if (args.verb>verb) : print(message)

def regionStr(region):
    def coordStr(lat):
        if lat == 0:
            return 'EQ'
        elif lat<0:
            return f'{-lat:.0f}S'
        else:
            return f'{lat:.0f}N'

    return f'{coordStr(region[0])}:{coordStr(region[1])}'

# ===-----------------------------------------------------------------===
# parse command-line arguments

"""
YAML plot configuration file may have two sections:

defaults:
    apply to all plots

plots:
    an array of parameters for each of the plots

Many parameters may exist in either defaults or individual plots parameters,
while some only make sense either in defaults or in per-plot settings

Description of parameters:
files: pattern (in terms of the Unix file name glob) describing the files
    where the data are

measures: pattern of the file(s) containing the area associated with the
    variable; typically a "static" file

var: name of the variable to plot

scale: scaling factor applied to the variable before plotting

units: Units of the variable (after scale is applied)

region: latitudinal region to plot, array. Example: [30S, 30N]

label: label of the line, if different from the default

lineProperties: dictionary of the matplotlib properties of the line(s)

op: aggregation operation in horizontal dimensions, one of ...

smooth: number of years to smooth data over

title: title of the entire plot

figureWidth, figureHeight: dimensions of the figure

Example:
----
defaults:
  scale: 0.000031536
  units: PgC/year
  var: fFire
  smooth: 20
plots:
  - files:    "/archive/slm/lm4p2/2022/lm4p2sc-GSWP3-potveg/gfdl.ncrc3-intel18-prod/pp/land_cmip/ts/monthly/5yr/land_cmip.*.fFire.nc"
    measures: "/archive/slm/lm4p2/2022/lm4p2sc-GSWP3-potveg/gfdl.ncrc3-intel18-prod/pp/land/land.static.nc"
  - files:    "/archive/slm/lm4p2/2025/lm4p2-c96am5-potveg/gfdl.ncrc6-intel23-prod/pp/land_cmip/ts/monthly/5yr/land_cmip.*.fFire.nc"
    measures: "/archive/slm/lm4p2/2025/lm4p2-c96am5-potveg/gfdl.ncrc6-intel23-prod/pp_1/land/land.static.nc"
----
"""

parser = argparse.ArgumentParser(description='plot something')
parser.add_argument('--verbose', dest='verb',
    help='increase verbosity', action='count', default=1)
parser.add_argument(
    '-f','--file', metavar='FILENAME.yaml',
    help='plot configuration file, in YAML')
parser.add_argument(
    '-s','--save', metavar='FILENAME',
    help='save figure instead of plotting it on screen.')
args=parser.parse_args()


# ===-----------------------------------------------------------------===
# read configuration file
if args.file:
    f = open(args.file, 'r')
else:
    f = sys.stdin
config = yaml.safe_load(f)

# ===-----------------------------------------------------------------===
# create "environment" for plots with default and hard-coded parameters
hardcoded = {
    'op':'integral',
    'region':[-90,90],
    'scale':1.0,
    'figureWidth':10.0, 'figureHeight':5.0
    }
env0 = ChainMap(config['defaults'],hardcoded)
# for item in env0:
#     print(f'{item:>10} : {env0[item]}')

fig,ax = plt.subplots(1,1,facecolor='w',
    figsize=(float(env0['figureWidth']),float(env0['figureHeight'])))

lineList = []
for pars in config['plots'] :
    env = env0.new_child(pars)
    plot(ax,env,lineList)

# Construct default labels
print(lineList)
# find the information that needs to go in line label
titleKeys = []; labelKeys=[]
for key in lineList[0].keys():
    if key == 'line': continue
    s = {l[key] for l in lineList}
    if len(s) > 1:
        labelKeys.append(key)
    else:
        titleKeys.append(key)
    print(f' {key:>10} : {len(s):2d} : {s} ')

print(f'titleKeys : {titleKeys}')
print(f'labelKeys : {labelKeys}')

def titleString(keys,env0,env):
    if 'title' in env0:
        return env0['title']
    else:
        s = []
        if 'region' in keys: s.append(env['region'])
        if 'op'     in keys: s.append(env['op'])
        if 'var'    in keys: s.append(f'of {env["var"]}')
        if 'smooth' in keys: s.append(f'smoothed over {env["smooth"]} years')
        if 'exp'    in keys: s.append(env['exp'])
        if 'long_name' in keys: s.append(f'({env["long_name"]})')
        return ' '.join(s)

def unitString(keys,env0,env):
    if 'units' in env0:
        return env0['units']
    elif 'units' in keys:
        return env['units']
    else:
        return ''

def labelString(keys,env):
    if 'label' in env:
        return env['label']
    else:
        s = []
        if 'exp'    in keys: s.append(env['exp'])
        if 'region' in keys: s.append(env['region'])
#         if 'op'     in keys: s.append(env['op'])
        if 'var'    in keys: s.append(f'of {env["var"]}')
        return ' '.join(s)

for line in lineList:
    print(line)
    line['line'].set_label(labelString(labelKeys,line))

ax.grid(True)
ax.legend(loc='best')
ax.set_ylabel(unitString(titleKeys,env0,lineList[0]))
ax.set_xlabel('year')

print(titleString(titleKeys,env0,lineList[0]))
ax.set_title(titleString(titleKeys,env0,lineList[0]))


if args.save:
    report(f'Saving figure to "{args.save}"...')
    fig.savefig(args.save, transparent=True, bbox_inches='tight')
else:
    plt.show()
