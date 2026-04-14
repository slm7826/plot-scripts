# An eclectic collection of scripts for plotting model output

Example of plotting annual mean near-surface temperature difference between 10 years
of two experiments, using here-doc feature of `bash` shell:
```bash
./xr-plot-diff-map.py -v - <<EOF
var: t_ref
levels: "-2:2:0.2"
colormap: RdBu_r
colorbar: true
experiments:
  - files:    "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
  - files:    "/archive/slm/am5/am5f12e0r1/c96L65_am5f12e0r1_amip_noLam/gfdl.ncrc5-intel25-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
EOF
```

Difference between two periods
```bash
./xr-plot-diff-map.py -v - <<EOF
var: t_ref
levels: "-2:2:0.2"
colormap: RdBu_r
colorbar: true
experiments:
  - files:    "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
    years:    "2008:2009"
  - files:    "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
    years:    "2000:2002"
EOF
```
Or equivalently:
```bash
./xr-plot-diff-map.py -v - <<EOF
var: t_ref
levels: "-2:2:0.2"
colormap: RdBu_r
colorbar: true
files: "/archive/oar.gfdl.am5/am5/am5f12e0r1/c96L65_am5f12e0r1_amip/gfdl.ncrc5-deploy-prod-openmp/pp/atmos/ts/monthly/1yr/atmos.200*.t_ref.nc"
experiments:
  - years:    "2008:2009"
  - years:    "2000:2002"
EOF
```

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
