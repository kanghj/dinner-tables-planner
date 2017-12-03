from collections import defaultdict
import math
import typing


def pick_table_with_space(tables: typing.List[int], space_needed: int,
                          presolved_facts):
    for i, table in enumerate(tables):
        occupied_seats_at_table = len(
            [fact for fact in presolved_facts if fact[0] == 'in_table' and fact[2] == i])
        if table - occupied_seats_at_table >= space_needed:
            return i
    raise ValueError("no table found")


def coarse_local(community: typing.Mapping[int, typing.List[int]],
                 table_size: int):
    """
    Coarses local communities of 
        fully-connected persons not connected to other cliques into nodes.
    Decrease the table_size.
    Return a tuple of 4 things:
      ( the new table sizes after combining/coarsening persons,
        updated community,
        mapping of coarse_node back to original persons, and
        prefined atoms assigning the nodes to tables with decreased sizes)
    """
    num_tables = math.ceil(sum(
        (len(members) for key, members in community.items())) / table_size)

    new_table_sz = [table_size for i in range(0, num_tables)]
    new_community: typing.MutableMapping[int, typing.List[int]] \
        = defaultdict(list)
    node_to_persons = {}
    presolved_facts = []

    single_clique_members: typing.MutableMapping[
        int, typing.List[typing.List[int]]] = defaultdict(list)

    cliques_of_person: typing.MutableMapping[int, typing.List[int]] = \
        defaultdict(list)
    for clique_name, members in community.items():
        for member in members:
            cliques_of_person[member].append(clique_name)

    for person, cliques in cliques_of_person.items():
        if len(cliques) > 1:
            node_to_persons[person] = [person]

            for clique in cliques:
                new_community[clique].append(person)
            # person cannot be combined with another to form a single node
            continue

        clique = cliques[0]

        num_nodes_in_clique = len(single_clique_members[clique])

        if num_nodes_in_clique == 0 or \
                len(single_clique_members[clique][num_nodes_in_clique - 1]) \
                == table_size:
            # create another node for this clique
            num_nodes_in_clique += 1
            single_clique_members[clique].append([])
            assert len(single_clique_members[clique]) == num_nodes_in_clique

        single_clique_members[clique][num_nodes_in_clique - 1].append(person)

    for clique, nodes in single_clique_members.items():
        for members in nodes:

            clique_rep = min(members)
            node_to_persons[clique_rep] = members
            new_community[clique].append(clique_rep)

            table_to_seat_clique = pick_table_with_space(
                new_table_sz, len(members), presolved_facts)
            new_table_sz[table_to_seat_clique] -= len(members) - 1
            presolved_facts.append(
                ('in_table', clique_rep, table_to_seat_clique))

    return new_table_sz, new_community, node_to_persons, presolved_facts
