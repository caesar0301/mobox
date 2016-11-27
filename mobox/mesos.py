import graphsim as gs
from munkres import Munkres
import networkx as nx
import numpy as np

__all__ = ['dumps_mobgraph', 'loads_mobgraph', 'Mesos']


def dumps_mobgraph(G, node_attribute='weight', edge_attribute='weight', norm=True):
    """ Save a mobility graph to string
    """
    assert isinstance(G, nx.DiGraph)
    nw = []
    ew = []
    node_index = {}
    for node in G.nodes():
        if node not in node_index:
            node_index[node] = len(node_index)
        nw.append((node, G.node[node][node_attribute]))
    for es, et in G.edges():
        ew.append((node_index[es], node_index[et], G[es][et][edge_attribute]))

    if norm:
        nwsum = np.sum([i[1] for i in nw])
        nw = [(i[0], 1.0 * i[1] / nwsum) for i in nw]
        ewsum = np.sum([i[2] for i in ew])
        ew = [(i[0], i[1], 1.0 * i[2] / ewsum) for i in ew]

    nodestr = ';'.join(['%s,%.3f' % (str(n[0]), float(n[1])) for n in nw])
    edgestr = ';'.join(['%d,%d,%.3f' % (e[0], e[1], float(e[2])) for e in ew])
    return '%s|%s' % (nodestr, edgestr)


def loads_mobgraph(S, node_attribute='weight', edge_attribute='weight'):
    """ Load a mobility graph from a string representation
    """
    nodestr, edgestr = S.split('|')
    nodes = nodestr.split(';')
    edges = edgestr.split(';')

    node_rindex = {}
    for nid in range(0, len(nodes)):
        n, w = nodes[nid].rsplit(',', 1)
        node_rindex[nid] = (n, float(w))

    G = nx.DiGraph()
    for e in edges:
        es, et, ew = e.split(',')
        es, nsw = node_rindex[int(es)]
        et, ntw = node_rindex[int(et)]
        G.add_edge(es, et)
        G.edge[es][et][edge_attribute] = float(ew)
        G.node[es][node_attribute] = nsw
        G.node[et][node_attribute] = ntw

    return G


class Mesos(object):
    """ Extract mesostructure for two mobility graphs.
    """
    def __init__(self, G1, G2, nattr='weight', eattr='weight', lamb = 0.5):
        G1, G2 = sorted([G1, G2], key=lambda x: len(x))
        csim = gs.tacsim_combined_in_C(G1, G2, node_attribute=nattr, edge_attribute=eattr, lamb=lamb)
        self.csim = csim / np.sqrt(((csim * csim).sum())) # to ensure valid structural distance
        self.g1 = G1
        self.g2 = G2

        m = Munkres()
        cdist = (1 - self.csim).tolist()
        self.matching = m.compute(cdist)

        nmap = {}
        def _gen_nnid(node):
            if node not in nmap:
                nmap[node] = len(nmap)
            return nmap[node]

        self.mesos = nx.DiGraph()
        for (e1_idx, e2_idx) in self.matching:
            e1 = G1.edges()[e1_idx]
            e2 = G2.edges()[e2_idx]
            ns = _gen_nnid(e1[0])
            nt = _gen_nnid(e1[1])
            self.mesos.add_edge(ns, nt)
            self.mesos.edge[ns][nt][eattr] = 0.5 * (G1.edge[e1[0]][e1[1]][eattr] + G2.edge[e2[0]][e2[1]][eattr])
            self.mesos.node[ns][nattr] = 0.5 * (G1.node[e1[0]][nattr] + G2.node[e2[0]][nattr])
            self.mesos.node[nt][nattr] = 0.5 * (G1.node[e1[1]][nattr] + G2.node[e2[1]][nattr])


    def struct_dist(self, eps=1e-3):
        ''' Structutal distance defined by a mesos for two mobility graphs.
        Refer to paper Mesos.
        '''
        sims = []
        for e1, e2 in self.matching:
            sims.append(self.csim[e1][e2])
        sims = np.array(sims)
        dist = np.sqrt(1 - np.dot(sims, sims))
        return (0 if dist <= eps else dist)


if __name__ == '__main__':
    G1 = nx.DiGraph()
    G1.add_weighted_edges_from([(0,1,1), (1,0,1)])
    G1.node[0]['weight'] = 0.997
    G1.node[1]['weight'] = 0.003

    # G1 = nx.DiGraph()
    # G1.add_weighted_edges_from([(0,1,1), (1,2,1), (2,0,1)])
    # G1.node[0]['weight'] = 0.35
    # G1.node[1]['weight'] = 0.35
    # G1.node[2]['weight'] = 0.3

    mesos = Mesos(G1, G1)

    print 1-mesos.struct_dist()

