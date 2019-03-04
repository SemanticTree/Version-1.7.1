# Compilation Functions --->

from .global_variables import *
from .token_manipulation import set_extentions, make_unique
from .vector_calculation import cosine_similarity
from .structural_calculation import term_distance, freq_sum
from . import global_variables as gv

def get_relation(token1, token2):
    output = [(token1, gv.DOC[i], token2) for i in range(token1.i, token2.i) if gv.DOC[i].pos_ == "VERB"]
    word_ranking=get_freq_sorted_dictionary()
    if not output:
        final_relation = (token1, 'has', token2)
    else:
        rank=[gv.WORD_RANKING[x] for (token1,x,token2) in output if x in gv.WORD_RANKING.keys()]
        if not rank:
            rels = [x[1] for x in output]
            rel2 = [x for x in rels if x.text not in ["is", "has", "have", "had", "was", "will"]]
            final_relation = (token1, rels[int(len(rels) / 2)].text, token2)
        else :
            max_rank=max(rank)
            final_relation= output[rank.index(max_rank)]
    return final_relation

# Text to Pairs funtion.


def make_pairs(processed_text):
    """
    Accepts processed_text and outputs pair list as tuples.
    """

    gv.DOC = gv.nlp(processed_text)
    gv.DOC = set_extentions(gv.DOC)
    gv.DOC = gv.DOC

    # 1. Make Sections - Based in new Lines
    index = [x.i for x in gv.DOC if "\n" in x.text]
    sections = [gv.DOC[i:j] for i, j in zip(index[:-1], index[1:])]

    # 2. Merge Sections
    logical_sections = []

    a = sections.pop(0)
    sec_start, sec_end = a.start, a.end
    while(sections):
        b = sections.pop(0)
        if a.similarity(b) > gv.SECTION_JOIN_THRESHHOLD:
            sec_end = b.end
        else:
            logical_sections.append((sec_start, sec_end))
            a = b
            sec_start, sec_end = a.start, a.end
    logical_sections.append((sec_start, sec_end))

    # 3. Identify Nodes
    Major, Minor = [], []
    for i, j in logical_sections:
        sec = gv.DOC[i:j]
        nodes = [ele for ele in sec if ele.pos_ in gv.NODE_TAGS]
        selected_nodes = make_unique(nodes)
        nodes = np.array(selected_nodes[:])
        pmc = len(nodes) if gv.PAIR_MAX_CONNECTIONS > len(nodes) else gv.PAIR_MAX_CONNECTIONS
        simi_matrix = np.array([[x.similarity(y) for y in nodes] for x in nodes])
        sorted_ranks = np.fliplr(simi_matrix.argsort(axis=1))
        pair_list = zip(nodes, nodes[sorted_ranks[:, 1:pmc]])
        pairs = np.array([(a, b) for a, ls in pair_list for b in ls])
        Major.extend(list(pairs))
        top_nodes = nodes[simi_matrix.sum(axis=1).argsort()][:5]
        Minor.extend(top_nodes)

    selected_nodes = make_unique(Minor)
    nodes = np.array(selected_nodes[:])
    pmc = len(nodes) if gv.PAIR_MAX_CONNECTIONS > len(nodes) else gv.PAIR_MAX_CONNECTIONS
    simi_matrix = np.array([[x.similarity(y) for y in nodes] for x in nodes])
    sorted_ranks = np.fliplr(simi_matrix.argsort(axis=1))
    pair_list = zip(nodes, nodes[sorted_ranks[:, 1:pmc]])
    pairs = np.array([(a, b) for a, ls in pair_list for b in ls])
    Major.extend(list(pairs))
    unique_pairs = list({''.join(sorted([p[0].text, p[1].text])): tuple(p) for p in Major}.values())

    print(f'Total Pairs             : {len(unique_pairs)}')

    return unique_pairs


# Assign values - Compilation Functin - Key Pipeline Function
def assign_values(edge_list, weight_matrix=None):
    """
    Returns edge and value pair : ((node1, node2), edge_weight)

    Keyword:
    concept_list -  a list of unique concepts objects with properties: vector, p_id, s_id, w_id
    weight_matrix - weights for the various attributes.
    """

    gathered_value = []

    for a, b in edge_list:
        cs = cosine_similarity(a.vector, b.vector)

        # Make a better fuction to get i values in future versions
        wd = term_distance(a, b)

        fs = freq_sum(a, b)
        arr = np.array([cs, wd, fs])
        gathered_value.append(arr)

    compiled = np.array(gathered_value)
    nrm = (compiled - compiled.min(axis=0)) / compiled.ptp(axis=0)

    w_mat = np.ones(3) / 3 if weight_matrix is None else weight_matrix
    w_normalised = nrm * w_mat

    total_nrm = w_normalised.sum(axis=1)

    pair = list(zip(edge_list, total_nrm))
    return pair
