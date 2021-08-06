import unittest
from merkle_tree import MerkleTree


class MerkelTreeTest(unittest.TestCase):

    def my_wrapper_test(self, responses):
        merkel_tree = MerkleTree()
        mtroot = merkel_tree.make_tree(responses)
        json_data = merkel_tree.get_proofs()
        del merkel_tree

        new_mtroot = MerkleTree().get_proofs(json_data, mtroot)

        self.assertTrue(mtroot == new_mtroot)

    def test_1(self):
        responses = list(map(lambda x: str(x), range(100, 0, -1)))
        self.my_wrapper_test(responses)

    def test_2(self):
        responses = list(map(lambda x: str(x), range(0, 100000)))
        self.my_wrapper_test(responses)

    def test_3(self):
        responses = list(map(lambda x: str(x), range(25345363, -3535, -43)))
        self.my_wrapper_test(responses)


if __name__ == "__main__":
    unittest.main()