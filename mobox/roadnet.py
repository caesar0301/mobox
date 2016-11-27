import json
import numpy as np
import networkx as nx

from utils import greate_circle_distance


__all__ = ['RoadNetwork']


class RoadNetwork(object):
    """Convert an ERIS shapefile to an undirected graph weighted by distance.
    """
    def __init__(self, shapefile, edge_weighted_by_distance=True):
        g = nx.read_shp(shapefile)
        mg = max(nx.connected_component_subgraphs(g.to_undirected()), key=len)
        if edge_weighted_by_distance:
            for n0, n1 in mg.edges_iter():
                path = np.array(json.loads(mg[n0][n1]['Json'])['coordinates'])
                distance = np.sum(
                    greate_circle_distance(path[1:,0],path[1:,1], path[:-1,0], path[:-1,1])
                )
                mg.edge[n0][n1]['distance'] = distance
        self.graph = mg
        self._cache = {}
        self._cache_nn = {}

    def _hit_cache(self, lonlat1, lonlat2):
        hit = self._cache.get((lonlat1, lonlat2))
        if not hit:
            hit = self._cache.get((lonlat2, lonlat1))
        return hit

    def _update_cache(self, lonlat1, lonlat2, distance):
        self._cache.update({(lonlat1, lonlat2): distance})

    def _hit_cache_nn(self, lonlat):
        return self._cache_nn.get(lonlat)

    def _update_cache_nn(self, lonlat, nearest_node):
        self._cache_nn.update({lonlat: nearest_node})

    def nearest_node_to(self, lonlat):
        """ Find the nearest node of given point with (long, lat).
        """
        hit = self._hit_cache_nn(lonlat)
        if hit is not None:
            return hit
        nodes = np.array(self.graph.nodes())
        nn = np.argmin(np.sum((nodes[:,:] - lonlat)**2, axis=1))
        coord = self.graph.nodes()[nn]
        self._update_cache_nn(lonlat, coord)
        return coord

    def shortest_path(self, lonlat1, lonlat2, weight='distance'):
        """Find the shortest path for a pair of points.
        Two points are not required to be the vertex of graph.
        """
        p1 = self.nearest_node_to(lonlat1)
        p2 = self.nearest_node_to(lonlat2)
        path = nx.shortest_path(self.graph, p1, p2, weight)
        return path

    def shortest_path_distance(self, lonlat1, lonlat2, weight='distance'):
        """Return the distance of two points with the shortest path algorithm.
        """
        hit = self._hit_cache(lonlat1, lonlat2)
        if hit is not None:
            return hit
        p1 = self.nearest_node_to(lonlat1)
        p2 = self.nearest_node_to(lonlat2)
        distance = nx.shortest_path_length(self.graph, p1, p2, weight)
        self._update_cache(lonlat1, lonlat2, distance)
        return distance
