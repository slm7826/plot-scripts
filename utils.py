import re
import numpy as np
import xarray as xr

# ===-----------------------------------------------------------------------===
def parseLevels(s):
    '''
    Given a string in the form "0:1:0.1,-10:10:1,0.25,-0.25,del(0)”, returns
    a tuple of three values: (sorted level values, minimum, and maximum).
    Note that the input string is processed left-to-right, so the effect
    of del() may depend on its location in the input string.
    '''
    s1 = re.sub(r'\s+','',s) # remove all spaces
    l=re.split(r',',s1)
    lev=set()
    for p in l:
        m = re.match(r'del\(([^)]+)\)',p)
        if m:
            lev.discard(float(m.group(1)))
        else:
            e = re.split(r':',p)
            if len(e) == 1 :
                lev.add(float(e[0]))
            else:
                if len(e) != 3:
                    raise ValueError(f'Level spec must have three numbers, got {len(e)} in "{p}"')
                start = float(e[0])
                stop  = float(e[1])
                step  = float(e[2])
                if start >= stop:
                    raise ValueError(f'Start of levels must be smaller than stop in "{p}"')
                if step <= 0:
                    raise ValueError(f'Step of levels must be greater tha zero in "{p}"')
                for f in np.arange(start,stop,step):
                    lev.add(round(f,6))
                lev.add(float(e[1]))
    if len(lev) < 2:
        raise ValueError(f'Level spec must result in 2 or more layers, got {len(lev)} from "{s}"')
    return sorted(list(lev))


# ===-----------------------------------------------------------------------===
def parseRange(r):
    '''
    Given input string in the form "YYYY:YYYY", returns a tuple of integers
    '''
    r1 = re.sub(r'\s+','',r) # remove all white space
    m  = re.fullmatch(r'(\d+):(\d+)',r1)
    if not m:
        raise ValueError(f'argument of parseRange must be a string in form "YYYY:YYYY", got "{r}"')
    start,stop=int(m.group(1)),int(m.group(2))
    if start>stop:
        start,stop=stop,start
    return (start,stop)


# ===-----------------------------------------------------------------------===
def getBounds(ds,coordName):
    '''
    Given an xarray data set and the name of a coordinate, returns an array of bound
    for this coordinate variable.

    The bounds are taken from the coordinate variable attributes, or
    computed if not available.
    '''
    coord = ds[coordName]
    # check that coordinate is 1D
    if len(coord.shape) != 1:
        raise ValueError('Coordinate "{coordName}" has {len(coord.shape)} dimensions, must be one-dimensional')

    if 'bounds' in coord.attrs:
        bounds = ds[coord.bounds]
        if len(bounds.shape) != 2:
            raise ValueError('Variable "{coordName}" attribute "bounds" points to variable "{bounds.name}" whose number of dimensions is not 2')
        if bounds.shape[-1] != 2:
            raise ValueError('variable "{coordName}" attribute "bounds" points to variable "{bounds.name}" whose second dimension length is not 2')
        return bounds
    # TODO: handle "edges" attribute that ferret adds to its data sets
    else:
        # calculate bounds from coordinates
        varlen = coord.shape[0]
        # TODO: handle time coordinate here: data type should be inherited from the coordinate. Can it be cftime?
        bnds = np.zeros((varlen,2))
        bnds[1:, 0] = (coord.values[0:-1]+coord.values[1:])/2.0
        bnds[:-1,1] = bnds[1:, 0]
        bnds[0,  0] = 2*coord[0]-bnds[1,0]
        bnds[-1, 1] = 2*coord[-1]-bnds[-1,0]
        return xr.DataArray(bnds, {coordName:coord, 'bnds':[1,2]})


# ===-----------------------------------------------------------------------===
def monthsInSeason(seasonName):
    '''
    Given the symbolic name of a season, return the list of (1-based) months
    numbers that belong to this season. Season name can be 'ANNUAL', 'ANN', or a
    string of contiguous months initials, e.g. 'DJF', 'JAS', 'SO', 'JJAS', or a
    month name, e.g 'APR' or April. Season names are case insensitive; spaces are
    ignored.

    After Fabien's idea and implementation.

    Note that to be useful in xarray "isin" selector, the argument must
    be array-like: this is why we return a list, and not a more efficient
    set.
    '''
    if not isinstance(seasonName, str):
        raise ValueError(f"seasonName must be a string, got {type(seasonName)}")

    key = re.sub(r'\s+','',seasonName).upper() # remove all white space and convert to upper case
    if len(key) < 2:
        raise ValueError(
            f"Unsupported season selector '{seasonName}'. Use 'annual' or contiguous month initials like 'SO', 'JAS', 'DJF'."
        )

    if key in {'ANNUAL','ANN'}:
        return list(range(1,13))

    monthNames = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    if key in monthNames:
        return [monthNames.index(key) + 1]

    monthNames = ['JANUARY','FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
                  'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
    if key in monthNames:
        return [monthNames.index(key) + 1]

    month_initials = 'JFMAMJJASOND'
    doubled = month_initials * 2
    start = doubled.find(key)

    if start == -1 or start >= 12:
        raise ValueError(
            f"Unsupported season selector '{seasonName}'. Use 'annual' or contiguous month initials like 'SO', 'JAS', 'DJF'."
        )
    return [(start + i) % 12 + 1 for i in range(len(key))]
