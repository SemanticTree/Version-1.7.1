from .global_variables import *


# Transform StandardDict form to cytoscape form - Key Pipeline Function
def transform_data(data):
    """Accepts a data dictionary of standard format {Heirarchial format} and returns a
    format suitable for cytoscape.js"""
    new_dict = {'elements': []}
    elements = new_dict['elements']
    children, title = 'children', 'title'
    # r_st, rtp = 'relation_strength', 'relation_to_parent'

    def get_id():
        i = 1
        while True:
            yield 'edge' + str(i)
            i += 1

    id_generator = get_id()

    def add_node(node):
        elements.append({
            'data': {
                'id': node[title],
                'title': node[title],
                'has_child': node[children] == [],
                'i': node["i"],
                'j': node["j"],
                'is_central': node['is_central'],
            }
        })
        if node[children]:
            for a in node[children]:
                add_node(a)

        return

    def add_edge(node, parent):
        if node['relation_to_parent'] is not '-':
            if parent is not '-':
                elements.append({
                    'data': {
                        'id': next(id_generator),
                        'source': parent,
                        'target': node[title],
                        'title': node['relation_to_parent'],
                        'weight': node['relation_strength'],
                    }
                })
        if node[children]:
            for a in node[children]:
                add_edge(a, node[title])

        return

    new_dict = {'elements': []}
    elements = new_dict['elements']
    id_generator = get_id()
    add_node(data)
    add_edge(data, '-')
    return new_dict


def print_param(p):
    print("*" * 40)
    # print()
    print(p)
    # print()
