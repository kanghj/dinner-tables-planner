from unittest import TestCase

import pytest

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
        self.assertCountEqual(new_table_sz, [1, 1, 1, 2])

        self.assertTrue(0 in coarse_to_original.keys())

        self.assertTrue(8 in coarse_to_original.keys())

        self.assertTrue(('in_table', 0, 0) in presolved_facts)
        self.assertTrue(('in_table', 8, 3) in presolved_facts)

    def test_coarse_local_simple(self):
        community = {
            0: [0, 1, 2],
            1: [3, 4, 5, 6, 7, 8],
            2: [9, 10, 11]
        }
        table_size = 3
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        # print(new_community)
        self.assertCountEqual(new_table_sz, [1, 1, 1, 1])

        self.assertTrue(0 in coarse_to_original.keys())

        self.assertTrue(9 in coarse_to_original.keys())

        self.assertTrue(('in_table', 0, 0) in presolved_facts)
        self.assertTrue(('in_table', 9, 3) in presolved_facts)


    def test_coarse_local_does_not_remove_multiple_connected_person(self):
        community = {
            0: [0, 1, 2],
            1: [3, 4, 5, 6, 7, 2],
            2: [9, 10, 2]
        }
        table_size = 3
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        self.assertCountEqual(new_table_sz, [2, 2, 2, 1])

        # that 2 is still present in each clique
        for key, values in new_community.items():
            self.assertTrue(2 in values)

        self.assertTrue(0 in coarse_to_original.keys())
        self.assertTrue(9 in coarse_to_original.keys())
        self.assertEqual(coarse_to_original[2], [2])

        self.assertTrue(('in_table', 0, 0) in presolved_facts)
        self.assertTrue(('in_table', 3, 1) in presolved_facts)
        self.assertTrue(('in_table', 6, 2) in presolved_facts)
        self.assertTrue(('in_table', 9, 3) in presolved_facts)

    def test_coarse_local_handles_single_person_in_node(self):
        community = {
            0: [0, 1, 2, 3]
        }
        table_size = 3
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        self.assertCountEqual(new_table_sz, [1, 3])

        self.assertTrue(0 in coarse_to_original.keys())
        self.assertTrue(3 in coarse_to_original.keys())
        self.assertEqual(coarse_to_original[3], [3])
        self.assertTrue(('in_table', 0, 0) in presolved_facts)

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
        self.assertCountEqual(new_table_sz, [3, 3])

        self.assertTrue(0 in coarse_to_original.keys())
        self.assertTrue(7 in coarse_to_original.keys())
        self.assertEqual(coarse_to_original[3], [3])
        self.assertTrue(('in_table', 0, 0) in presolved_facts)

    def test_coarse_local_handles_repeated_occurence_but_not_always(self):
        community = {
            0: [0, 1, 2, 3],
            1: [0, 1, 2, 4],
            3: [4, 7, 8, 9],
            4: [5, 7, 8, 9],
            5: [5, 6, 7, 8, 10]
        }
        table_size = 5
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        print(new_community)
        print(coarse_to_original)
        self.assertCountEqual(new_table_sz, [3, 4, 4])

        self.assertTrue(0 in coarse_to_original.keys())
        self.assertEquals([0, 1, 2], coarse_to_original[0])
        self.assertTrue(7 in coarse_to_original.keys())
        self.assertEquals([7, 8], coarse_to_original[7])
        self.assertEqual(coarse_to_original[3], [3])

        self.assertTrue(('in_table', 0, 0) in presolved_facts)
        self.assertTrue(('in_table', 4, 0) in presolved_facts)
        self.assertTrue(('in_table', 7, 1) in presolved_facts)