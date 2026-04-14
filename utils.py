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
