from unittest import TestCase

import pytest
from collections import defaultdict

from .coarser import coarse_local


class CoarserTest(TestCase):

    def test_coarse_local_extra_seat(self):
        community = {
            0: [0, 5, 10],
            1: [1, 2, 3, 4, 6, 7],
            2: [8, 9]
        }
        table_size = 3
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        # there appears to be an additional seat since
        # 1 of the nodes only contains 2 persons

        self.assertTrue(0 in coarse_to_original.keys())

        self.assertTrue(8 in coarse_to_original.keys())

        self.assertEqual(community.keys(), new_community.keys(), 'communities don''t change')


    def test_coarse_local_simple(self):
        community = {
            0: [0, 1, 2],
            1: [3, 4, 5, 6, 7, 8],
            2: [9, 10, 11]
        }
        table_size = 3
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        self.assertTrue(0 in coarse_to_original.keys())

        self.assertTrue(9 in coarse_to_original.keys())
        self.assertEqual(community.keys(), new_community.keys(), 'communities don''t change')


    def test_coarse_local_does_not_remove_multiple_connected_person(self):
        community = {
            0: [0, 1, 2],
            1: [3, 4, 5, 6, 7, 2],
            2: [9, 10, 2]
        }
        table_size = 3
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        # that 2 is still present in each clique
        for key, values in new_community.items():
            self.assertTrue(2 in values)

        self.assertTrue(0 in coarse_to_original.keys())
        self.assertTrue(9 in coarse_to_original.keys())
        self.assertEqual(coarse_to_original[2], [2])

        self.assertEqual(community.keys(), new_community.keys(), 'communities don''t change')

    def test_coarse_local_handles_single_person_in_node(self):
        community = {
            0: [0, 1, 2, 3]
        }
        table_size = 3
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        self.assertTrue(0 in coarse_to_original.keys())
        self.assertTrue(3 in coarse_to_original.keys())
        self.assertEqual(coarse_to_original[3], [3])

        self.assertEqual(community.keys(), new_community.keys(), 'communities don''t change')

    def test_coarse_local_handles_nodes_connected_to_persons(self):
        community = {
            0: [0, 1, 2, 3],
            1: [0, 1, 2, 4],
            2: [0, 1, 2, 5],
            3: [4, 7, 8, 9],
            4: [5, 7, 8, 9],
            5: [6, 7, 8, 9]
        }
        table_size = 5
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        print(new_community)
        print(coarse_to_original)

        self.assertTrue(0 in coarse_to_original.keys())
        self.assertTrue(7 in coarse_to_original.keys())
        self.assertEqual(coarse_to_original[3], [3])

        self.assertEqual(community.keys(), new_community.keys(), 'communities don''t change')

    def test_coarse_local_handles_repeated_occurence_but_not_always(self):
        community = {
            0: [0, 1, 2, 3, 5],
            1: [0, 1, 2, 4, 5],
            3: [4, 7, 8, 9],
            4: [5, 7, 8, 9],
            5: [5, 6, 7, 8, 10]
        }
        table_size = 5
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        print(new_community)
        print(coarse_to_original)
        print(new_table_sz)
        print(presolved_facts)
        # self.assertCountEqual(new_table_sz, [4, 5, 5])

        self.assertTrue(0 in coarse_to_original.keys())
        self.assertEquals([0, 1, 2], coarse_to_original[0])
        self.assertTrue(7 in coarse_to_original.keys())
        self.assertEquals([7, 8], coarse_to_original[7])
        self.assertEqual(coarse_to_original[3], [3])

        self.assertEqual(community.keys(), new_community.keys(), 'communities don''t change')

        # self.assertTrue(('in_table', 3, 0) in presolved_facts)
        # TODO is this wrong?
        # self.assertTrue(('in_table', 6, 0) in presolved_facts)

    def test_coarse_break_up_clique_if_cannot_fit(self):
        community = {
            0: [0, 1, 2, 3],
            1: [2, 3, 4, 5]
            
        }
        table_size = 3
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        print(new_community)
        print(coarse_to_original)

        self.assertEquals([0, 1], coarse_to_original[0])
        self.assertEquals([2, 3], coarse_to_original[2])

        self.assertEqual(community.keys(), new_community.keys(), 'communities don''t change')

    def test_coarse_ignore_cliques_with_weight_eq_zero(self):
        community = {
            0: [0, 1, 2, 3],
            1: [2, 3, 4, 5]

        }
        table_size = 3
        clique_weights = {
            0: 1,
            1: 0
        }
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size, clique_weights)

        print(new_community)
        print(coarse_to_original)

        self.assertEquals([0, 1], coarse_to_original[0])
        self.assertEquals([2], coarse_to_original[2])
        self.assertEquals([3], coarse_to_original[3])
        self.assertEquals([4], coarse_to_original[4])

        self.assertEqual(community.keys(), new_community.keys(), 'communities don''t change')

    def test_coarse_ignore_cliques_with_weight_lt_zero(self):
        community = {
            0: [0, 1, 2, 3],
            1: [2, 3, 4, 5]

        }
        table_size = 3
        clique_weights = {
            0: 1,
            1: -1
        }
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size, clique_weights)

        print(new_community)
        print(coarse_to_original)

        self.assertEquals([0, 1], coarse_to_original[0])
        self.assertEquals([2], coarse_to_original[2])
        self.assertEquals([3], coarse_to_original[3])
        self.assertEquals([4], coarse_to_original[4])

        self.assertEqual(community.keys(), new_community.keys(), 'communities don''t change')

    def test_coarse_doesnt_leave_stray_member(self):
        community = {
            0: [0, 1, 2, 3],
            1: [2, 3, 4]

        }
        table_size = 3
        clique_weights = {
            0: 1,
            1: 1
        }
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size, clique_weights)

        print(new_community)
        print(coarse_to_original)

        self.assertEquals([0, 1], coarse_to_original[0])
        self.assertEquals([2], coarse_to_original[2])
        self.assertEquals([3], coarse_to_original[3])
        self.assertEquals([4], coarse_to_original[4])

        self.assertEqual(community.keys(), new_community.keys(), 'communities don''t change')

    def test_coarse_doesnt_add_one_member_to_multiple(self):
        community = {"2": [1, 2, 3, 4, 5, 6, 7, 1, 8, 9, 10], "3": [11],
                     "7": [7, 1, 12],
                     "8": [7, 1, 1, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
                     "9": [32, 33, 34, 35, 33, 36, 1, 37], "10": [38, 39, 40, 1, 41], "11": [7, 38, 39, 1, 1, 40, 42],
                     "12": [1, 1, 13, 15, 18, 19, 20, 22, 23, 24, 25, 28, 30, 43, 21, 44, 45, 24, 46, 13, 29, 47, 14, 48],
                     "13": [32, 34, 35, 33, 36, 1, 37, 16, 49, 50, 1, 33], "14": [33, 1, 51],
                     "15": [33, 36, 1, 1, 51, 52],
                     "16": [1, 1, 13, 15, 16, 17, 19, 22, 24, 44, 45, 24, 46, 13, 14, 48, 53, 54, 14, 55, 56, 45, 57, 17, 46],
                     "17": [7, 1, 28, 24, 46, 13, 14, 54, 56, 45, 57, 58, 59, 60, 57, 61, 62, 63, 48, 64, 65, 23, 66, 67, 46],
                     "18": [7, 17, 22, 23, 44, 24, 46, 48, 53, 45, 64]}
        table_size = 10
        clique_weights = defaultdict(lambda : 1)
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size, clique_weights)

        print(new_community)
        print(coarse_to_original)

        number_of_times_each_person_appears = defaultdict(lambda : 0)
        for node, members in coarse_to_original.items():
            for member in members:
                number_of_times_each_person_appears[member] += 1

        members_appearing_more_than_once = []
        members_appearing_less_then_once = []
        for member, count in number_of_times_each_person_appears.items():
            if count > 1:
                members_appearing_more_than_once.append(member)
            elif count < 1:
                members_appearing_less_then_once.append(member)
        self.assertEqual(len(members_appearing_more_than_once), 0)
        self.assertEqual(len(members_appearing_less_then_once), 0)