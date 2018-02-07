from unittest import TestCase

from .main import merge_similar


class MergeTest(TestCase):

    def test_negative_example(self):
        test_communities = {
            'abc': set([1,2,3,4]),
            'def': set([5,6,7,8])
        }
        merged = merge_similar(test_communities, 0.75)
        print(merged)
        self.assertEqual(test_communities, merged)

        merged = merge_similar(test_communities, 0.1)
        self.assertEqual(test_communities, merged)

    def test_positive_example(self):
        test_communities = {
            'abc': set([1,2,3,4]),
            'def': set([4,5,6,7, 7])
        }
        merged = merge_similar(test_communities, 0.75)
        self.assertEqual(test_communities, merged)
        merged = merge_similar(test_communities, 0.25)
        print(merged)
        self.assertEqual({
            'abc': set([1, 2, 3, 4, 5 ,6 ,7])
        }, merged)
