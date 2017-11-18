from collections import defaultdict
import math
import typing


def pick_table_with_space(tables: typing.List[int], space_needed: int):
    for i, table in enumerate(tables):
        if table >= space_needed:
            return i
    return None


def coarse_local(community: typing.Mapping[int, typing.List[int]],
                 table_size: int):
    """
    Coarses a local community of fully-connected persons.
    Decrease the table_size, but combine subgraphs of cliques into single node
    Return the new table sizes, updated community,
     mapping of coarse_node back to original nodes, and
     prefined atoms assigning the coarse nodes to tables
    """
    num_tables = math.ceil(sum(
        (len(members) for key, members in community.items())) / table_size)

    # Here are what we will return
    new_table_sz = [table_size for i in range(0, num_tables)]
    new_community = defaultdict(list)
    coarse_to_original = {}
    presolved_facts = []

    single_clique_members = defaultdict(list)

    cliques_of_person = defaultdict(list)
    for clique_name, members in community.items():
        for member in members:
            cliques_of_person[member].append(clique_name)

    for person, cliques in cliques_of_person.items():
        clique = cliques[0]
        if len(cliques) > 1:
            coarse_to_original[person] = [person]
            new_community[clique].append(person)
            continue
        if len(single_clique_members[clique]) == table_size:
            # cannot add more to this clique already
            # TODO form a second representation node
            coarse_to_original[person] = [person]
            new_community[clique].append(person)
            continue
        single_clique_members[clique].append(person)

    for clique, members in single_clique_members.items():
        clique_rep = min(members)
        coarse_to_original[clique_rep] = members
        new_community[clique].append(clique_rep)

        table_to_seat_clique = pick_table_with_space(
            new_table_sz, len(members))
        new_table_sz[table_to_seat_clique] -= len(members) - 1
        presolved_facts.append('in_table({}, {}).'.format(
            clique_rep, table_to_seat_clique))

    return new_table_sz, new_community, coarse_to_original, presolved_facts
