# Copyright © 2013, Ben Longbons <b.r.longbons@gmail.com>

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

''' A priority queue that knows about key-value pairs.
'''

import heapq

class Entry:
    __slots__ = ('key', 'value')
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __lt__(self, other):
        return self.key < other.key

    def __le__(self, other):
        return self.key <= other.key

    def __gt__(self, other):
        return self.key > other.key

    def __ge__(self, other):
        return self.key >= other.key

    def __eq__(self, other):
        assert False, "don't use this"

    def __ne__(self, other):
        assert False, "don't use this"

    def __iter__(self):
        yield self.key
        yield self.value

    def __repr__(self):
        return 'Entry(%r, %r)' % (self.key, self.value)

class PriorityQueue:
    __slots__ = ('_heap',)
    def __init__(self):
        self._heap = []

    def __bool__(self):
        return bool(self._heap)

    def push(self, key, value):
        heapq.heappush(self._heap, Entry(key, value))

    def peek(self):
        return self._heap[0]

    def pop(self):
        return heapq.heappop(self._heap)

    def replace(self, key, value):
        return heapq.heapreplace(self._heap, Entry(key, value))

    def has(self, key):
        return self and self.peek().key <= key
