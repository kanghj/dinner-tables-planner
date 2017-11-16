from unittest import TestCase
from .coarser import coarse_local


class CoarserTest(TestCase):
    def test_coarse_local(self):
        community = {
            0: [0, 5, 10],
            1: [1, 2, 3, 4, 6, 7],
            2: [8, 9]
        }
        table_size = 3
        new_table_sz, new_community, coarse_to_original, presolved_facts = \
            coarse_local(community, table_size)

        # this is actually sub-optimal
        # TODO implement multiple nodes for one community
        # there appears to be an additional seat since
        # 1 of the nodes only contains 2 persons
        self.assertCountEqual(new_table_sz, [1, 1, 2, 3])

        self.assertTrue(0 in coarse_to_original.keys())
        print(coarse_to_original.keys())
        self.assertTrue(8 in coarse_to_original.keys())

        self.assertTrue('in_table(0, 0).' in presolved_facts)
        self.assertTrue('in_table(8, 2).' in presolved_facts)
