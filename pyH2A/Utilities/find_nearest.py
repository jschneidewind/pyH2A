import numpy as np
import math as math

def find_nearest(array, values):
    '''Find value(s) in `array` that are nearest to `values`.

    Parameters
    ----------
    array: ndarray
        Array to be searched. If `array` has more than one dimension, only
        the first column is used.
    values : float, ndarray or list
        Single float, ndarray or list with values for which the nearest entries
        in `array` should be found.

    Returns
    -------
    hits : list
        List of indices of closest values in `array`.
    '''
    
    if array.ndim != 1:
        array_1d = array[:,0]
    else:
        array_1d = array

    values = np.atleast_1d(values)
    hits = []

    for i in range(len(values)):

        idx = np.searchsorted(array_1d, values[i], side= "left")
        if idx > 0 and (idx == len(array_1d) or math.fabs(values[i] - array_1d[idx-1]) < math.fabs(values[i] - array_1d[idx])):
            hits.append(idx-1)
        else:
            hits.append(idx)

    return hits