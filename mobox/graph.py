import networkx as nx

__all__ = ['seq2graph', 'draw_curved_graph', 'dumps_mobgraph', 'loads_mobgraph']


def seq2graph(seq, directed=True):
    """Create a directed graph from an odered
    sequence of items.

    An alternative to nx.Graph.add_path().
    """
    seq = [i for i in seq]
    N = len(seq)
    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
    G.add_nodes_from(seq)
    edges = [i for i in zip(seq[0:N-1], seq[1:N]) if i[0] != i[1]]
    G.add_edges_from(edges)
    return G


def draw_curved_graph(G, pos, ax):
    """Draw network with curved edges.

    Examples
    --------

    plt.figure(figsize=(10, 10))
    ax=plt.gca()
    pos=nx.spring_layout(G)
    draw_curved_graph(G, pos, ax)
    ax.autoscale()
    plt.axis('equal')
    plt.axis('off')
    plt.title('Curved network')

    """
    # import matplotlib.pyplot as plt

    for n in G:
        c = Circle(pos[n], radius=0.05, alpha=0.5)
        ax.add_patch(c)
        G.node[n]['patch'] = c
    seen={}
    for (u,v,d) in G.edges(data=True):
        n1 = G.node[u]['patch']
        n2 = G.node[v]['patch']
        rad = 0.1
        if (u,v) in seen:
            rad = seen.get((u,v))
            rad = (rad + np.sign(rad) * 0.1) * -1
        alpha = 0.5; color = 'k'
        e = FancyArrowPatch(n1.center, n2.center,
                            patchA=n1, patchB=n2,
                            arrowstyle='-|>',
                            connectionstyle='arc3,rad=%s' % rad,
                            mutation_scale=10.0,
                            lw=2, alpha=alpha, color=color)
        seen[(u, v)] = rad
        ax.add_patch(e)

    # ax.autoscale()
    # plt.axis('equal')
    # plt.axis('off')

    return e


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

