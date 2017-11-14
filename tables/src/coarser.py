import csv
import uuid
from collections import defaultdict
import subprocess
import os
import math
import re
import typing


def coarse_local(community: typing.Mapping[int, typing.List[int]], table_size : int):
    """
    Decrease the table_size, but combine subgraphs of cliques into single node
    Return the new table sizes, updated community, mapping of coarse_node back to original nodes
    """
    num_tables = math.ceil(sum((len(members) for key, members in community.items())) / table_size)

    # Here are what we will return
    new_table_sz = [table_size for i in range(num_tables)]
    new_community = defaultdict(list)
    coarse_to_original = {}

    single_clique_members = defaultdict(list)

    cliques_of_person = defaultdict(list)
    for clique_name, members in community.items():
        for member in members:
            cliques_of_person.append(clique_name)

    for person, cliques in cliques_of_person.items():
        if len(cliques) > 1:
            coarse_to_original[person] = [person]
            new_community[clique].append(person)
            continue
        clique = cliques[0]
        single_clique_members[clique].append(person)

    for clique, members in single_clique_members.items():
        clique_rep = min(members)
        coarse_to_original[clique_rep] = members
        new_community[clique].append(clique_rep)
        new_table_sz[clique - 1] -= len(members) - 1

    return (new_table_sz, new_community, coarse_to_original)



