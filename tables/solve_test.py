import uuid
from unittest import TestCase
from .solve import partition


class SolverTest(TestCase):
    def test_partition_simple(self):

        community = {
            0: [0, 5, 10],
            1: [1, 2, 3, 4, 6, 7],
            2: [8, 9]
        }
        persons = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        assert len(persons) == 11
        tables, persons = partition(community, str(uuid.uuid4()), persons, 3)

        resulting_groups = [values for values in tables.values()]
        print(resulting_groups)

        self.assertTrue([0, 5, 10] in resulting_groups)
        self.assertTrue([1, 2, 3] in resulting_groups)
        self.assertTrue([4, 6, 7] in resulting_groups)
        self.assertTrue([8, 9] in resulting_groups)

