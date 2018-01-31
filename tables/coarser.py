from collections import defaultdict
import math
import typing
import itertools


def pick_table_with_space(tables: typing.List[int], space_needed: int,
                          presolved_facts):
    for i, table in enumerate(tables):
        occupied_seats_at_table = len(
            [fact for fact in presolved_facts
             if fact[0] == 'in_table' and fact[2] == i])
        if table - occupied_seats_at_table >= space_needed:
            return i
        # if occupied_seats_at_table == 0:
        #     return i
    raise ValueError("no table found")


def coarse_local(community: typing.Mapping[int, typing.List[int]],
                 table_size: int,
                 clique_weights=None):
    """
    Coarses local communities of
        fully-connected persons connected to same cliques into nodes.
    Decrease the table_size.
    Return a tuple of 4 things:
      ( the new table sizes after combining/coarsening persons,
        updated community,
        mapping of coarse_node back to original persons, and
        prefined atoms assigning the nodes to tables with decreased sizes)
    """
    if clique_weights is None:
        clique_weights = defaultdict(lambda: 1)

    num_persons = len({member for members in community.values()
                       for member in members})

    # upper bound for num_tables
    # the true num tables is determined in asp
    num_tables = max(math.ceil(num_persons / table_size), len(community))

    new_table_sz = [table_size for i in range(0, num_tables)]
    new_community: typing.MutableMapping[int, typing.List[int]] \
        = defaultdict(list)
    node_to_persons = {}
    presolved_facts = []

    grouped_clique_members = defaultdict(list)
    members_cooccurence = defaultdict(lambda: defaultdict((lambda: 0)))

    cliques_of_person: typing.MutableMapping[int, typing.List[int]] = \
        defaultdict(list)
    coupled_persons_of_person = defaultdict(list)
    for clique_name, members in community.items():
        for member in members:
            cliques_of_person[member].append(clique_name)
        if clique_weights[clique_name] <= 0:
            # prevent persons with only zero or negative to be coarsened
            continue
        for member1, member2 in itertools.product(members, members):
            # if member1 != member2:
            members_cooccurence[member1][member2] += 1

    for member1, member2_and_count in members_cooccurence.items():
        for member2, count in member2_and_count.items():

            if count == len(cliques_of_person[member1]) and \
                    count == members_cooccurence[member2][member1] and \
                    count == len(cliques_of_person[member2]):

                coupled_persons_of_person[member1].append(member2)

    for person, cliques in cliques_of_person.items():
        if len(coupled_persons_of_person[person]) == 0:

            node_to_persons[person] = [person]

            for clique in cliques:
                new_community[clique].append(person)
            if clique_weights[clique_name] > 0:
                presolved_facts.append(
                    ('can_violate_isolation_rule', person,))
            # person cannot be combined with another to form a single node
            continue

        coupled_people = coupled_persons_of_person[person]
        chunks = [coupled_people[i:i + table_size]
                  for i in range(0, len(coupled_people), table_size)]
        for chunk in chunks:

            # test eligibility of `chunk`
            # a `chunk` is not eligible to be grouped into a single coarse node
            # if it causes only a single remaining member in the community
            is_eligible = True
            for clique in cliques:
                if len(community[clique]) - len(chunk) == 1:
                    is_eligible = False

            if not is_eligible:
                # on fail, update node_to_persons and new_community
                node_to_persons[person] = [person]

                for clique in cliques:
                    new_community[clique].append(person)
                if clique_weights[clique] > 0:
                    presolved_facts.append(
                        ('can_violate_isolation_rule', person,))

                continue

            for clique in cliques:
                if chunk in grouped_clique_members[clique]:
                    continue

                grouped_clique_members[clique].append(chunk)

    # clique_rep_already_in_table = {}
    for clique, groups in grouped_clique_members.items():
        for members in groups:

            clique_rep = min(members)
            node_to_persons[clique_rep] = members
            new_community[clique].append(clique_rep)

            if clique_weights[clique] > 0:
                presolved_facts.append(
                    ('can_violate_isolation_rule', clique_rep, ))
            # if clique_rep in clique_rep_already_in_table:
            #    already assigned this clique a table
            #    continue

            # if this clique belongs to only one community
            # can assign them a seat directly (in an empty table)
            # since they have no links
            # if len(cliques_of_person[clique_rep]) == 1:
            #     try:
            #         table_to_seat_clique = pick_table_with_space(
            #             new_table_sz, len(members), presolved_facts)
            #     except ValueError:
            #         # TODO unable to seat this clique, get a new table?
            #         new_table = len(new_table_sz)
            #         new_table_sz.append(table_size)
            #         table_to_seat_clique = new_table
            #
            #     new_table_sz[table_to_seat_clique] -= len(members) - 1
            #
            #     presolved_facts.append(
            #         ('in_table', clique_rep, table_to_seat_clique))
            #     clique_rep_already_in_table[clique_rep] =
            # table_to_seat_clique

    return new_table_sz, new_community, node_to_persons, presolved_facts
