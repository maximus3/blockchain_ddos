import hashlib
import random


def generate_numbers(to, rng, num=10):
    """
    Generate random num numbers from 0 to (to - 1)
    """
    to = min(to, num)

    return rng.sample(range(to), num)


class MerkleNode:
    def __init__(self, isHash, value, parent=None, next=None):
        self.isHash = isHash
        self.value = value
        self.parent = parent
        self.next = next

    def set_parent(self, parent):
        self.parent = parent

    def get_copy(self):
        return MerkleNode(self.isHash, self.value, self.parent, self.next)


class MerkleTree(object):
    def __init__(self):
        self.root = None
        self._tree_made = False
        self.leaf_count = 0
        self.levels = []
        self.rng = random.Random()

    @staticmethod
    def double_sha_256(s):
        return hashlib.sha256(hashlib.sha256(s).hexdigest()).hexdigest()

    def make_tree(self, seq, is_hashes=False):
        if not is_hashes:
            self.leaf_count = len(seq)
            node_seq = []
            for el in seq:
                node_seq.append(MerkleNode(False, el))
            self.levels.append(node_seq)
        else:
            node_seq = seq
        node_hashes = []
        if len(node_seq) % 2 != 0:
            node_seq.append(node_seq[-1].get_copy())
        for i in range(0, len(node_seq), 2):
            el1, el2 = node_seq[i], node_seq[i + 1]
            parent = MerkleNode(True, self.double_sha_256(el1.value + el2.value), next=[el1, el2])
            el1.set_parent(parent)
            el2.set_parent(parent)
            node_hashes.append(parent)

        self.levels.append(node_hashes)
        if len(node_hashes) == 1:
            self.root = node_hashes.pop()
            self._tree_made = True
            self.rng.seed(self.root.value)
            return self.root
        return self.make_tree(node_hashes, is_hashes=True)

    def get_proofs(self):
        if not self._tree_made:
            raise RuntimeError('Merkel tree not made')
        numbers = generate_numbers(self.leaf_count, self.rng)  # TODO: num=?
        # TODO: make tree and add to stored needed hashes

    @staticmethod
    def find_merkle_root(seq):
        hashes = []
        if len(seq) % 2 != 0:
            seq.append(seq[-1])

        for i in range(0, len(seq), 2):
            el1, el2 = seq[i], seq[i + 1]
            hashes.append(MerkleTree.double_sha_256(el1 + el2))

        if len(hashes) == 1:
            return hashes
        return MerkleTree.find_merkle_root(hashes)
