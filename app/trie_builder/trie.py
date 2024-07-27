from typing import List, Dict, Tuple


class TrieNode:
    def __init__(self) -> None:
        self.children = {}
        self.eow = False
        self.word_frequency = 0

    def __eq__(self, other) -> bool:
        return (
            self.word_frequency == 0
            and other.word_frequency == 0
            and self.children == other.children
        )


class Trie:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating the instance")
            cls._instance = super().__new__(cls)
            cls._root = TrieNode()
        return cls._instance

    def __init__(self) -> None:
        pass

    def get_root(self) -> TrieNode:
        return self._root

    def insert(self, word: str, _count: int = 1) -> None:
        word = word.lower()
        if len(word) == 0:
            raise ValueError("Word is Empty")

        root = self._root

        for char in word:
            if char not in root.children:
                root.children[char] = TrieNode()
            root = root.children[char]

        root.eow = True
        root.word_frequency = root.word_frequency + _count

    def get_all_words(self, root: TrieNode, prefix: str) -> List[Dict[str, int] | None]:
        def get_words(root: TrieNode, prefix: str, curr_word: str):
            if root.eow:
                words.append({prefix + curr_word: root.word_frequency})
            for char, node in root.children.items():
                curr_word += char
                get_words(node, prefix, curr_word)
                curr_word = curr_word[:-1]

        words: List[Dict[str, int]] = []
        get_words(root, prefix, "")
        return words

    def compress_paths(self, node: TrieNode):
        if len(node.children) == 1 and not node.eow:
            char = next(iter(node.children))
            child = node.children[char]
            node.children.clear()
            node.children[char] = child
            self._compress_recursive(child)
        else:
            for child in node.children.values():
                self._compress_recursive(child)

    def compress(self):
        self.compress_paths()

    def serach(self, word: str) -> List[str | None]:
        word = word.lower()
        root = self.get_root()
        prefix: str = ""
        HEAD_ROOT = root
        for char in word:
            if char in root.children:
                prefix += char
                root = root.children[char]
            else:
                return []
        if HEAD_ROOT == root:
            return []

        words_list = self.get_all_words(root, prefix)
        words_dict: Dict[str, int] = {
            list(word_dict.keys())[0]: list(word_dict.values())[0]
            for word_dict in words_list
        }

        words_dict = dict(
            sorted(words_dict.items(), key=lambda items: items[1], reverse=True)
        )

        return list(words_dict.keys())


def initialize_trie() -> Tuple[Trie, TrieNode]:
    trie: Trie = Trie()

    return trie, trie.get_root()


# if __name__ == "__main__":
#     trie, root = initialize_trie()

#     test_words = ["UNITED", "UNIQUE", "UNIVERSAL", "UNIVERSITY"]

#     for word in test_words:
#         trie.insert(word)

#     print(trie.serach("univv"))
