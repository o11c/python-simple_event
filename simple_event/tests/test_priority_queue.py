import unittest

from simple_event.priority_queue import Entry, PriorityQueue

class TestEntry(unittest.TestCase):
    __slots__ = ('key', 'value')

    def test_lt(self):
        assert Entry(0, None) < Entry(1, None)
        assert not Entry(1, None) < Entry(1, None)
        assert not Entry(2, None) < Entry(1, None)

    def test_le(self):
        assert Entry(0, None) <= Entry(1, None)
        assert Entry(1, None) <= Entry(1, None)
        assert not Entry(2, None) <= Entry(1, None)

    def test_gt(self):
        assert not Entry(0, None) > Entry(1, None)
        assert not Entry(1, None) > Entry(1, None)
        assert Entry(2, None) > Entry(1, None)

    def test_ge(self):
        assert not Entry(0, None) >= Entry(1, None)
        assert Entry(1, None) >= Entry(1, None)
        assert Entry(2, None) >= Entry(1, None)

    def test_iter(self):
        k, v = Entry('k', 'v')
        assert k == 'k'
        assert v == 'v'

    def test_repr(self):
        assert repr(Entry(1, 2)) == 'Entry(1, 2)'

class TestPriorityQueue(unittest.TestCase):

    def test_bool(self):
        pq = PriorityQueue()
        assert not pq
        pq.push(1, 2)
        assert pq

    def test_push(self):
        pq = PriorityQueue()
        pq.push(1, 2)
        e = pq.peek()
        assert e.key == 1
        assert e.value == 2
        e2 = pq.pop()
        assert e is e2

    def test_pop(self):
        pq = PriorityQueue()
        self.assertRaises(IndexError, pq.peek)
        self.assertRaises(IndexError, pq.pop)

    def test_replace(self):
        pq = PriorityQueue()
        pq.push(1, 2)
        k, v = pq.replace(0, 1)
        assert k == 1 and v == 2
        pq.pop()
        with self.assertRaises(IndexError):
            pq.replace(0, 1)

    def test_has(self):
        pq = PriorityQueue()
        assert not pq.has(1)
        pq.push(1, None)
        assert not pq.has(0)
        assert pq.has(1)
        assert pq.has(2)

if __name__ == '__main__':
    unittest.main()
