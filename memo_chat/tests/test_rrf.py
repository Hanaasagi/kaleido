import unittest

from memo_chat.models import Memory
from memo_chat.rrf import apply_type_weights, collect_mems, rrf_merge, sort_by_score


class TestRRF(unittest.TestCase):
    def test_rrf_merge_orders(self) -> None:
        a = Memory(id="a", content="x")
        b = Memory(id="b", content="y")
        c = Memory(id="c", content="z")
        fts = [a, b]
        vec = [b, c]
        scores = rrf_merge(fts, vec)
        self.assertGreater(scores["b"], scores["a"])
        self.assertGreater(scores["b"], scores["c"])

    def test_pinned_boost(self) -> None:
        mems = {
            "p": Memory(id="p", content="p", memory_type="pinned"),
            "i": Memory(id="i", content="i", memory_type="insight"),
        }
        scores = {"p": 1.0, "i": 1.0}
        apply_type_weights(mems, scores)
        self.assertEqual(scores["p"], 1.5)
        self.assertEqual(scores["i"], 1.0)

    def test_collect_and_sort(self) -> None:
        a = Memory(id="a", content="")
        b = Memory(id="b", content="")
        m = collect_mems([a], [b])
        scores = rrf_merge([a], [b])
        ordered = sort_by_score(m, scores)
        self.assertEqual(len(ordered), 2)


if __name__ == "__main__":
    unittest.main()
