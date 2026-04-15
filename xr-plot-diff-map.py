#!/usr/bin/env python
import sys
import argparse
import glob
import re
from collections import ChainMap

import numpy      as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import xarray     as xr

import cartopy as cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import yaml
import utils as ut

xr.set_options(use_new_combine_kwarg_defaults=True)


def report(message, verb=0):
    ''' prints message if current level of verbosity is high enough '''
    if (args.verb>verb) : print(message)

# ===-----------------------------------------------------------------------===
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
    return xr.open_mfdataset(fileNames,decode_times=timeCoder)


# ===-----------------------------------------------------------------------===
def titleText(e0,e1):
    '''
    Given two dictionaries with experiment parameters, construct a
    reasonable title text describing the difference map.
    '''
    def dsTitle(ds,fallback):
        if 'title' in ds.attrs:
            return ds.title
        else:
            return fallback

    # Form the information string for the range of years.
    if e1['years'] == e0['years']:
        # comparing the same period
        ys,ye = e0['years']
        years0 = years1 = ''; yearsA = f'[{ys}:{ye}]'
    else:
        # different periods
        ys,ye = e0['years']; years0 = f'[{ys}:{ye}]'
        ys,ye = e1['years']; years1 = f'[{ys}:{ye}]'
        yearsA = ''

    # form the information string for seasons
    if e1['season'] == e0['season']:
        # comparing the same season
        season0 = season1 = ''; seasonA = f',{e0["season"]}'
    else:
        season0 = f',{e0["season"]}'
        season1 = f',{e1["season"]}'
        seasonA = ''
    t = f'{dsTitle(e1["ds"],"exp1")}{years1}{season1} - {dsTitle(e0["ds"],"exp0")}{years0}{season0} {yearsA}{seasonA}'
    return t

class ChainMap1(ChainMap):
    'Variant of ChainMap that returns None if item not present'
    def __missing__(self,key):
        return None

# ===-----------------------------------------------------------------------===
# parse command-line arguments
parser = argparse.ArgumentParser(description='plot a map of differences between two experiments')
parser.add_argument('-v','--verbose', dest='verb',
    help='increase verbosity', action='count', default=1)
parser.add_argument(
    '-s','--save', metavar='FILENAME',
    help='save plot to file (pdf, png, ...) instead of plotting it on screen.')
parser.add_argument('--dpi',
    help='resoution for saved raster figures', type=int, default=150)
parser.add_argument('file', metavar='FILENAME.yaml',
    help='plot configuration file, in yaml format',
    type=argparse.FileType('r'), default=sys.stdin)
args=parser.parse_args()

# ===-----------------------------------------------------------------------===
if args.verb > 0:
    print('using pakages:')
    for package in np,xr,yaml,mpl,cartopy:
         print('    {:>12} : {}'.format(package.__name__,package.__version__))


# ===-----------------------------------------------------------------------===
# create "environment" for plots with default and hard-coded parameters
# that can be overriden through the config file
defaults = {
    'figureWidth'  : 10.0,
    'figureHeight' : 5.0,
    'projection'   : 'PlateCarree',
    'colormap'     : 'rainbow',
    'colorbar'     : True,
    'scale'        : 1.0,
    'season'       : 'ANN'
    }
env0 = ChainMap1(defaults)

# ===-----------------------------------------------------------------------===
# read configuration file
config = yaml.safe_load(args.file)

# add configuration parameters to the environment (except 'experiments'
# array, which will be handled later)
env0 = env0.new_child({x: config[x] for x in config if x not in ['experiments']})

# print configuration, for information
if args.verb > 0:
    for item in env0:
        print(f'{item:>10} : {env0[item]}')

# check that we have two and only two data sets
if len(config['experiments']) != 2:
    die(f'Need two experiments in configuration YAML, got {len(config["experiments"])}')

# ===-----------------------------------------------------------------------===
# accumulate and process data
expList = list()
for exp in config['experiments']:
    # create new nested environment of parameters for current experiment:
    # experiment>defaults>builtin
    env = env0.new_child(exp)

    # create a dictionary to hold relevant information for plots and information lines
    expDict={}

    # load data from a set of files
    expDict['ds'] = ds = openFiles(env['files'])

    # pick the variable by name
    varName = env['var']
    if not varName:
        die('variable name not specified')
    expDict['var'] = var = ds[varName]

    # TODO: do not assume that time is the first dimension of the variable
    time = var.coords[var.dims[0]]

    # select the range of years
    if 'years' in env:
        ys,ye = ut.parseRange(env['years'])
    else:
        ys,ye = (int(time.dt.year[0]),int(time.dt.year[-1]))
    expDict['years'] = (ys,ye)
    expDict['season'] = env['season']
    months = ut.monthsInSeason(env['season'])
    var0 = var.sel(time=slice(f'{ys}-01-01',f'{ye+1}-01-01'))
    var1 = var0.where(time.dt.month.isin(months),drop=True)

    # calculate the time average
    # TODO: use appropriate month lengths for averaging
    expDict['ave'] = var1.mean(dim=time.name, keep_attrs=True, skipna=True) * env['scale']

    # form the list of the experiments
    expList.append(expDict)

diff = expList[1]['ave'] - expList[0]['ave']

# ===-----------------------------------------------------------------------===
# plotting the difference
fig = plt.figure(figsize=(env0['figureWidth'],env0['figureHeight']),
                 dpi=args.dpi)
ax  = fig.add_subplot(1, 1, 1, projection=getattr(ccrs,env0['projection'])())

# make the map global rather than have it zoom in to the extents of any plotted data
ax.set_global()
ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
             xlocs=np.linspace(-180,180,7),ylocs=np.linspace(-90,90,7),
             linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
cmap=plt.get_cmap(env['colormap'])

if 'levels' in env:
    levels = ut.parseLevels(env['levels'])
    norm   = mpl.colors.BoundaryNorm(levels, ncolors=cmap.N, extend='both')
else:
    norm = None

im = diff.plot.pcolormesh(ax=ax,
     transform=ccrs.PlateCarree(),
     cmap=cmap, norm = norm,
     shading='flat', edgecolors='none', add_colorbar=False)

ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.LAKES, edgecolor='black', facecolor='none')

if env0['colorbar'] :
    x0,y0,w,h = ax.get_position().bounds
    cax = fig.add_axes([x0+w+0.03,y0,0.015,h])
    fig.colorbar(im,cax=cax,extend='both',ticks=levels)

# set the title of the plot
title = env0['title']
if not title:
    title = titleText(expList[0],expList[1])
if title.lower() != 'none':
    ax.set_title(title,y=1.07)

# add the name, long name, and units of the variable to the plot
left = 0.0; top = 1.01
v = expList[0]['var']
ax.text(left, top, f'\n{v.name} ({v.long_name}), {v.units}',
        fontsize='small',
        horizontalalignment='left',
        verticalalignment='bottom',
        transform=ax.transAxes)

if args.save:
    report(f'Saving figure to "{args.save}"...')
    fig.savefig(args.save, transparent=True, bbox_inches='tight')
else:
    plt.show()
