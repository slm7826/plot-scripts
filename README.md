# An eclectic collection of scripts for plotting model output


To run unit tests:
```bash
python -m unittest
```

## `plot-diff-map.py`
### Structure of YAML configuration file

Some of the options can be specified either in the common section, or for each
experiments individually. If an option is set for the experiment, then it is
used to process this experiment data, otherwise the option from the common
section; if neither is set then the default is used. For example, "season" could
be DJF for the first and JJA for the second, in which case the average JJA-DJF
difference will be calculated and plotted. Another example: if "var" is "t_surf"
in the first experiment and "t_surf" in the second, then the t_ref-t_surf
difference will be calculated and plotted.

Options (case sensitive):
- title: string, optional; if absent formed automatically
- figureWidth: float, optiona, default is 10
- figureHeight: float, optiona, default is 5
- projection: string, optional, default is 'PlateCarree'; one of the global
  [cartopy projections](https://cartopy.readthedocs.io/stable/reference/projections.html)
- colormap: string, the name of a [matplotlib colormap](https://matplotlib.org/stable/users/explain/colors/colormaps.html), optional, defaults to "rainbow"
- levels: string (e.g."-2:2:0.2"), optional, but typically would be provided
- var: string, the name of the variable that must be present in each of the input files
- scale: float, default is 1.0
- units: string; if not specified units form the variable attributes are used
- season: string, default is "ANN". Can be a full name of the months, or seasons abbreviation (e.g. DJF, JJA, JSON, etc.)
- measureFile: required if the variable has "area" section in cell_measures attribute; typically one of the "static" files in the post-processin
- years: range of years (e.g. "1979:2001", inclusive), optional, defaults to the all available in input files
- experiments: required, array of two experiment/var/period,season description
   - files: Unix file mask for the experiment data, required
   - var: string, the name of the variable; variable of this name must be present in the input files
   - season: string, can be different in each experiment, e.g. to calculate JJA-DJF
   - scale: float, can be different in two experiments
   - units: string (only units from the first experiment -- or general -- are used)
   - years: range of years, optional, can be different in two experiments,
     defaults to the all available in the experiment's input files


### Examples

The examples below use here-doc feature of  Unix `bash` shell to keep
all the information in one place, but they also can use the
configuration stored in a yaml file.

Plot annual mean near-surface temperature difference between 10 years
of two experiments:
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

Difference in December temperatures:
```bash
./plot-diff-map.py -v - <<EOF
var: t_ref
levels: "-2:2:0.2"
colormap: RdBu_r
season: July
#projection: Mollweide
projection: Robinson
experiments:
  - files: "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
  - files: "/archive/slm/am5/am5f12e0r1/c96L65_am5f12e0r1_amip_noLam/gfdl.ncrc5-intel25-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
EOF
```

Example with scaling (conversion of precipitation units from kg/m2 to mm/day):
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

Same from the land data:
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

Difference between two variables
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

Plot MAM difference between two experiments:
```bash
./plot-diff-map.py -v - <<EOF
var: t_ref
levels: "-2:2:0.2"
colormap: RdBu_r
season: MAM
experiments:
  - files:    "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
  - files:    "/archive/slm/am5/am5f12e0r1/c96L65_am5f12e0r1_amip_noLam/gfdl.ncrc5-intel25-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
EOF
```

Plot JJA-DJF difference for the same experiment:
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

Plot difference between two periods, no colorbar:
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

### Examples of plotting time series

Example of plotting time series of annual total vegetation carbon amount
from two experiments, using here-doc feature of `bash` shell:
```bash
dir1="/archive/slm/lm4p2/2022/lm4p2sc-GSWP3-potveg/gfdl.ncrc3-intel18-prod/pp"
dir2="/archive/slm/lm4p2/2025/lm4p2-c96am5-potveg/gfdl.ncrc6-intel23-prod/pp"
var=cVeg

./xr-plot-annual-ts.py -v - << EOF
defaults:
  scale: 1e-12
  units: PgC
  var: $var
plots:
  - files:    "$dir1/land_cmip/ts/monthly/5yr/land_cmip.*.$var.nc"
    measures: "$dir1/land_cmip/land_cmip.static.nc"
  - files:    "$dir2/land_cmip/ts/monthly/5yr/land_cmip.*.$var.nc"
    measures: "$dir2/land_cmip/land_cmip.static.nc"
EOF
```

Plotting two different variables from the same experiment:
```bash
dir1="/archive/slm/lm4p2/2022/lm4p2sc-GSWP3-potveg/gfdl.ncrc3-intel18-prod/pp"

./xr-plot-annual-ts.py -v - << EOF
defaults:
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

Example of plotting several time series, saving plots to respective files:
```bash
dir1="/archive/slm/lm4p2/2022/lm4p2sc-GSWP3-potveg/gfdl.ncrc3-intel18-prod/pp"
dir2="/archive/slm/lm4p2/2025/lm4p2-c96am5-potveg/gfdl.ncrc6-intel23-prod/pp"

for var in cVeg cSoil cLitter cLand; do
    ./xr-plot-annual-ts.py --save ts-$var.pdf<< EOF1
defaults:
  scale: 1e-12
  units: PgC
  var: $var
plots:
  - files:    "$dir1/land_cmip/ts/monthly/5yr/land_cmip.*.$var.nc"
    measures: "$dir1/land_cmip/land_cmip.static.nc"
  - files:    "$dir2/land_cmip/ts/monthly/5yr/land_cmip.*.$var.nc"
    measures: "$dir2/land_cmip/land_cmip.static.nc"
EOF1
done
```


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
done
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