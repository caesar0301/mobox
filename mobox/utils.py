import os, zipfile, random, string
import fnmatch
import numpy as np
from datetime import datetime


__all__ = ['dayends_from_timestamp', 'in_area', 'greate_circle_distance',
           'randstr', 'zipdir', 'zippylib', 'normalized']

try:
    from matplotlib.patches import FancyArrowPatch, Circle
    __all__.append('draw_network')
except:
    print("Warnning: install `matplotlib` to use draw_network().")


def dayends_from_timestamp(ts):
    """ Determine the range of a valid day now with
    (03:00 ~ 03:00 next day)
    """
    dt = datetime.fromtimestamp(ts)
    if dt.hour < 3:
        sds = datetime(dt.year, dt.month, dt.day-1, 3)
    else:
        sds = datetime(dt.year, dt.month, dt.day, 3)
    eds = sds.replace(day=sds.day+1)
    return (sds, eds)


def in_area(p, lb, rt):
    """Check if a point (lon, lat) is in an area denoted by
    the left-below and right-top points.
    """
    if p[0] >= lb[0] and p[0] <= rt[0] and p[1] >= lb[1] and p[1] <= rt[1]:
        return True
    return False


def greate_circle_distance(lon0, lat0, lon1, lat1):
    """Return the distance (in km) between two points in
    geographical coordinates.
    """
    EARTH_R = 6372.8
    lat0 = np.radians(lat0)
    lon0 = np.radians(lon0)
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    dlon = lon0 - lon1
    y = np.sqrt(
        (np.cos(lat1) * np.sin(dlon)) ** 2
        + (np.cos(lat0) * np.sin(lat1)
           - np.sin(lat0) * np.cos(lat1) * np.cos(dlon)) ** 2)
    x = np.sin(lat0) * np.sin(lat1) + \
        np.cos(lat0) * np.cos(lat1) * np.cos(dlon)
    c = np.arctan2(y, x)
    return EARTH_R * c


def radius_of_gyration(coordinates):
    """ Calculate the radius of gyration given a list of [(lons, lats)]
    """
    clon = np.average([coord[0] for coord in coordinates])
    clat = np.average([coord[1] for coord in coordinates])

    return np.average([greate_circle_distance(clon, clat, coord[0], coord[1]) for coord in coordinates])


def zipdir(path, zipf=None, fnpat='*'):
    """
    Parameters
    ----------
    path:
        folder containing plain files to zip
    zipf:
        path to store zipped file
    fnpat:
        Unix shell-style wildcards supported by
        `fnmatch.py <https://docs.python.org/2/library/fnmatch.html>`_
    """
    if zipf is None:
        zipf = '/tmp/xoxo-' + randstr(10) + '.zip'
    elif zipf[-4:] != '.zip':
        zipf = zipf + ".zip"
    ziph = zipfile.ZipFile(zipf, 'w')
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                if fnmatch.fnmatch(file, fnpat):
                    ziph.write(os.path.join(root, file))
        return zipf
    finally:
        ziph.close()


def zippylib(libpath, zipf=None):
    """ A particular zip utility for python module.
    """
    if zipf is None:
        zipf = '/tmp/xoxo-' + randstr(10) + '.zip'
    elif zipf[-4:] != '.zip':
        zipf = zipf + ".zip"
    ziph = zipfile.PyZipFile(zipf, 'w')
    try:
        ziph.debug = 3
        ziph.writepy(libpath)
        return zipf
    finally:
        ziph.close()


def randstr(len):
    return ''.join(random.choice(string.lowercase) for i in range(len))


def normalized(a, axis=None, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / l2
