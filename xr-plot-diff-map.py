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

xr.set_options(use_new_combine_kwarg_defaults=True)


def report(message, verb=0):
    ''' prints message if current level of verbosity is high enough '''
    if (args.verb>verb) : print(message)

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

def parse_levels(s):
    '''
    Given a string in form "0:1:0.1,-10:10:1,0.25,-0.25,del(0)" returns a list of
    level values
    '''
    if not s:
        return (None,None,None)
    l=re.split(r'\s*,\s*',s)
    lev=set()
    for e in l:
        m = re.match(r'\s*del\s*\(([^)]+)\)',e)
        if m:
            lev.discard(float(m.group(1)))
        else:
            e = re.split(r'\s*:\s*',e)
            if len(e) == 1 :
                lev.add(float(e[0]))
            else:
                for f in np.arange(float(e[0]),float(e[1]),float(e[2])):
                    lev.add(round(f,6))
                lev.add(float(e[1]))
    return (sorted(list(lev)),min(lev),max(lev))

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
# read configuration file
config = yaml.safe_load(args.file)

# ===-----------------------------------------------------------------------===
# create "environment" for plots with default and hard-coded parameters
# that can be overriden through the config file
hardcoded = {
    'figureWidth'  : 10.0,
    'figureHeight' : 5.0,
    'projection'   : 'PlateCarree',
    'colormap'     : 'rainbow',
    'scale'        : 1.0,
    }
env0 = ChainMap1(config['defaults'],hardcoded)
for item in env0:
    print(f'{item:>10} : {env0[item]}')

# ===-----------------------------------------------------------------------===
# accumulate and process data
maps = list(); dsets = list()
for pars in config['experiments']:
    env = env0.new_child(pars)
    # load file data
    src = openFiles(env['files'])
    print('###### dataset:\n',src)
    print(src)
    # do the averaging
    varName = env['var']
    var = src[varName]
    print('###### variable:\n',var)
    ave = var.mean(dim=var.dims[0],keep_attrs=True) # assuming the first dimension is time
    print('###### average:\n',ave)
    dsets.append(src)
    maps.append(ave)

# TODO: check that we have two and only two data sets
diff = (maps[1]-maps[0])*env0['scale']

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

levels,vmin,vmax=parse_levels(env['levels'])
if levels:
    norm = mpl.colors.BoundaryNorm(levels, ncolors=cmap.N, extend='both')
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
#     title = '{} - {},  years {:04d}-{:04d}'.format(
#           dsets[1].title, dsets[0].title, years[0],years[1])
    title = f'{dsets[1].title} - {dsets[0].title}'
if title.lower() != 'none':
    ax.set_title(title,y=1.07)

# add the name, long name, and units of the variable to the plot
left = 0.0; top = 1.01
v = maps[0]
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
