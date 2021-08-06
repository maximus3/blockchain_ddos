import hashlib
import random
import json


def generate_numbers(to, rng, num=10):
    """
    Generate random num numbers from 0 to (to - 1)
    """
    to = min(to, num)

    return rng.sample(range(to), num)


class MerkleTree:
    def __init__(self):
        self.root = None
        self._tree_made = False
        self.leaf_count = 0
        self.levels = []
        self.rng = random.Random()

    @staticmethod
    def double_sha_256(s):
        return hashlib.sha256(hashlib.sha256(s.encode('utf-8')).hexdigest().encode('utf-8')).hexdigest()

    def make_tree(self, seq, is_hashes=False):
        if not is_hashes:
            self.leaf_count = len(seq)
            node_seq = []
            for el in seq:
                node_seq.append(el)
            self.levels.append(node_seq)
        else:
            node_seq = seq
        node_hashes = []
        if len(node_seq) % 2 != 0:
            node_seq.append(node_seq[-1])
        for i in range(0, len(node_seq), 2):
            el1, el2 = node_seq[i], node_seq[i + 1]
            node_hashes.append(self.double_sha_256(el1 + el2))  # TODO: in first el1 and el2 not hashes

        self.levels.append(node_hashes)
        if len(node_hashes) == 1:
            self.root = node_hashes.pop()
            self._tree_made = True
            self.set_rng_seed(self.root)
            return self.root
        return self.make_tree(node_hashes, is_hashes=True)

    def set_rng_seed(self, value):
        self.rng.seed(value)

    def get_stored(self, i, level, already_stored):
        if already_stored is not None:
            return already_stored.pop()
        return self.levels[level][i]

    def get_proofs(self, json_data=None, seed=None):
        if not self._tree_made and (json_data is None or seed is None):
            raise RuntimeError('Merkle tree not made')
        if self._tree_made and (json_data is not None or seed is not None):
            raise RuntimeError('Merkle tree is already made, run function without parameters or on another tree')
        already_stored = None
        if json_data is not None:
            leaf_count, already_responses, already_stored = json.loads(json_data)
        if json_data:
            self.leaf_count = leaf_count
            self.set_rng_seed(seed)
        numbers = generate_numbers(self.leaf_count, self.rng)  # TODO: num=?
        if json_data is None:
            responses = []
            stored = []

        current = {}
        for i, num in enumerate(numbers):
            if json_data is None:
                responses.append(self.levels[0][num])
                current[num] = self.levels[0][num]
            else:
                current[num] = already_responses[i]

        level = 0
        current_leaf_count = self.leaf_count
        while True:
            if current_leaf_count % 2 != 0:
                current_leaf_count += 1
            node_hashes = {}
            cur_i = -1
            for i in range(0, current_leaf_count, 2):
                cur_i += 1
                el1, el2 = None, None
                if i in current:
                    el1 = current[i]
                if i + 1 in current:
                    el2 = current[i + 1]
                if el1 is None and el2 is None:
                    continue
                if el1 is None:
                    value = self.get_stored(i, level, already_stored)
                    if json_data is None:
                        stored.append(value)
                    el1 = value
                if el2 is None:
                    value = self.get_stored(i + 1, level, already_stored)
                    if json_data is None:
                        stored.append(value)
                    el2 = value
                node_hashes[cur_i] = self.double_sha_256(el1 + el2)
            current_leaf_count //= 2
            if current_leaf_count == 1:
                if json_data is None:
                    return json.dumps((self.leaf_count, responses, stored[::-1]))
                return node_hashes[0]
            current = node_hashes
            level += 1



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
