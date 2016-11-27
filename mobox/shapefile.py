import shapefile

__all__ = ['shape2points']


def shape2points(shpfile):
    """Extract point coordinats from a ERIS point shapefile.
    """
    sf = shapefile.Reader(shpfile)
    return [shape.points[0] for shape in sf.shapes()]

