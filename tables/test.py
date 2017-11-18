from unittest import TestCase
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

        self.assertTrue('in_table(0, 0).' in presolved_facts)
        self.assertTrue('in_table(8, 3).' in presolved_facts)

    def test_coarse_local_simple(self):
        community = {
            0: [0, 1, 2],
            1: [3, 4, 5, 6, 7, 8],
            2: [9, 10, 11]
        }
        table_size = 3
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        self.assertCountEqual(new_table_sz, [1, 1, 1, 1])

        self.assertTrue(0 in coarse_to_original.keys())

        self.assertTrue(9 in coarse_to_original.keys())

        self.assertTrue('in_table(0, 0).' in presolved_facts)
        self.assertTrue('in_table(9, 3).' in presolved_facts)

    def test_coarse_local_does_not_remove_multiple_connected_person(self):
        community = {
            0: [0, 1, 2],
            1: [3, 4, 5, 6, 7, 2],
            2: [9, 10, 2]
        }
        table_size = 3
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        self.assertCountEqual(new_table_sz, [1, 1, 2, 3])

        # that 2 is still present in each clique
        for key, values in new_community.items():
            self.assertTrue(2 in values)

        self.assertTrue(0 in coarse_to_original.keys())
        self.assertTrue(9 in coarse_to_original.keys())
        self.assertEqual(coarse_to_original[2], [2])

        self.assertTrue('in_table(0, 0).' in presolved_facts)
        self.assertTrue('in_table(3, 1).' in presolved_facts)
        self.assertTrue('in_table(6, 0).' in presolved_facts)
        self.assertTrue('in_table(9, 2).' in presolved_facts)
