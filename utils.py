import re
import numpy as np

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
def monthsInSeason(seasonName):
    '''
    Given the symbolic name of a season, return the list of (1-based)
    months numbers that belong to this season. Season name can be
    'ANNUAL', 'ANN', or a string of contiguous months initials, e.g.
    'DJF', 'JAS', 'SO', 'JJAS'. Season names are case insensitive;
    spaces are ignored.

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

    month_initials = 'JFMAMJJASOND'
    doubled = month_initials * 2
    start = doubled.find(key)

    if start == -1 or start >= 12:
        raise ValueError(
            f"Unsupported season selector '{seasonName}'. Use 'annual' or contiguous month initials like 'SO', 'JAS', 'DJF'."
        )
    return [(start + i) % 12 + 1 for i in range(len(key))]
