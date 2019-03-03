# Make Tree --->

from collections import defaultdict
from .compilation import get_relation
from . import global_variables as gv

# Make thresholded graph


def make_graph(edge_list, threshold=0.0, max_connections=10):
    """Return 2 way graph from edge_list based on threshold"""
    graph = defaultdict(list)
    edge_list.sort(reverse=True, key=lambda x: x[1])
    for nodes, weight in edge_list:
        a, b = nodes
        if weight > threshold:
            if len(graph[a]) < max_connections:
                graph[a].append(gv.connection(b, weight))
            if len(graph[b]) < max_connections:
                graph[b].append(gv.connection(a, weight))
    print(f'Total graph nodes considered       : {len(graph.keys())}')
    print(f'Total graph connections considered : {sum(map(len, graph.values()))}')
    return graph


# Tree Generation Algorithm - Key Pipeline Function
def make_tree(graph):
    """
    Prepares a tree object from a graph based on edge strength. Determines the central node on its own.

    Keyword:
    graph -- A graph object(dict) containing list of connections as its value. E.g.
    { sapcy.token:node : [connection(node={spacy.token:node1}, weight={float:value}),..], ... }
    """
    tree = defaultdict(list)
    available = set(graph.keys())
    active = set()
    leaves = set()

    def _make_edge(parent, child, weight):
        child.set_extension('edge_strength', default=None, force=True)
        child._.edge_strength = weight
        child.set_extension('relation_to_parent', default=None, force=True)
        child._.relation_to_parent = get_relation(parent, child)[1]
        tree[parent].append(child)

    def get_max_from_available():
        return max(available, key=lambda x: x._.frequency)

    def get_max_from_active():
        return max(active, key=lambda x: graph[x][0].weight)

    root = get_max_from_available()
    available.remove(root)
    active.add(root)
    while(available):

        parent = get_max_from_active() if active else get_max_from_available()
        active.discard(parent)

        if not graph[parent]:
            leaves.add(parent)
            available.remove(parent)
            continue

        child, weight = graph[parent].pop(0)

        if child in available or child in leaves:  # danger
            _make_edge(parent, child, weight)
            available.remove(child)

            if graph[child]:
                active.add(child)

        if graph[parent]:
            active.add(parent)

    return tree, root

# Dict object to Standard Dict - Key Pipeline Function


def make_a_node_dict(node):
    node_dict = {}
    node_dict["title"] = node.text
    node_dict["i"] = node.sent.start_char  # MD-TPM 5.0
    node_dict["j"] = node.sent.end_char    # MD-TPM 5.0
    node_dict["relation_to_parent"] = node._.relation_to_parent  # MD-TPM 6.0
    node_dict["relation_strength"] = node._.edge_strength
    node_dict['is_central'] = node.text == gv.ROOT.text
    node_dict["children"] = [ele for ele in map(make_a_node_dict, gv.TREE[node])]
    return node_dict
