# An eclectic collection of scripts for plotting model output


To run unit tests:
```bash
python -m unittest
```

## `plot-diff-map.py` --- plotting seasonal or annual differences.

This script allows to plot a map of differences: between two experiments, or
between two periods of the same run, or between different seasons, or between
different varuables. The input data and the parameters of the plot are specified
in the input YAML file, except few settings such as verbosity level or
destination of the plot.

```bash
usage: plot-diff-map.py [-h] [-v] [-s FILENAME] [--dpi DPI] FILENAME.yaml

plot a map of differences between two experiments

positional arguments:
  FILENAME.yaml         plot configuration file, in yaml format

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase verbosity
  -s FILENAME, --save FILENAME
                        save plot to file (pdf, png, ...) instead of plotting it on screen.
  --dpi DPI             resolution for saved raster figures
```

For example:
```bash
plot-diff-map.py --save=diff.png diff.yaml
```
where the contents of `diff.yaml` is:
```yaml
var: t_ref
levels: "-2:2:0.2, del(0)"
colormap: RdBu_r
experiments:
  - files: "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
  - files: "/archive/slm/am5/am5f12e0r1/c96L65_am5f12e0r1_amip_noLam/gfdl.ncrc5-intel25-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
```
### Structure of YAML configuration file

Some of the options can be specified either in the common section, or for each
of the experiments individually. If an option is set for the specific experiment (e.g.
`scale` of the variable), then it is used to process this experiment data,
otherwise the option from the common section is used; if neither is set then the default
is used. For example, `season` could be `DJF` for the first and `JJA` for the
second experiment, in which case the average JJA-DJF difference will be calculated and
plotted. Another example: if "var" is "t_surf" in the first experiment and
"t_ref" in the second, then the t_ref-t_surf difference will be calculated and
plotted.

Configuration options (case sensitive):
- title: string, optional; if absent formed automatically
- figureWidth: float, optiona, default is 10
- figureHeight: float, optiona, default is 5
- projection: string, optional, default is 'PlateCarree'; one of the global
  [cartopy projections](https://cartopy.readthedocs.io/stable/reference/projections.html)
- colormap: string, the name of a [matplotlib colormap](https://matplotlib.org/stable/users/explain/colors/colormaps.html), optional, defaults to "rainbow"
- levels: string (e.g."-2:2:0.2, del(0)"), optional, but typically should be provided
- var: string, the name of the variable to plot; naturally the variable of that name must be present in each of the input files
- scale: float, default is 1.0
- units: string; if not specified units form the variable attributes are used
- season: string, default is "ANNUAL". Can be a full name of a month, or abbreviated season name, e.g. DJF, JJA, JSON, etc.
- measureFile: required if the variable has "area" section in cell_measures attribute; typically one of the "static" files in the post-processin
- years: range of years (e.g. "1979:2001", inclusive), optional, defaults to the all available in input files
- experiments: required, array of two experiment/var/period/season descriptions
   - files: Unix file mask for the experiment data, required
   - var: string, the name of the variable; variable of this name must be present in the input files
   - season: string, can be different in each experiment, e.g. to calculate JJA-DJF
   - scale: float, can be different in two experiments
   - units: string (only units from the first experiment -- or general section -- are used)
   - years: range of years, optional, can be different in two experiments,
     defaults to the all years available in the experiment's input files


### Examples of `plot-diff-map.py` usage

The examples below use here-doc feature of  Unix `bash` shell to keep all the
information in one place, but they also can use the configuration stored in a
yaml file, as shown above.

#### Annual mean near-surface temperature difference between 10 years of two experiments:
```bash
./plot-diff-map.py -v - <<EOF
var: t_ref
levels: "-2:2:0.2, del(0)"
colormap: RdBu_r
experiments:
  - files: "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
  - files: "/archive/slm/am5/am5f12e0r1/c96L65_am5f12e0r1_amip_noLam/gfdl.ncrc5-intel25-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
EOF
```

#### Difference of July temperatures:
```bash
./plot-diff-map.py -v - <<EOF
var: t_ref
levels: "-2:2:0.2"
colormap: RdBu_r
season: July
projection: Robinson
experiments:
  - files: "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
  - files: "/archive/slm/am5/am5f12e0r1/c96L65_am5f12e0r1_amip_noLam/gfdl.ncrc5-intel25-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
EOF
```

#### Same from the land output

Land data have area variable specified in the `cell_measure` attribute of the
variables, and therefore the script uses it for calculating spatial statistics):
```bash
./plot-diff-map.py -v - <<EOF
var: t_ref
levels: "-2:2:0.2"
colormap: RdBu_r
measureFile: /archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/land/land.static.nc
experiments:
  - files: "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/land/ts/monthly/1yr/land.200*.t_ref.nc"
  - files: "/archive/slm/am5/am5f12e0r1/c96L65_am5f12e0r1_amip_noLam/gfdl.ncrc5-intel25-prod-openmp/pp/land/ts/monthly/1yr/land.200*.t_ref.nc"
EOF
```

#### Scaling: conversion of precipitation units from kg/(m2 s) to mm/day
```bash
./plot-diff-map.py -v - <<EOF
var: precip
scale: 86400
units: "mm/day"
levels: "-2:2:0.2"
colormap: RdBu
experiments:
  - files: "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.precip.nc"
  - files: "/archive/slm/am5/am5f12e0r1/c96L65_am5f12e0r1_amip_noLam/gfdl.ncrc5-intel25-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.precip.nc"
EOF
```

#### Difference between two variables
```bash
./plot-diff-map.py -v - <<EOF
levels: "-2:2:0.2"
colormap: RdBu_r
experiments:
  - files: "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_surf.nc"
    var: t_surf
  - files: "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
    var: t_ref
EOF
```

#### JJAS seasonal difference between two experiments
```bash
./plot-diff-map.py -v - <<EOF
var: t_ref
levels: "-2:2:0.2"
colormap: RdBu_r
season: JJAS
experiments:
  - files:    "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
  - files:    "/archive/slm/am5/am5f12e0r1/c96L65_am5f12e0r1_amip_noLam/gfdl.ncrc5-intel25-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
EOF
```

#### JJA-DJF difference for the same experiment
```bash
./plot-diff-map.py -v - <<EOF
var: t_ref
levels: "-50:50:5"
colormap: RdBu_r
files: "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
experiments:
  - season: DJF
  - season: JJA
EOF
```

#### Difference between two periods

This example also shows how to disable colorbar
```bash
./plot-diff-map.py -v - <<EOF
var: t_ref
levels: "-2:2:0.2"
colormap: RdBu_r
colorbar: No
files:    "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
experiments:
    - years:    "2008:2009"
    - years:    "2000:2002"
EOF
```

## `xr-plot-annual-ts.py` --- plot time series of annual-mean values

This script allows to plot time series of annual mean values (average or total
global) for a number of experiments, or for several variables, or for several
regions, on the same plot.

```bash
usage: xr-plot-annual-ts.py [-h] [-v] [-s FILENAME] FILENAME.yaml

plot something

positional arguments:
  FILENAME.yaml         plot configuration file, in yaml format

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase verbosity
  -s FILENAME, --save FILENAME
                        save plot to file (pdf, png, ...) instead of plotting it on screen.
```

The script expects to find the configuration of plots in the input YAML file, but it can
also come from stdin, as shown in examples below using here-doc feature of
`bash`; it should work in other shells too, perhaps with appropriate
modifications.

### Structure of YAML configuration file

Some of the options can be specified either in the common section, or for each
plot individually. If an option is set for the specific plot (e.g.
name of the variable), then it is used to process this experiment data,
otherwise the option from the common section is used; if neither is set then the
default is used.

Many parameters may exist in either defaults or individual plots parameters,
while some only make sense either in defaults or in per-plot settings

Description of parameters:
- files: pattern (in terms of the Unix file name glob) describing the files where the data are
- measures: pattern of the file(s) containing the area associated with the variable; typically a "static" file
- var: name of the variable to plot
- scale: scaling factor applied to the variable before plotting
- units: Units of the variable (after scale is applied)
- region: latitudinal region to plot, array. Example: [30S, 30N]
- label: label of the line, if different from the default
- lineProperties: dictionary of the [matplotlib properties](https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D) of the line(s)
- op: aggregation operation in horizontal dimensions, one of ...
- smooth: number of years to smooth data over
- title: title of the entire plot
- figureWidth, figureHeight: dimensions of the figure

### Examples of plotting time series

#### Plot two time series

Plot time series of annual total vegetation carbon amount
from two experiments, using here-doc feature of `bash` shell:
```bash
dir1="/archive/slm/lm4p2/2022/lm4p2sc-GSWP3-potveg/gfdl.ncrc3-intel18-prod/pp"
dir2="/archive/slm/lm4p2/2025/lm4p2-c96am5-potveg/gfdl.ncrc6-intel23-prod/pp"
var=cVeg

./xr-plot-annual-ts.py -v - << EOF
scale: 1e-12
units: PgC
var: $var
plots:
  - files:    "$dir1/land_cmip/ts/monthly/5yr/land_cmip.00*.$var.nc"
    measures: "$dir1/land_cmip/land_cmip.static.nc"
  - files:    "$dir2/land_cmip/ts/monthly/5yr/land_cmip.00*.$var.nc"
    measures: "$dir2/land_cmip/land_cmip.static.nc"
    lineProperties:
        ls: "--"
        color: black
        linewidth: 2.5
EOF
```

#### Plotting two different variables from the same experiment:
```bash
dir1="/archive/slm/lm4p2/2022/lm4p2sc-GSWP3-potveg/gfdl.ncrc3-intel18-prod/pp"

./xr-plot-annual-ts.py -v - << EOF
scale: 1e-12
units: PgC
measures: "$dir1/land_cmip/land_cmip.static.nc"
plots:
  - files:    "$dir1/land_cmip/ts/monthly/5yr/land_cmip.*.cSoil.nc"
    var: cSoil
  - files:    "$dir1/land_cmip/ts/monthly/5yr/land_cmip.*.cVeg.nc"
    var: cVeg
EOF
```

### Plot several time series in a loop

Example of plotting several time series in a loop, saving plots to respective
files. This is written in `bash`, so users of `c-shell` must modify it
accordingly.
```bash
dir1="/archive/slm/lm4p2/2022/lm4p2sc-GSWP3-potveg/gfdl.ncrc3-intel18-prod/pp"
dir2="/archive/slm/lm4p2/2025/lm4p2-c96am5-potveg/gfdl.ncrc6-intel23-prod/pp"

for var in cVeg cSoil cLitter cLand; do
    ./xr-plot-annual-ts.py --save ts-$var.pdf - << EOF
scale: 1e-12
units: PgC
var: $var
plots:
  - files:    "$dir1/land_cmip/ts/monthly/5yr/land_cmip.*.$var.nc"
    measures: "$dir1/land_cmip/land_cmip.static.nc"
  - files:    "$dir2/land_cmip/ts/monthly/5yr/land_cmip.*.$var.nc"
    measures: "$dir2/land_cmip/land_cmip.static.nc"
EOF
done
```

These example do not work because static file is broken

```bash
dir1="/archive/ens/CMIP7/ESM4/DECK/ESM4.5-landbridge-esm/gfdl.ncrc6-intel25-prod-openmp/pp"
dir2="/archive/ens/CMIP7/ESM4/DECK/ESM4.5-landbridge-newsun/gfdl.ncrc6-intel25-prod-openmp/pp"

var=btot
./xr-plot-annual-ts.py - << EOF
defaults:
  scale: 1e-12
  units: PgC
  var: $var
plots:
  - files:    "$dir1/land/ts/monthly/5yr/*.$var.nc"
    measures: "$dir2/land/land.static.nc"
  - files:    "$dir2/land/ts/monthly/5yr/*.$var.nc"
    measures: "$dir2/land/land.static.nc"
EOF
```

```bash
./xr-plot-annual-ts.py - << EOF
defaults:
  scale: 1e-12
  units: PgC
  var: btot
plots:
  - files:    "/archive/ens/CMIP7/ESM4/DECK/ESM4.5-landbridge-newsun/gfdl.ncrc6-intel25-prod-openmp/pp/land/ts/monthly/5yr/*.btot.nc"
    measures: "/archive/ens/CMIP7/ESM4/DECK/ESM4.5-landbridge-newsun/gfdl.ncrc6-intel25-prod-openmp/pp/land/land.static.nc"
EOF
```

Old script that does not work any more:
```
ppDir=/archive/ens/CMIP7/ESM4/DECK/ESM4.5-landbridge-esm/gfdl.ncrc6-intel25-prod-openmp/pp
var=cLand
~/bin/plot/plot-annual-ts.py --verb --var=$var --scale=1e-12 --units=PgC \
   --measures "$ppDir/land/land.static.nc" \
   --exp "$ppDir/land/ts/monthly/5yr/*.Ctot.nc"
```

Error message:
```
  File "/home/Sergey.Malyshev/bin/plot/plot-annual-ts.py", line 172, in <module>
    src=nc.MFDataset(files,master_file=files[-1])
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "src/netCDF4/_netCDF4.pyx", line 7044, in netCDF4._netCDF4.MFDataset.__init__
ValueError: MFNetCDF4 only works with NETCDF3_* and NETCDF4_CLASSIC formatted files, not NETCDF4
```